import configparser
import time
from pathlib import Path
from PIL import Image

import pytest
from testfixtures import TempDirectory

from rivals_workshop_assistant import paths, injection
from rivals_workshop_assistant.setup import make_basic_folder_structure
from rivals_workshop_assistant.injection import apply_injection, installation
from rivals_workshop_assistant.injection.paths import INJECT_FOLDER, USER_INJECT_FOLDER
from rivals_workshop_assistant.injection.dependency_handling import Define
import rivals_workshop_assistant.main as src
from tests.testing_helpers import (
    make_script,
    ScriptWithPath,
    create_script,
    make_script_from_script_with_path,
    supply_anim,
    TEST_ANIM_NAME,
)


pytestmark = pytest.mark.slow

script_1 = ScriptWithPath(
    path=Path("scripts/script_1.gml"),
    content="""\
script 1
    content
    needs_other()
    
    
    another_func()""",
)

script_subfolder = ScriptWithPath(
    path=Path("scripts/subfolder/script_subfolder.gml"),
    content="""\
script in subfolder
func()""",
)

injection_at_root = ScriptWithPath(
    path=INJECT_FOLDER / Path("at_root.gml"),
    content="""\
#define func {
    // some docs
    //some more docs
    func content

}

#define another_func
    another func 
    content

""",
)

injection_in_subfolder = ScriptWithPath(
    path=USER_INJECT_FOLDER / Path("subfolder/in_subfolder.gml"),
    content="""\
#define needs_other {
    other()
}

#define other
    other content

""",
)

func = Define(name="func", docs="some docs\nsome more docs", content="func content")
another_func = Define(name="another_func", content="another func\ncontent")
needs_other = Define(name="needs_other", content="other()")
other = Define(name="other", content="other content")


def test_read_scripts():
    with TempDirectory() as tmp:
        create_script(tmp, script_1)
        create_script(tmp, script_subfolder)

        result = src.read_scripts(Path(tmp.path), {})

        assert result == [
            make_script_from_script_with_path(tmp, script_1),
            make_script_from_script_with_path(tmp, script_subfolder),
        ]


# TODO create test for correct times


def test_read_injection_library():
    with TempDirectory() as tmp:
        create_script(tmp, injection_at_root)
        create_script(tmp, injection_in_subfolder)

        result_library = injection.read_injection_library(Path(tmp.path))
        assert result_library == [func, another_func, needs_other, other]


def test_full_injection():
    with TempDirectory() as tmp:
        create_script(tmp, script_1)
        create_script(tmp, script_subfolder)
        create_script(tmp, injection_at_root)
        create_script(tmp, injection_in_subfolder)

        scripts = src.read_scripts(Path(tmp.path), {})
        library = injection.read_injection_library(Path(tmp.path))
        result_scripts = apply_injection(scripts=scripts, injection_library=library)

        expected_script_1 = f"""\
{script_1.content}

{injection.application.INJECTION_START_HEADER}
{another_func.gml}

{needs_other.gml}

{other.gml}
{injection.application.INJECTION_END_HEADER}"""

        expected_subfolder = f"""\
{script_subfolder.content}

{injection.application.INJECTION_START_HEADER}
{func.gml}
{injection.application.INJECTION_END_HEADER}"""

        assert result_scripts == [
            make_script(
                script_1.absolute_path(tmp),
                original_content=script_1.content,
                working_content=expected_script_1,
            ),
            make_script(
                script_subfolder.absolute_path(tmp),
                original_content=script_subfolder.content,
                working_content=expected_subfolder,
            ),
        ]

        src.save_scripts(root_dir=Path(tmp.path), scripts=result_scripts)

        actual_script_1 = tmp.read(script_1.path.as_posix(), encoding="utf8")
        assert actual_script_1 == expected_script_1

        actual_script_subfolder = tmp.read(
            script_subfolder.path.as_posix(), encoding="utf8"
        )
        assert actual_script_subfolder == expected_subfolder


def test__make_basic_folder_structure__make_missing_config():
    with TempDirectory() as tmp:
        make_basic_folder_structure(Path(tmp.path))

        actual = (Path(tmp.path) / paths.ASSISTANT_CONFIG_PATH).read_text()
        assert actual == installation.DEFAULT_CONFIG


def test__make_basic_folder_structure__config_present():
    with TempDirectory() as tmp:
        config_path = Path(tmp.path) / paths.ASSISTANT_CONFIG_PATH
        create_script(tmp, ScriptWithPath(path=config_path, content="a"))

        make_basic_folder_structure(Path(tmp.path))

        actual = config_path.read_text()
        assert actual == "a"


def test__read_anims():
    with TempDirectory() as tmp:
        supply_anim(tmp, TEST_ANIM_NAME)

        result = src.read_anims(root_dir=Path(tmp.path), dotfile={})
        assert len(result) == 1
        assert result[0].path == Path(tmp.path) / "anims" / TEST_ANIM_NAME
        assert result[0].is_fresh


def test__save_anims():
    with TempDirectory() as tmp:
        anims = [supply_anim(tmp, TEST_ANIM_NAME)]
        root_dir = Path(tmp.path)

        config = configparser.ConfigParser()
        config.read("dev_config.ini")
        aseprite_path = config["aseprite"]["path"]

        src.save_anims(
            root_dir=root_dir,
            aseprite_path=Path(aseprite_path),
            anims=anims,
        )

        with Image.open(
            root_dir / paths.SPRITES_FOLDER / f"{TEST_ANIM_NAME.stem}_strip3.png"
        ) as img:
            assert img.height == 66 * 2
            assert img.width == 76 * 3 * 2
