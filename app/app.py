"""
Flask app that wraps `roshab` pipeline
"""
from collections import defaultdict
import os
import re
import subprocess
from typing import Optional
import uuid

from flask import Flask, redirect, render_template, request, flash, url_for
from flask_socketio import emit, SocketIO
import pandas as pd


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
app.config["SECRET_KEY"] = uuid.uuid4().hex
socketio = SocketIO(app)

IMPORT_FOLDER = os.getenv("INPUT_DIR")

class ExpConfig:
    def __init__(self):
        self._config = {
            "exp_id": "",
            "samplesheet": "",
            "n_samples": 0,
            "skip_qc": "not_set",
            "pipeline_finished": False
        }

    def get(self, key):
        return self._config.get(key)

    def set(self, key, value):
        self._config[key] = value

    def update(self, **kwargs):
        self._config.update(kwargs)

    def as_dict(self):
        return self._config

    def reset(self):
        self.__init__()

    def is_ready_for_run(self):
        return all([
            self._config["exp_id"],
            self._config["samplesheet"]
        ])

    def delete_uploaded_file(self):
        if self._config["samplesheet"] and os.path.exists(self._config["samplesheet"]):
            os.remove(self._config["samplesheet"])
            self._config["samplesheet"] = ""
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
                                        "--output", f"{IMPORT_FOLDER.rstrip(r'/')}/{exp_config['exp_id']}",
                                        "--input", exp_config['samplesheet'],
                                        "-w", f"{IMPORT_FOLDER.rstrip(r'/')}/work"],
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


# Global instances
SAMPLES = []
WF_SUBPROCESS = WorkflowSubprocess()
EXP_CONFIG = ExpConfig()


def longest_common_prefix(strings):
    if not strings:
        return ""
    prefix = os.path.commonprefix(strings)
    return prefix

def input_validation(name):
    for char in name:
        if char in [r"?", "\\", r"/", r".", r",", r":", r";", r" "]:
            return False
    return True

def allowed_file(filename):
    return "." in filename and any(ext in filename for ext in ALLOWED_EXTENSIONS)

def convert_realpaths_to_wildcards(paths):
    """
    Convert a list of file paths into a single wildcard pattern.
    If only one file, return it directly.
    """
    if len(paths) == 1:
        return paths[0]

    dirs = [os.path.dirname(p) for p in paths]
    basenames = [os.path.basename(p) for p in paths]

    if len(set(dirs)) > 1:
        # fallback: cannot wildcard across directories, join with comma
        return ",".join(paths)

    dir_prefix = dirs[0]

    # Find common prefix
    common_prefix = os.path.commonprefix(basenames)

    # Find common suffix
    reversed_basenames = [b[::-1] for b in basenames]
    common_suffix_reversed = os.path.commonprefix(reversed_basenames)
    common_suffix = common_suffix_reversed[::-1]

    # Construct wildcard for variable middle part
    wildcard = common_prefix + "*" + common_suffix
    return os.path.join(dir_prefix, wildcard)


@app.route('/')
def index():
    WF_SUBPROCESS.refresh_config(EXP_CONFIG.as_dict())
    return render_template("index.html", exp_config=EXP_CONFIG.as_dict(), table_rows=SAMPLES)

@app.route("/refresh_sample_sheet")
def refresh_sample_sheet():
    samples_dict = detect_samples()
    SAMPLES.clear()
    for sample_name, paths in samples_dict.items():
        SAMPLES.append({
            "sample_name": sample_name,
            "date": "",
            "site": "",
            "group": "",
            "reads": paths
        })
    flash(f"{len(SAMPLES)} échantillon(s) détecté(s) dans le dossier.\n".split("\n")[:-1], "success")
    return redirect(url_for("index"))

@app.route("/reset_all")
def reset_all():
    EXP_CONFIG.delete_uploaded_file()
    EXP_CONFIG.reset()
    WF_SUBPROCESS.refresh_config(EXP_CONFIG.as_dict())
    SAMPLES.clear()
    return redirect(url_for("index"))

@app.route("/remove_samplesheet", methods=["POST"])
def remove_samplesheet():
    EXP_CONFIG.delete_uploaded_file()
    flash(["Fichier d'entrée supprimé."], "success")
    return redirect(url_for("index"))

