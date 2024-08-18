import os
import sys
import shutil
import pathlib
import logging
from mypy import stubgen
from setuptools import Extension, setup
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QFileDialog,
    QLineEdit,
    QHBoxLayout,
    QListWidget,
    QMessageBox,
)

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


def get_source_files(sources, exclude_dirs):
    source_dirs = set()
    source_files = set()

    for dir_or_file in map(pathlib.Path, sources):
        if dir_or_file.is_dir() and not any(
            ex in dir_or_file.parts for ex in exclude_dirs
        ):
            source_dirs.add(dir_or_file.resolve())

        elif dir_or_file.is_file() and dir_or_file.suffix == ".py":
            source_files.add((dir_or_file.stem, str(dir_or_file.resolve())))

    for source_dir in source_dirs:
        for file in source_dir.rglob("*.py"):
            if not any(ex in file.parts for ex in exclude_dirs):
                source_files.add((file.stem, str(file.resolve())))

    return sorted(source_files)


def generate_library(name, source, out_dir):
    logging.info(f"Generating library for {name}")
    try:
        copy_to_dir = os.path.join(os.path.dirname(source) + ".library")
        os.makedirs(copy_to_dir, exist_ok=True)

        if name in {"__init__", "main"}:
            copy_from = source
            copy_to = os.path.join(copy_to_dir, name) + ".py"

            pathlib.Path(copy_to).unlink(missing_ok=True)
            shutil.copyfile(copy_from, copy_to)

            return

        shutil.rmtree(out_dir, ignore_errors=True)
        stubgen.main([source])
        setup(ext_modules=[Extension(name, [source])])

        for root, dirs, files in os.walk(out_dir):
            for file in files:
                copy_from = os.path.join(root, file)
                copy_to = os.path.join(copy_to_dir, file)

                pathlib.Path(copy_to).unlink(missing_ok=True)
                shutil.copyfile(copy_from, copy_to)

    except Exception as e:
        logging.error(f"Failed to generate library for {name}: {e}")
    finally:
        c_file = source[: source.rindex(".")] + ".c"
        pathlib.Path(c_file).unlink(missing_ok=True)


def generate_libraries(source_files):
    base_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    out_dir = os.path.join(base_dir, "out")

    sys.argv[1:] = ["build_ext", "--build-lib", out_dir]

    for name, source in source_files:
        generate_library(name, source, out_dir)

    # Clean up temporary directories
    shutil.rmtree(os.path.join(base_dir, ".mypy_cache"), ignore_errors=True)
    shutil.rmtree(os.path.join(base_dir, "build"), ignore_errors=True)
    shutil.rmtree(out_dir, ignore_errors=True)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Python to Library Compiler")
        self.setGeometry(100, 100, 500, 600)

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Layout
        layout = QVBoxLayout()

        # Source file/directory selection
        self.source_list = QListWidget()
        layout.addWidget(QLabel("Selected Files/Directories:"))
        layout.addWidget(self.source_list)

        select_files_button = QPushButton("Add Files")
        select_files_button.clicked.connect(self.add_files)
        layout.addWidget(select_files_button)

        select_dirs_button = QPushButton("Add Directories")
        select_dirs_button.clicked.connect(self.add_directories)
        layout.addWidget(select_dirs_button)

        # Exclude directories
        exclude_layout = QHBoxLayout()
        self.exclude_input = QLineEdit(".venv")
        exclude_layout.addWidget(QLabel("Exclude Directories:"))
        exclude_layout.addWidget(self.exclude_input)
        layout.addLayout(exclude_layout)

        # Compile button
        compile_button = QPushButton("Compile")
        compile_button.clicked.connect(self.compile)
        layout.addWidget(compile_button)

        central_widget.setLayout(layout)

    def add_files(self):
        files, _ = QFileDialog.getOpenFileNames(
            self, "Select Python Files", "", "Python Files (*.py)"
        )
        for file in files:
            self.source_list.addItem(file)

    def add_directories(self):
        dir = QFileDialog.getExistingDirectory(self, "Select Directory")
        if dir:
            self.source_list.addItem(dir)

    def compile(self):
        sources = [
            self.source_list.item(i).text() for i in range(self.source_list.count())
        ]
        exclude_dirs = self.exclude_input.text().split()

        source_files = get_source_files(sources, exclude_dirs)

        if not source_files:
            QMessageBox.warning(
                self, "No Source Files", "No available source files found."
            )
            return

        generate_libraries(source_files)
        QMessageBox.information(
            self, "Compilation Complete", "Libraries generated successfully."
        )


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
