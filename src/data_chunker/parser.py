import sys
import os
from pathlib import Path
import fnmatch

def get_code_lines(file: Path) -> list:
    # Open file containing code
    with open(file, "r") as r:
        return r.readlines()

def get_file_list(code_path, file_extension: str = ".java"):
    file_list = []

    for root, dirs, files in os.walk(code_path):
        for file in files:
            if fnmatch.fnmatch(file,file_extension):
                file_list.append(os.path.join(root, file))


    if len(file_list) < 1:
        print(
            "The folder "
            + code_path
            + " should be populated with at least one "
            + file_extension
            + " file",
            file=sys.stderr,
        )
        sys.exit()
    return file_list