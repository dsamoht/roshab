"""
Flask app that wraps roshab-wf.nf Nextflow pipeline
"""
from glob import glob
import re
import os
from pathlib import Path
import subprocess
from typing import Optional
import webbrowser
from werkzeug.utils import secure_filename

from flask import Flask, render_template, request, flash
from flask_socketio import emit, SocketIO


class WorkflowSubprocess:

    def __init__(self, exp_config=None):
        self.process: Optional[subprocess.Popen] = None
        self.exp_config = exp_config

    def refresh_config(self, exp_config):
        self.exp_config = exp_config

    def start_subprocess(self):
        
        logger_file = Path(".nextflow.log")
        try:
            logger_file.resolve(strict=True)
            logger_file.unlink()
        except FileNotFoundError:
            pass

        try:
            self.process = subprocess.Popen(["nextflow", "run", "main.nf",
                                        "--exp", self.exp_config["exp_id"],
                                        "--output", self.exp_config['output_dir'],
                                        "--reads", "/".join(app.config['UPLOAD_FOLDER'].split("/")[0:-1])],
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
app.config["UPLOAD_FOLDER"] = os.path.abspath("uploads/fastq_pass")
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
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
    "uploaded_files": [],
    "n_barcodes": 0,
    "docker_status": False,
    "pipeline_finished": False
}

def get_docker_status():
    try:
        subprocess.check_output("docker info", shell=True)
        EXP_CONFIG["docker_status"] = True
    except subprocess.CalledProcessError:
        EXP_CONFIG["docker_status"] = False

get_docker_status()
workflow_subprocess = WorkflowSubprocess(EXP_CONFIG)

def input_validation(name):
    for char in name:
        if char in [r"?", "\\", r"/", r".", r",", r":", r";"]:
            return False
    return True

def allowed_file(filename):
    return "." in filename and any(ext in filename for ext in ALLOWED_EXTENSIONS)

@app.route('/')
def index():
    workflow_subprocess.refresh_config(EXP_CONFIG)
    return render_template("index.html", exp_config=EXP_CONFIG)

@app.route("/get_run_info_base", methods=["GET", "POST"])
def get_run_info_base():
    if request.method == "POST":
        exp_id = str(request.form.get("exp-id"))
        output_name = str(request.form.get("output-name"))
        if not input_validation(exp_id) or not input_validation(output_name):
            exp_id = ""
            output_name = ""
            txt_message = "Configuration invalide: contient des charactères spéciaux.\n".split("\n")
            flash(txt_message[:-1], "error")
        else:
            conf_saved_msg = "Configuration sauvegardée.\n" \
            f"Identifiant : {exp_id} \n" \
            f"Dossier de sortie : {output_name} \n"
            txt_conf_saved = conf_saved_msg.split("\n")
            flash(txt_conf_saved[:-1], "success")
        EXP_CONFIG["exp_id"] = exp_id
        EXP_CONFIG["output_dir"] = output_name
    return render_template("index.html", exp_config=EXP_CONFIG)

@app.route("/refresh_config", methods=["GET", "POST"])
def refresh_config():
    EXP_CONFIG["exp_id"] = ""
    EXP_CONFIG["output_dir"] = ""
    txt_message = "Configuration précédente effacée.\n".split("\n")
    flash(txt_message[:-1], "success")
    return render_template("index.html", exp_config=EXP_CONFIG)

@app.route("/open_results", methods=["GET", "POST"])
def open_results(*args, **kwargs):
    try:
        multiqc_path = glob(f'{EXP_CONFIG["output_dir"]}/multiqc/*.html')[-1]
        multiqc_abs_path = os.path.abspath(multiqc_path)
        webbrowser.open(f'file://{multiqc_abs_path}', new=2)
    except (FileNotFoundError, IndexError):
        txt_message = "Ouverture impossible du fichier de résultats.\n".split("\n")
        flash(txt_message[:-1], "error")

    return render_template("index.html", exp_config=EXP_CONFIG)

