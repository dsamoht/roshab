from __future__ import annotations
from collections import defaultdict
from datetime import datetime
from pathlib import Path
import subprocess
import threading

import tkinter as tk
from tkinter import filedialog

from .custom_tooltip import CustomTooltip


APP_WIDTH = 1200
APP_HEIGHT = 400

CONF_WIDTH = 600
CONF_HEIGHT = 400

class MainWindow(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title("Taxonomic Classification of Nanopore reads with Kraken2")
        self.center_window(self, APP_WIDTH, APP_HEIGHT)
        self.minsize(APP_WIDTH, APP_HEIGHT)
        self.resizable(False, False)
        self.config = defaultdict(lambda: 'to be configured')
        self.process_wf = None
        
        self.get_docker_status()
        self.create_widgets()
        self.cue_docker_status()
        self.run_workflow()
        self.pipeline_status()
        self.cancel_button()
 
    def update(self):
        self.update_configuration()
        self.create_widgets()
        self.cue_docker_status()
        self.run_workflow()
        self.cancel_button()
    
    def center_window(self, obj, width, height):

        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        pos_x = int((screen_width/2) - (width/2))
        pos_y = int((screen_height/2) - (height/2))
        obj.geometry(f"{width}x{height}+{pos_x}+{pos_y}")

    def create_widgets(self):

        self.bottom_image = tk.PhotoImage(file="roshab_gui/img/bloom_orig.png")
        self.bottom_image_label = tk.Label(self, image=self.bottom_image, width=CONF_WIDTH, height=CONF_HEIGHT)
        self.bottom_image_label.place(x=-5, y=0)
        self.widget_frame = tk.Frame(self, width=CONF_WIDTH/1.5, height=CONF_HEIGHT/2+30, borderwidth=2, relief="solid")
        self.widget_frame.place(x=100, y=100)

        exit_button = tk.Button(self, text="Quit", command=self.destroy, border=0)
        exit_button.place(x=APP_WIDTH/2 -160, y=APP_HEIGHT-100)


        # create experiment name
        self.exp_name_label = tk.Label(self.widget_frame, text="Experiment name :", font='Helvetica 14 bold')
        self.exp_name_label.place(x=5, y=8)
        self.exp_name_entry = tk.Entry(self.widget_frame)
        self.exp_name_entry.place(x=140, y=5)
        validate_exp_button = tk.Button(self.widget_frame, text="OK", command=self.confirm_exp_name)
        validate_exp_button.place(x=335, y=4)

        # choose input directory
        input_dir_button = tk.Button(self.widget_frame, text="Select Input Directory", command=self.choose_directory)
        input_dir_button.place(x=100, y=40)

        # report chosen exp_name and input_dir
        self.config_label = tk.Label(self.widget_frame, text="Run configuration :", font='Helvetica 14 bold')
        self.config_label.place(x=42, y=80)
        self.config_frame = tk.Frame(self.widget_frame, borderwidth=2, relief="solid", width=300, height=70)
        self.config_frame.place(x=45, y=100)

        self.exp_name_report = tk.Label(self.config_frame, text=f"Experiment name : {self.config['exp_name'][0:20]}{'...' if len(self.config['exp_name']) > 20 else ''}", font='Helvetica 12')
        self.exp_name_report.place(x=5, y=5)
        self.input_dir_report = tk.Label(self.config_frame, text=f"Input directory :       {'...' if len(self.config['input_dir']) > 20 else ''}{self.config['input_dir'][-20:]}", font='Helvetica 12')
        self.input_dir_report.place(x=5, y=25)

        # pipeline status
        self.output_label = tk.Label(self, text="Pipeline output :", font='Helvetica 14 bold')
        self.output_label.place(x=620, y=7)

    def pipeline_status(self):
        self.pipeline_status_text = tk.Text(self, borderwidth=2, relief="solid")
        self.pipeline_status_text.place(x=620, y=30, width=550, height=350)

    def confirm_exp_name(self):
        exp_name = self.exp_name_entry.get()
        if exp_name:
            for char in exp_name:
                if char in [r"?", "\\", r"/", r".", r",", r":"]:
                    self.update()
                    return self.config
        else:
            self.update()
            return self.config
        self.config['exp_name'] = exp_name
        self.update()

    def launch_workflow(self):

        self.run_workflow_button.config(state="disabled")
        now = datetime.now().strftime("roshab-wf_out_%Y_%m_%d_%H_%M")
        output = Path(self.config['input_dir']).joinpath(now)

        self.process_wf = subprocess.Popen(["nextflow", "run", "roshab-wf.nf",
                                    "-profile", "docker,local",
                                    "--exp", self.config['exp_name'],
                                    "--output", str(output),
                                    "--reads", self.config['input_dir']],
                                    universal_newlines=True,
                                    shell=False,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT)

        self.pipeline_status_text.delete(1.0, tk.END)

        self.update()
        while True:
            line_out = self.process_wf.stdout.readline()
            if self.process_wf.poll() is not None:
                break
            if output:
                self.pipeline_status_text.insert(tk.END, line_out)
                self.pipeline_status_text.see("end")

        self.process_wf.kill()
        self.process_wf = None
        self.update()
        return

    def get_docker_status(self):
        try:
            subprocess.check_output('docker info', shell=True)
            self.docker_status = True
        except subprocess.CalledProcessError:
            self.docker_status = False
        self.cue_docker_status()


    def cue_docker_status(self):

        self.docker_frame = tk.Frame(self, width=APP_WIDTH//2, height=60, borderwidth=2, relief="solid")
        self.docker_frame.place(x=0, y=0)

        docker_status_info = tk.Label(self.docker_frame, text="Docker status :", font='Helvetica 14 bold')
        docker_status_info.grid(row=0, column=0, padx=10, pady=10)
        docker_status = tk.Label(self.docker_frame, text=f"{'Running' if self.docker_status else 'Not running'}", bg=f"{'green' if self.docker_status else 'red'}", font='Helvetica 14 bold')
        docker_status.grid(row=0, column=1, padx=10, pady=10)
        docker_info = tk.Label(self.docker_frame, text="  ?  ", bg="cyan", font='Helvetica 14 bold')
        docker_info.grid(row=0, column=2, padx=10, pady=10)
        CustomTooltip(docker_info, "Docker is the engine running the workflow.\nIf it is not running, enable it by opening\nDocker Desktop and restart this application.")

    def choose_directory(self):
        self.config['input_dir'] = filedialog.askdirectory(initialdir='/mnt/', mustexist=True)
        if self.config['input_dir'] == '':
            self.config['input_dir'] = 'to be configured'
        self.update()

    def run_workflow(self):
        enabled = self.docker_status and (self.config['exp_name'] != "to be configured") and (self.config['input_dir'] not in ['to be configured', '']) and self.process_wf is None
        self.run_workflow_button = tk.Button(self, text="RUN", fg="green", command=threading.Thread(target=self.launch_workflow).start, state=["disabled" if not enabled else "normal"], borderwidth=2, highlightthickness=2)
        self.run_workflow_button.place(x=200, y=280)

    def update_configuration(self):
        self.exp_name_report["text"] = f"Experiment name : {self.config['exp_name']}"
        self.input_dir_report["text"] = f"Input directory : {self.config['input_dir']}"

    def cancel_workflow(self):
        self.process_wf.kill()
        self.process_wf = None
        self.update()

    def cancel_button(self):
        self.cancel_workflow_button = tk.Button(self, text="Cancel", fg="red", command=self.cancel_workflow, state=["normal" if self.process_wf else "disabled"], borderwidth=2, highlightthickness=2)
        self.cancel_workflow_button.place(x=300, y=280)
