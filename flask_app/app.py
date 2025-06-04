"""
Flask app that wraps `roshab` Nextflow pipeline
"""
import subprocess
from typing import Optional
from werkzeug.utils import secure_filename
import os
import pandas as pd

from flask import Flask, render_template, request, flash
from flask_socketio import emit, SocketIO


REQUIRED_COLUMNS = ["sample_name", "date", "site", "group", "reads"]
IMPORT_FOLDER = os.path.join(os.path.dirname(__file__), 'imports')

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
            print(f"Failed to start WorkflowSubprocess: {err}")
            self.process = None

    def kill_subprocess(self):
        self.process.kill()
        self.process = None

app = Flask(__name__)
app.config["SECRET_KEY"] = '00000000'
socketio = SocketIO(app)

ALLOWED_EXTENSIONS = {"fastq",
                      "fastq.gz",
                      "fasta",
                      "fasta.gz",
                      "fq", 
                      "fq.gz"}

EXP_CONFIG = {
    "exp_id": "",
    "output_dir": "",
    "samplesheet": "",
    "filename": "",
    "n_samples": 0,
    "skip_qc": "not_set",
    "docker_status": False,
    "pipeline_finished": False
}

WF_SUBPROCESS = WorkflowSubprocess()

def get_docker_status():
    try:
        subprocess.check_output("docker info", shell=True)
        EXP_CONFIG["docker_status"] = True
    except subprocess.CalledProcessError:
        EXP_CONFIG["docker_status"] = False

get_docker_status()

def input_validation(name):
    for char in name:
        if char in [r"?", "\\", r"/", r".", r",", r":", r";"]:
            return False
    return True

def allowed_file(filename):
    return "." in filename and any(ext in filename for ext in ALLOWED_EXTENSIONS)

@app.route('/')
def index():
    WF_SUBPROCESS.refresh_config(EXP_CONFIG)
    return render_template("index.html", exp_config=EXP_CONFIG)

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
        EXP_CONFIG["exp_id"] = exp_id
        EXP_CONFIG["output_dir"] = output_name
        EXP_CONFIG["skip_qc"] = skip_qc
    
    return render_template("index.html", exp_config=EXP_CONFIG)

@app.route("/refresh_config", methods=["GET", "POST"])
def refresh_config():
    EXP_CONFIG["exp_id"] = ""
    EXP_CONFIG["output_dir"] = ""
    EXP_CONFIG["skip_qc"] = "not_set"
    txt_message = "Configuration précédente effacée.\n".split("\n")
    flash(txt_message[:-1], "success")
    return render_template("index.html", exp_config=EXP_CONFIG)

@app.route("/upload_samplesheet", methods=["POST"])
def upload_samplesheet():

    os.makedirs(IMPORT_FOLDER, exist_ok=True)
    if "file" not in request.files:
        txt_message = "Aucun fichier trouvé.\n".split("\n")
        flash(txt_message[:-1], "error")
        return render_template("index.html", exp_config=EXP_CONFIG)

    file = request.files["file"]
    if file.filename == "":
        flash(["Aucun fichier sélectionné."], "error")
        return render_template("index.html", exp_config=EXP_CONFIG)

    filename = secure_filename(file.filename)
    file_path = os.path.join(IMPORT_FOLDER, filename)
    
    file.save(file_path)
    EXP_CONFIG["samplesheet"] = file_path

    try:
        df = pd.read_csv(file_path)
        if list(df.columns) != REQUIRED_COLUMNS:
            flash([f"Les colonnes du fichier doivent être exactement: {', '.join(REQUIRED_COLUMNS)}"], "error")
            EXP_CONFIG["samplesheet"] = ""
            return render_template("index.html", exp_config=EXP_CONFIG)
        if df.duplicated().any():
            flash(["Le fichier contient des lignes dupliquées."], "error")
            EXP_CONFIG["samplesheet"] = ""
            return render_template("index.html", exp_config=EXP_CONFIG)

        file_path = os.path.join(IMPORT_FOLDER, filename)
        EXP_CONFIG["n_samples"] = len(df)
        EXP_CONFIG["filename"] = filename
        df.to_csv(file_path, index=False)
        EXP_CONFIG["samplesheet"] = file_path
        flash(["Fichier téléchargé avec succès."], "success")

    except Exception as e:
        EXP_CONFIG["samplesheet"] = ""
        flash([f"Erreur lors du traitement du fichier : {str(e)}"], "error")

    return render_template("index.html", exp_config=EXP_CONFIG)

   
@socketio.on("run_workflow")
def run_workflow(*args, **kwargs):

    WF_SUBPROCESS.start_subprocess(EXP_CONFIG)

    if not WF_SUBPROCESS.process:
        emit('workflow_output', {'data': '[Erreur] Impossible de démarrer le processus.'})
        return

    for line in iter(WF_SUBPROCESS.process.stdout):
        if line:
            try:
                emit('workflow_output', {'data': line})
            except Exception as e:
                emit('workflow_output', {'data': f'[Erreur d\'émission] {str(e)}'})

    EXP_CONFIG["pipeline_finished"] = True
    emit('finish', {'finished': True})

    return render_template('index.html', exp_config=EXP_CONFIG)

@socketio.on("cancel_workflow")
def cancel_workflow(*args, **kwargs):
    WF_SUBPROCESS.kill_subprocess()
    EXP_CONFIG = {
    "exp_id": "",
    "output_dir": "",
    "samplesheet": "",
    "filename": "",
    "n_samples": 0,
    "skip_qc": "not_set",
    "docker_status": "false",
    "pipeline_finished": False
    }
    get_docker_status()
    WF_SUBPROCESS.refresh_config(EXP_CONFIG)
    return render_template("index.html", exp_config=EXP_CONFIG)


if __name__ == "__main__":
    app.run(debug=True)
