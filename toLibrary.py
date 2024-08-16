import os, pathlib, shutil
import sys, platform
from setuptools import Extension, setup

SOURCE_DIRS = []
SOURCE_FILES = []


for dir_or_file in sys.argv[1:]:
    if os.path.isdir(dir_or_file):
        SOURCE_DIRS.append(os.path.abspath(dir_or_file))
    elif os.path.isfile(dir_or_file):
        SOURCE_FILES.append(os.path.abspath(dir_or_file))


for source_dir in SOURCE_DIRS:
    for root, dirs, files in os.walk(source_dir):
        for file in files:
            if (not file.endswith((".py", ".pyx"))) or file.startswith("__init__"):
                continue
            name = file[: file.rindex(".")]
            SOURCE_FILES.append((name, os.path.join(root, file)))


if not SOURCE_FILES:
    sys.exit("No available source found.")


sys.argv[1:] = ["build_ext", "--inplace"]
ext_modules = [Extension(name, [source]) for name, source in SOURCE_FILES]
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


for name, source in SOURCE_FILES:
    c_file = source[: source.rindex(".")] + ".c"
    pathlib.Path(c_file).unlink(missing_ok=True)

    for library in dynamic_libraries:
        if not library.startswith(name):
            continue

        move_to_dir = os.path.dirname(source) + ".library"
        move_from = os.path.join(base_dir, library)
        move_to = os.path.join(move_to_dir, library)

        os.makedirs(move_to_dir, exist_ok=True)
        pathlib.Path(move_to).unlink(missing_ok=True)
        shutil.move(move_from, move_to)

        break
