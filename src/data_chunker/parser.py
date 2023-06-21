import sys
from pathlib import Path

def get_code_lines(file: Path) -> list:
    # Open file containing code
    with open( file, 'r' ) as r:
        return r.readlines()

def get_file_list(code_path: str, file_extension: str = "*.java") -> list:

    file_list = list(Path(code_path).glob("**/"+file_extension))

    if len(file_list) < 1:
        print("The folder "+code_path+" should be populated with at least one "
              +file_extension+" file", file=sys.stderr)
        sys.exit()

    return file_list