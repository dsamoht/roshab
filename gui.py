import subprocess

try:
    import PySide6
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "PySide6"])


from datetime import datetime
from pathlib import Path
import sys

from PySide6.QtWidgets import (QApplication, QMainWindow, QPushButton, QVBoxLayout, 
                               QTextEdit, QWidget, QDialog, QGridLayout, QLabel, 
                               QLineEdit, QDialogButtonBox, QFileDialog)

from PySide6.QtCore import QProcess


class NewExperimentDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("New Analysis")
        self.layout = QVBoxLayout()

        self.grid_layout = QGridLayout()
        self.layout.addLayout(self.grid_layout)

        # Labels and LineEdits for form fields
        self.name_label = QLabel("Name: ")
        self.name_edit = QLineEdit()
        self.grid_layout.addWidget(self.name_label, 0, 0)
        self.grid_layout.addWidget(self.name_edit, 0, 1)

        self.path_edit = QLineEdit()
        self.path_edit.setReadOnly(True)
        self.path_button = QPushButton("Select Path")
        self.path_button.clicked.connect(self.open_file_dialog)
        self.grid_layout.addWidget(self.path_edit, 1, 1)
        self.grid_layout.addWidget(self.path_button, 1, 0)

        # Dialog buttons
        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        self.layout.addWidget(self.button_box)

        self.setLayout(self.layout)

    def open_file_dialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ShowDirsOnly
        directory = QFileDialog.getExistingDirectory(self, "Select Directory", options=options)
        if directory:
            self.path_edit.setText(directory)

    def get_data(self):
        return {
            "name": self.name_edit.text(),
            "path": self.path_edit.text()
        }


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("RosHAB - Taxonomic Tool")
        self.width, self.height = 400, 400
        self.resize(self.width, self.height)
        self.setMinimumSize(self.width, self.height)
        self.p = None

        # Layout
        self.layout = QVBoxLayout()

        # Button to start new analysis
        self.select_button = QPushButton("New Analysis", self)
        self.select_button.clicked.connect(self.open_new_experiment_dialog)
        self.layout.addWidget(self.select_button)

        # Text edit to display experiment details
        self.show_directory = QTextEdit()
        self.show_directory.setReadOnly(True)
        self.layout.addWidget(self.show_directory)

        # Button to run analysis
        self.run_button = QPushButton("Run", self)
        now = datetime.now()
        self.now = now.strftime("roshab-wf_out_%Y_%m_%d_%H_%M_%S")
        self.run_button.clicked.connect(self.run_analysis)
        self.layout.addWidget(self.run_button)

        # Text edit to display pipeline logs
        self.pipeline_log = QTextEdit()
        self.pipeline_log.setReadOnly(True)
        self.layout.addWidget(self.pipeline_log)

        # Central widget
        central_widget = QWidget()
        central_widget.setLayout(self.layout)
        self.setCentralWidget(central_widget)

    def run_analysis(self):
        output = Path(self.data['path']).joinpath(self.now)

        if self.p is None:
            self.p = QProcess()
            self.p.readyReadStandardOutput.connect(self.on_ready_read)
            self.p.finished.connect(self.process_finished)
            try:
                self.p.start("nextflow", ["run", "roshab-wf.nf",
                                          "-profile", "docker,local",
                                          "--exp", self.data['name'],
                                          "--output", str(output),
                                          "--reads", self.data['path']])
            except Exception as e:
                self.pipeline_log.append(f"Error starting process: {e}")

    def process_finished(self):
        self.pipeline_log.append("Process finished.")
        self.p = None

    def on_ready_read(self):
        self.pipeline_log.append(self.p.readAllStandardOutput().data().decode())
        self.pipeline_log.append(self.p.readAllStandardError().data().decode())

    def open_new_experiment_dialog(self):
        dialog = NewExperimentDialog()
        if dialog.exec() == QDialog.Accepted:
            self.data = dialog.get_data()
            self.show_directory.append(f"Experiment Name: {self.data['name']}")
            self.show_directory.append(f"Selected Path: {self.data['path']}")

def main():

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
