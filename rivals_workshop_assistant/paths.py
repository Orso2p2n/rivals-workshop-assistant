import sys
from pathlib import Path


def get_exe_path():
    return Path(sys.argv[0])


ASSISTANT_FOLDER = Path("assistant")
ASSISTANT_EXE_NAME = "rivals_workshop_assistant.exe"
ASSISTANT_TMP_EXE_NAME = "rivals_workshop_assistant.exe_"

SPRITES_FOLDER = Path("sprites")
SCRIPTS_FOLDER = Path("scripts")
ANIMS_FOLDER = Path("anims")

REPO_OWNER = "Rivals-Workshop-Community-Projects"
ASSISTANT_REPO_NAME = "rivals-workshop-assistant"
LIBRARY_REPO_NAME = "injector-library"
INJECT_FOLDER = ASSISTANT_FOLDER / Path(".inject")
USER_INJECT_FOLDER = ASSISTANT_FOLDER / Path("user_inject")
