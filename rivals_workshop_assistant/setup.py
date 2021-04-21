from pathlib import Path

import rivals_workshop_assistant.assistant_config_mod
from rivals_workshop_assistant import paths as paths
from rivals_workshop_assistant.injection import paths as inject_paths
from rivals_workshop_assistant.injection.installation import (
    ANIMS_FOLDER_README,
)
from rivals_workshop_assistant.assistant_config_mod import DEFAULT_CONFIG
from rivals_workshop_assistant.file_handling import create_file


def make_basic_folder_structure(root_dir: Path):
    (root_dir / inject_paths.USER_INJECT_FOLDER).mkdir(parents=True, exist_ok=True)

    (root_dir / paths.ANIMS_FOLDER).mkdir(parents=True, exist_ok=True)
    create_file(path=(root_dir / paths.ANIMS_FOLDER), content=ANIMS_FOLDER_README)

    create_file(
        path=(root_dir / rivals_workshop_assistant.assistant_config_mod.PATH),
        content=DEFAULT_CONFIG,
    )
