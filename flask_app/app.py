"""
Flask app that wraps `roshab` pipeline
"""
import subprocess
from typing import Optional
from werkzeug.utils import secure_filename
import os
import pandas as pd

from flask import Flask, redirect, render_template, request, flash, url_for
from flask_socketio import emit, SocketIO


REQUIRED_COLUMNS = [
    "sample_name",
    "date",
    "site",
    "group",
    "reads"
]
ALLOWED_EXTENSIONS = {
    "fastq",
    "fastq.gz",
    "fq", 
    "fq.gz"
}


app = Flask(__name__)
app.config["SECRET_KEY"] = '00000000'
socketio = SocketIO(app)

IMPORT_FOLDER = os.path.join(os.path.dirname(__file__), 'imports')


class ExpConfig:
    def __init__(self):
        self._config = {
            "exp_id": "",
            "output_dir": "",
            "samplesheet": "",
            "filename": "",
            "n_samples": 0,
            "skip_qc": "not_set",
            "docker_status": False,
            "pipeline_finished": False
        }
        self.update_docker_status()

    def get(self, key):
        return self._config.get(key)

    def set(self, key, value):
        self._config[key] = value

    def update(self, **kwargs):
        self._config.update(kwargs)

    def as_dict(self):
        return self._config

    def reset(self, keep_uploaded=False):
        filename = self._config["filename"]
        samplesheet = self._config["samplesheet"]
        n_samples = self._config["n_samples"]
        self.__init__()
        if keep_uploaded:
            self._config.update({
                "filename": filename,
                "samplesheet": samplesheet,
                "n_samples": n_samples
            })

    def update_docker_status(self):
        try:
            subprocess.check_output("docker info", shell=True)
            self._config["docker_status"] = True
        except subprocess.CalledProcessError:
            self._config["docker_status"] = False

    def is_ready_for_run(self):
        return all([
            self._config["exp_id"],
            self._config["output_dir"],
            self._config["samplesheet"],
            self._config["docker_status"]
        ])

    def delete_uploaded_file(self):
        if self._config["samplesheet"] and os.path.exists(self._config["samplesheet"]):
            os.remove(self._config["samplesheet"])
            self._config["samplesheet"] = ""
            self._config["filename"] = ""
            self._config["n_samples"] = 0


class WorkflowSubprocess:

    def __init__(self):
        self.process: Optional[subprocess.Popen] = None
        self.skip_qc = False
        self.exp_config = {}

    def refresh_config(self, exp_config):
        self.exp_config = exp_config

    def start_subprocess(self, exp_config):
        exp_config = exp_config
        if exp_config['skip_qc'] == True:
            skip_qc = "--skip_qc"
        else:
            skip_qc = ""
        try:
            self.process = subprocess.Popen(["nextflow", "run", "main.nf",
                                        skip_qc,
                                        "--exp", exp_config["exp_id"],
                                        "--output", exp_config['output_dir'],
                                        "--input", exp_config['samplesheet']],
                                        universal_newlines=True,
                                        shell=False,
                                        stdout=subprocess.PIPE,
                                        stderr=subprocess.STDOUT)
        except Exception as err:
            emit('workflow_output', {'data': f'{err}'})
            self.process = None

    def kill_subprocess(self):
        self.process.kill()
        self.process = None


WF_SUBPROCESS = WorkflowSubprocess()
EXP_CONFIG = ExpConfig()


def input_validation(name):
    for char in name:
        if char in [r"?", "\\", r"/", r".", r",", r":", r";", r" "]:
            return False
    return True

def allowed_file(filename):
    return "." in filename and any(ext in filename for ext in ALLOWED_EXTENSIONS)

@app.route('/')
def index():
    WF_SUBPROCESS.refresh_config(EXP_CONFIG.as_dict())
    return render_template("index.html", exp_config=EXP_CONFIG.as_dict())

@app.route("/reset_all", methods=["GET"])
def reset_all():
    EXP_CONFIG.delete_uploaded_file()
    EXP_CONFIG.reset()
    WF_SUBPROCESS.refresh_config(EXP_CONFIG.as_dict())
    return redirect(url_for("index"))