@app.route("/get_run_info_base", methods=["POST"])
def get_run_info_base():
    if request.method == "POST":
        exp_id = str(request.form.get("exp-id"))
        skip_qc = request.form.get("skip_qc") == "on"
        if not input_validation(exp_id):
            skip_qc = "not_set"
            exp_id = ""
            txt_message = "Configuration invalide: contient des charactères spéciaux.\n".split("\n")
            flash(txt_message[:-1], "error")
        else:
            conf_saved_msg = "Configuration sauvegardée.\n" \
            f"Identifiant : {exp_id} \n" \
            f"Protocole rapide : {'Oui' if skip_qc else 'Non'} \n"
            txt_conf_saved = conf_saved_msg.split("\n")
            flash(txt_conf_saved[:-1], "success")
        EXP_CONFIG.update(exp_id=exp_id, skip_qc=skip_qc)
    return redirect(url_for("index"))

@app.route("/refresh_config", methods=["POST"])
def refresh_config():
    EXP_CONFIG.reset(keep_uploaded=True)
    txt_message = "Configuration précédente effacée.\n".split("\n")
    flash(txt_message[:-1], "success")
    return redirect(url_for("index"))

@app.route("/detect_samples", methods=["GET"])
def detect_samples():
    """
    Recursively detect single-end FASTQ(.gz) files and group them by sample name.
    Handles split FASTQ files like sample_1.fastq.gz, ..., sample_38.fastq.gz.

    Returns:
        dict: {sample_name: [list of file paths]}
    """
    fastq_pattern = re.compile(r'\.f(ast)?q(\.gz)?$', re.IGNORECASE)

    # Patterns for obvious technical split suffixes
    split_patterns = [
        re.compile(r'(_part\d+)$', re.IGNORECASE),
        re.compile(r'(_run\d+)$', re.IGNORECASE),
        re.compile(r'(_rep\d+)$', re.IGNORECASE),
        re.compile(r'(_bf[a-z0-9]+_[a-z0-9]+_\d+)$', re.IGNORECASE),  # Nanopore-like
        re.compile(r'(_[Rr]?[12])$'),  # Illumina _R1/_R2 etc.
        re.compile(r'(?<=\D)_(\d+)$'),  # trailing _1, _2 after non-digit prefix only (meaning sample name contains replicate-like numbers)
    ]

    samples = defaultdict(list)

    for root, _, files in os.walk(IMPORT_FOLDER):
        for f in files:
            if not fastq_pattern.search(f):
                continue
            basename = re.sub(fastq_pattern, '', f)
            cleaned = basename
            # Apply all split suffix cleanups
            for pat in split_patterns:
                cleaned = pat.sub('', cleaned)
            # Remove any leftover trailing dots/underscores/hyphens
            cleaned = re.sub(r'[\.\-_]+$', '', cleaned)
            full_path = os.path.join(root, f)
            samples[cleaned].append(full_path)
    
    for s, paths in samples.items():
        paths.sort()
        samples[s] = convert_realpaths_to_wildcards(paths)
    return samples

@app.route("/update_samples", methods=["POST"])
def update_samples():
    if request.method == "POST":
        sample_names = request.form.getlist("sample_name")
        dates = request.form.getlist("date")
        sites = request.form.getlist("site")
        groups = request.form.getlist("group")
        reads = request.form.getlist("reads")
        df = pd.DataFrame({
            "sample_name": sample_names,
            "date": dates,
            "site": sites,
            "group": groups,
            "reads": reads
        })
        df["date"] = pd.to_datetime(df["date"], errors='coerce').dt.strftime('%Y-%m-%d').fillna('')
        SAMPLES.clear()
        SAMPLES.extend(df.to_dict(orient="records"))
        if not df.empty:
            filepath = f"{IMPORT_FOLDER.rstrip('/')}/samplesheet_{uuid.uuid4().hex}.csv"
            df.to_csv(filepath, index=False)
            EXP_CONFIG.set("samplesheet", filepath)
            EXP_CONFIG.set("n_samples", df.shape[0])

        flash(["Fichier d'entrée mis à jour avec succès."], "success")
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
    return redirect(url_for("index"))

@socketio.on("cancel_workflow")
def cancel_workflow():
    if WF_SUBPROCESS.process:
        WF_SUBPROCESS.process.kill()
    emit("workflow_cancelled", {"success": True})


if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000, debug=True, allow_unsafe_werkzeug=True)
