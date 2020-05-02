from typing import List
from pathlib import Path
import argparse
import ntpath
import json
import os

# TODO:
# typed arrays

parser = argparse.ArgumentParser(description="takes a file path to a json and outputs a .py")
parser.add_argument("path", metavar="path/to/file.json", type=str)


def generateTypes(typename: str, dictionary: dict) -> None:
    pretext = "from typing import TypedDict\n\n"
    types: List[str] = []

    def generateType(typename: str, dictionary: dict) -> None:
        typestr = ""
        for key, value in dictionary.items():
            typestr += f"'{key}': "
            if isinstance(value, dict):
                generateType(key, value)
                typestr += key
            else:
                typestr += type(value).__name__
            typestr += ", "
        if typestr not in types:
            types.append(f"{typename} = TypedDict('{typename}', {{{typestr}}})")

    generateType(typename, dictionary)
    alltypesstr = "\n".join(types)
    Path(f"{typename}.py").write_text(f"{pretext}{alltypesstr}\n")


def loadJSON(path: str):
    with open(path) as f:
        return json.load(f)


jsonpath: str = parser.parse_args().path
generateTypes(os.path.splitext(ntpath.basename(jsonpath))[0], loadJSON(jsonpath))
