import os
import sys
import shutil
import pathlib
import logging
import argparse
from mypy import stubgen
from setuptools import Extension, setup


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

        elif (
            dir_or_file.is_file()
            and dir_or_file.suffix == ".py"
            and dir_or_file.stem not in ["__init__", "main"]
        ):
            source_files.add((dir_or_file.stem, str(dir_or_file.resolve())))

    for source_dir in source_dirs:
        for file in source_dir.rglob("*.py"):
            if not any(
                ex in file.parts for ex in exclude_dirs
            ) and dir_or_file.stem not in ["__init__", "main"]:
                source_files.add((file.stem, str(file.resolve())))

    return sorted(source_files)


def generate_library(name, source, out_dir):
    logging.info(f"Generating library for {name}")
    try:
        shutil.rmtree(out_dir, ignore_errors=True)

        stubgen.main([source])
        setup(ext_modules=[Extension(name, [source])])

        move_to_dir = os.path.join(os.path.dirname(source) + ".library")
        os.makedirs(move_to_dir, exist_ok=True)

        for root, dirs, files in os.walk(out_dir):
            for file in files:
                move_from = os.path.join(root, file)
                move_to = os.path.join(move_to_dir, file)

                pathlib.Path(move_to).unlink(missing_ok=True)
                shutil.move(move_from, move_to)

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


if __name__ == "__main__":
    # Command-line argument parsing
    parser = argparse.ArgumentParser(description="Compile Python files to libraries.")
    parser.add_argument(
        "sources", nargs="+", help="Python source files or directories to compile."
    )
    parser.add_argument(
        "--exclude", nargs="*", default=[".venv"], help="Directories to exclude."
    )
    args = parser.parse_args()

    # Get the list of source files
    source_files = get_source_files(args.sources, args.exclude)

    if not source_files:
        sys.exit("No available source found.")

    # Generate libraries
    generate_libraries(source_files)