import argparse
import json
from pathlib import Path


def generate_types(file_name: str, body: object) -> None:
    pretext = """from typing import TypedDict, List, Union\n\n"""
    types = {}

    def generate_type(name: str, value: object) -> str:
        if isinstance(value, dict):
            return generate_dict_type(name, value)
        elif isinstance(value, list):
            return generate_list_type(name, value)
        else:
            return type(value).__name__

    def generate_dict_type(name, dictionary: dict) -> str:
        """Returns an entry from types
        """
        typestr = ""
        for key, value in dictionary.items():
            typestr += f"'{key}': "
            typestr += generate_type(key, value)
            typestr += ", "
        if f"TypedDict('{name}', {{{typestr}}})" not in types.keys():
            types[name] = f"TypedDict('{name}', {{{typestr}}})"
        return name

    def generate_list_type(name, the_list: list) -> str:
        list_types = set(map(lambda x: type(x).__name__, the_list))
        if len(list_types) > 1:
            typestr = "Union[" + ", ".join(list_types) + "]"
        else:
            typestr = list(list_types)[0]
        return f"List[{typestr}]"

    list_type_index = 0
    file_name = file_name[:-5]
    # all_typesstr = file_name + f" = TypedDict('{file_name}', {{{}}})\n"
    it = generate_type(file_name, body)
    all_typesstr = "\n".join(map(lambda x: f"{x[0]} = {x[1]}", types.items()))
    # all_typesstr += f"\n{file_name} = {types[it]}"

    Path(f"{file_name}.py").write_text(f"{pretext}{all_typesstr}\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="takes a file path to a json and outputs a .py"
    )
    parser.add_argument("path", metavar="path/to/file.json", type=str)

    file_path = Path(parser.parse_args().path)
    generate_types(file_path.name, json.loads(file_path.read_text()))
