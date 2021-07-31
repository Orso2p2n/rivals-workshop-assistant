import re
from pathlib import Path
from typing import List, Tuple

import rivals_workshop_assistant.paths
from .dependency_handling import GmlInjection, INJECT_TYPES


def read_injection_library(root_dir: Path) -> List[GmlInjection]:
    """Controller"""
    inject_gml_paths = list(
        (root_dir / rivals_workshop_assistant.paths.INJECT_FOLDER).rglob("*.gml")
    ) + list(
        (root_dir / rivals_workshop_assistant.paths.USER_INJECT_FOLDER).rglob("*.gml")
    )

    full_lib = []
    for file in inject_gml_paths:
        full_lib.extend(get_injection_library_from_file(file))
    return full_lib


def get_injection_library_from_gml(gml: str) -> List[GmlInjection]:
    dependencies = []
    dependency_strings = gml.split("#")[1:]
    for dependency_string in dependency_strings:
        inject_type, name, content = _get_inject_components(dependency_string)

        for possible_inject_type in INJECT_TYPES:
            if inject_type == possible_inject_type.IDENTIFIER_STRING:
                injection = possible_inject_type.from_gml(name, content)
                break
        else:
            raise ValueError(f"unknown inject type {inject_type}")
        dependencies.append(injection)

    return dependencies


def get_injection_library_from_file(gml_path: Path) -> List[GmlInjection]:
    dependencies = get_injection_library_from_gml(gml_path.read_text())
    #saving filepath ideally done through constructor 
    #didn't feel like upsetting signature of all other functions just yet
    for dep in dependencies:
        dep.filepath = gml_path
    return dependencies


def _get_inject_components(gml: str) -> Tuple[str, str, str]:
    inject_type, after_inject_type = gml.split(" ", maxsplit=1)
    if "(" in after_inject_type:
        pattern = r"(\n|{)"
    else:
        pattern = r"(\s|{)"
    split = re.split(pattern=pattern, string=after_inject_type, maxsplit=1)
    return inject_type, split[0], split[1] + split[2]
