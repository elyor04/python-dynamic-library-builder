import sys
import logging
from toLibrary import get_source_files, generate_libraries
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
