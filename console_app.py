import sys
import logging
import argparse
from toLibrary import get_source_files, generate_libraries

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

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
