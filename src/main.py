import argparse
import json
import re
from pathlib import Path

# TODO:
#  1. name anon types based on parent type

from typing import Optional, Union, Tuple, Dict, List


def valid_symbol(key: str) -> bool:
    return re.fullmatch(r"[_a-zA-Z]\w*", key) is not None


def title_case(symbol: str) -> str:
    return symbol[0].upper() + symbol[1:]


def generate_types(file_name: str, body: object) -> None:
    anon_index = 0

    def generate_type(name: Optional[str], value: object, root: bool = False) -> Tuple[str, str]:
        if isinstance(value, dict):
            return generate_dict_type(name, value, root)
        elif isinstance(value, list):
            return generate_list_type(value)
        else:
            it = type(value).__name__
            if it == "NoneType":
                it = "None"
            return it, it

    def generate_dict_type(name: Optional[str], dictionary: Dict[str, object], root: bool = False) -> Tuple[str, str]:
        """Returns an entry from types
        """
        typestr = ""
        protocol_typestr = ""
        empty_protocol_flag = True
        for key, value in dictionary.items():
            temp_type = generate_type(key, value)
            typestr += f"'{key}': "
            typestr += temp_type[0]
            typestr += ", "
            if valid_symbol(key):
                empty_protocol_flag = False
                protocol_typestr += f"    {key}: "
            else:
                protocol_typestr += f"    # {key}: "
            protocol_typestr += temp_type[1]
            protocol_typestr += "\n"
        if empty_protocol_flag:
            protocol_typestr += "    pass\n"
        if not name:
            # should be f"{parent_type}_child{index}"
            nonlocal anon_index
            name = f"child{anon_index}"
            anon_index += 1
        if not root:
            if name.lower() in types:
                name += "1"
            i = 1
            while name.lower() in types:
                name = name[:-len(str(i))] + str(i + 1)
                i += 1
            types[name] = f"TypedDict('{name}', {{{typestr}}})"
            if valid_symbol(name):
                protocols[title_case(name)] = f"""class {title_case(name)}(Protocol):
{protocol_typestr}"""
            else:
                protocols[title_case(name)] = f"""\"""INVALID SYMBOL
class {title_case(name)}(Protocol):
{protocol_typestr}\"\"\""""
            return name, title_case(name)
        else:
            return f"TypedDict('{name}', {{{typestr}}})", f"""class {title_case(name)}(Protocol):
{protocol_typestr}"""

    def generate_list_type(the_list: List[object]) -> Tuple[str, str]:
        all_types = {generate_type(None, it) for it in the_list}
        list_types = {it[0] for it in all_types}
        proc_list_types = {it[1] for it in all_types}
        if len(all_types) > 1:
            typestr = "Union[" + ", ".join(list_types) + "]"
            proc_typestr = "Union[" + ", ".join(proc_list_types) + "]"
        else:
            typestr = list(list_types)[0]
            proc_typestr = list(proc_list_types)[0]
        return f"List[{typestr}]", f"List[{proc_typestr}]"

    pretext = """from typing import TypedDict, List, Union, Protocol\n\n"""
    file_name = file_name[:-5]
    types = {file_name: "<PLACEHOLDER>"}
    protocols: Dict[str, str] = {}
    root_type = generate_type(file_name, body, True)
    types.pop(file_name)
    all_typesstr = ""
    if typeddicts:
        all_typesstr += "\n".join(map(lambda x: f"{x[0]} = {x[1]}", types.items()))
        all_typesstr += f"\n{file_name} = {root_type[0]}\n\n\n"
    if gen_protocols:
        all_typesstr += "\n\n".join(protocols.values())
        if isinstance(body, dict):
            all_typesstr += f"\n\n{root_type[1]}"
        else:
            all_typesstr += f"\n\n{file_name} = {root_type[1]}"

    Path(f"{file_name}.py").write_text(f"{pretext}{all_typesstr}\n\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="takes a file path to a json and outputs a .py"
    )
    parser.add_argument("path", metavar="path/to/file.json", type=str)
    parser.add_argument("--protocols", action="store_true")
    parser.add_argument("--typeddicts", action="store_true")
    args = parser.parse_args()

    file_path = Path(args.path)
    gen_protocols = args.protocols
    typeddicts = args.typeddicts
    if not gen_protocols and not typeddicts:
        gen_protocols = typeddicts = True
    generate_types(file_path.name, json.loads(file_path.read_text()))
