import os
import sys
import shutil
import pathlib
import logging
from mypy import stubgen
from setuptools import Extension, setup


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


def generate_libraries(source_files):
    base_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    out_dir = os.path.join(base_dir, "out")

    argv_save = sys.argv[1:]
    sys.argv[1:] = ["build_ext", "--build-lib", out_dir]

    for name, source in source_files:
        _generate_library(name, source, out_dir)

    sys.argv[1:] = argv_save

    # Clean up temporary directories
    shutil.rmtree(os.path.join(base_dir, ".mypy_cache"), ignore_errors=True)
    shutil.rmtree(os.path.join(base_dir, "build"), ignore_errors=True)
    shutil.rmtree(out_dir, ignore_errors=True)


def _generate_library(name, source, out_dir):
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