@app.route("/remove_samplesheet", methods=["POST"])
def remove_samplesheet():
    EXP_CONFIG.delete_uploaded_file()
    flash(["Fichier supprimé."], "success")
    return redirect(url_for("index"))

@app.route("/get_run_info_base", methods=["GET", "POST"])
def get_run_info_base():
    if request.method == "POST":
        exp_id = str(request.form.get("exp-id"))
        output_name = str(request.form.get("output-name"))
        skip_qc = request.form.get("skip_qc") == "on"
        if not input_validation(exp_id) or not input_validation(output_name):
            exp_id = ""
            output_name = ""
            txt_message = "Configuration invalide: contient des charactères spéciaux.\n".split("\n")
            flash(txt_message[:-1], "error")
        else:
            conf_saved_msg = "Configuration sauvegardée.\n" \
            f"Identifiant : {exp_id} \n" \
            f"Dossier de sortie : {output_name} \n" \
            f"Protocole rapide : {'Oui' if skip_qc else 'Non'} \n"
            txt_conf_saved = conf_saved_msg.split("\n")
            flash(txt_conf_saved[:-1], "success")
        EXP_CONFIG.update(exp_id=exp_id, output_dir=output_name, skip_qc=skip_qc)
    
    return render_template("index.html", exp_config=EXP_CONFIG.as_dict())

@app.route("/refresh_config", methods=["GET", "POST"])
def refresh_config():
    EXP_CONFIG.reset(keep_uploaded=True)
    txt_message = "Configuration précédente effacée.\n".split("\n")
    flash(txt_message[:-1], "success")
    return render_template("index.html", exp_config=EXP_CONFIG.as_dict())

@app.route("/upload_samplesheet", methods=["POST"])
def upload_samplesheet():

    os.makedirs(IMPORT_FOLDER, exist_ok=True)
    if "file" not in request.files or request.files["file"].filename == "":
        flash(["Aucun fichier sélectionné."], "error")
        return redirect(url_for("index"))

    file = request.files["file"]
    filename = secure_filename(file.filename)
    file_path = os.path.join(IMPORT_FOLDER, filename)
    file.save(file_path)

    try:
        df = pd.read_csv(file_path)
        if list(df.columns) != REQUIRED_COLUMNS:
            flash([f"Les colonnes du fichier doivent être exactement: {', '.join(REQUIRED_COLUMNS)}"], "error")
            return render_template("index.html", exp_config=EXP_CONFIG.as_dict())
        if df.duplicated().any():
            flash(["Le fichier contient des lignes dupliquées."], "error")
            return render_template("index.html", exp_config=EXP_CONFIG.as_dict())

        df.to_csv(file_path, index=False)
        EXP_CONFIG.update(samplesheet=file_path, filename=filename, n_samples=len(df))
        flash(["Fichier téléchargé avec succès."], "success")

    except Exception as e:
        flash([f"Erreur lors du traitement du fichier : {str(e)}"], "error")

    return redirect(url_for("index"))

   
@socketio.on("run_workflow")
def run_workflow(*args, **kwargs):
    if not EXP_CONFIG.is_ready_for_run():
        emit('workflow_output', {'data': '[Erreur] Configuration incomplète.'})
        return
    WF_SUBPROCESS.start_subprocess(EXP_CONFIG.as_dict())

    if not WF_SUBPROCESS.process:
        emit('workflow_output', {'data': '[Erreur] Impossible de démarrer le processus.'})
        return

    for line in iter(WF_SUBPROCESS.process.stdout):
        if line:
            try:
                emit('workflow_output', {'data': line})
            except Exception as e:
                emit('workflow_output', {'data': f'[Erreur d\'émission] {str(e)}'})

    EXP_CONFIG.set("pipeline_finished", True)
    emit('finish', {'finished': True})

    return render_template('index.html', exp_config=EXP_CONFIG)

@socketio.on("cancel_workflow")
def cancel_workflow(*args, **kwargs):
    emit("redirect_after_cancel", {"url": url_for("reset_all")})

if __name__ == "__main__":
    socketio.run(app, debug=True)
