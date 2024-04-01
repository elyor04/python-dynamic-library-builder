import os, pathlib, shutil
import sys, platform
from setuptools import Extension, setup

SOURCE_DIR = "path/to/folder"
source_files = []

for root, dirs, files in os.walk(SOURCE_DIR):
    for file in files:
        if (not file.endswith((".py", ".pyx"))) or file.startswith("__init__"):
            continue
        name = file[: file.rindex(".")]
        source_files.append((name, os.path.join(root, file)))

sys.argv[1:] = ["build_ext", "--inplace"]
ext_modules = [Extension(name, [source]) for name, source in source_files]
setup(ext_modules=ext_modules)

base_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
build_dir = os.path.join(base_dir, "build")
shutil.rmtree(build_dir, ignore_errors=True)

extension = ".pyd" if platform.system().lower() == "windows" else ".so"
dynamic_libraries = [
    file
    for file in os.listdir(base_dir)
    if (os.path.isfile(file) and file.endswith(extension))
]

for name, source in source_files:
    c_file = source[: source.rindex(".")] + ".c"
    pathlib.Path(c_file).unlink(missing_ok=True)

    for library in dynamic_libraries:
        if not library.startswith(name):
            continue
        move_from = os.path.join(base_dir, library)
        move_to = os.path.join(os.path.dirname(source), library)
        pathlib.Path(move_to).unlink(missing_ok=True)
        shutil.move(move_from, move_to)
        break