@app.route("/upload_directory", methods=["POST"])
def upload_directory():
    if "files[]" not in request.files:
        txt_message = "Aucun fichier trouvé.\n".split("\n")
        flash(txt_message[:-1], "error")
        return render_template("index.html", exp_config=EXP_CONFIG)

    files = request.files.getlist("files[]")
    EXP_CONFIG["uploaded_files"] = []

    upload_path = app.config["UPLOAD_FOLDER"]

    for file in files:
        if not file.filename:
            continue
        if file.filename.startswith(r".") or r"/." in file.filename:
            continue
        if not allowed_file(file.filename):
            continue

        filename = secure_filename(os.path.basename(file.filename))
        file_path = os.path.join(upload_path, filename)
        file.save(file_path)
        EXP_CONFIG["uploaded_files"].append(filename)

    if EXP_CONFIG["uploaded_files"]:

        _file_dict = {}
        barcode_pattern = re.compile(r'barcode\d{2}')
        exp_id = EXP_CONFIG["exp_id"]

        for file in EXP_CONFIG["uploaded_files"]:
            match = barcode_pattern.search(file)
            if match:
                barcode_key = exp_id + "_" + match.group(0)
                if barcode_key not in _file_dict:
                    _file_dict[barcode_key] = []
                    EXP_CONFIG["n_barcodes"] += 1
                _file_dict[barcode_key].append(file)
            else:
                if exp_id not in _file_dict:
                    _file_dict[exp_id] = []
                _file_dict[exp_id].append(file)

        n_files = len(EXP_CONFIG["uploaded_files"])
        txt_message = f"""{n_files} fichier{"s" if n_files > 1 else ""} chargé{"s" if n_files > 1 else ""}.\n""" \
            f"""{EXP_CONFIG['n_barcodes']} "barcode{"s" if EXP_CONFIG['n_barcodes'] > 1 else ""}" trouvé{"s" if EXP_CONFIG['n_barcodes'] > 1 else ""}.\n""".split("\n")
        flash(txt_message[:-1], 'success')

    else:
        txt_message = "Aucun fichier trouvé.\n".split("\n")
        flash(txt_message[:-1], "error")

    EXP_CONFIG["input_dir"] = upload_path
    return render_template("index.html", exp_config=EXP_CONFIG)


def get_initial_processes_names(log_file):
    processes = set()
    parsing_not_finished = True
    while parsing_not_finished:
        try:
            with open(log_file, "r") as logger:
                for line in logger:
                    if "Starting process" in line:
                        processes.add(line.split()[-1].strip())
                    elif "Submitted process" in line:
                        parsing_not_finished = False
        except FileNotFoundError:
            continue
    return processes

@socketio.on("run_workflow")
def run_workflow(*args, **kwargs):

    workflow_subprocess.start_subprocess()
    processes = get_initial_processes_names(".nextflow.log")
    progression_map = dict.fromkeys(processes, False)
    current_processes = dict.fromkeys(processes, False)

    emit('logging', {'log': f"0/{len(progression_map)} terminé(s) (Mise en place des conteneurs...)"})
    while True:
        try:
            if workflow_subprocess.process.poll() is not None:
                break
            try:
                with open(".nextflow.log", "r") as logger:
                    for line in logger:
                        if "status: COMPLETED; exit: 0; error: -;" in line:
                            for software in progression_map:
                                if software in line:
                                    progression_map[software] = True
                        elif "Submitted process" in line:
                            for software in progression_map:
                                if software in line:
                                    current_processes[software] = True

                progress = round(sum(progression_map.values())/len(progression_map)*100)
                finished_processes = [soft for soft, status in progression_map.items() if status]
                current_processes_live = [soft for soft, status in current_processes.items() if (status and soft not in finished_processes)]
                log_message = f"{len(finished_processes)}/{len(progression_map)} terminé(s): [{', '.join(finished_processes)}] "
                log_message += f"En cours: [{', '.join(current_processes_live)}]"
                emit('progress', {'progress': progress})
                emit('logging', {'log': log_message})

            except FileNotFoundError:
                return render_template('index.html', exp_config=EXP_CONFIG)
        except AttributeError:
            return render_template('index.html', exp_config=EXP_CONFIG)

    EXP_CONFIG["pipeline_finished"] = True
    emit('finish', {'finished': True})

    return render_template('index.html', exp_config=EXP_CONFIG)

@socketio.on("cancel_workflow")
def cancel_workflow(*args, **kwargs):
    workflow_subprocess.kill_subprocess()


if __name__ == "__main__":
    app.run(debug=True)
