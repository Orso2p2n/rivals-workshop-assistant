import contextlib
import os
import shutil
import tempfile
from pathlib import Path

from PIL import Image
import pytest
from testfixtures import TempDirectory

import rivals_workshop_assistant.aseprite_handling
import rivals_workshop_assistant.assistant_config_mod
import rivals_workshop_assistant.file_handling
import rivals_workshop_assistant.script_mod
import rivals_workshop_assistant.dotfile_mod
import rivals_workshop_assistant.character_config_mod as character_config
from tests import testing_helpers
from tests.testing_helpers import (
    make_empty_file,
    make_script,
    ScriptWithPath,
    create_script,
    make_script_from_script_with_path,
    supply_aseprites,
    TEST_ANIM_NAME,
    get_aseprite_path,
    make_test_config,
)
from rivals_workshop_assistant import paths, injection, info_files
from rivals_workshop_assistant.setup import make_basic_folder_structure
from rivals_workshop_assistant.injection import apply_injection
from rivals_workshop_assistant.paths import INJECT_FOLDER, USER_INJECT_FOLDER
from rivals_workshop_assistant.injection.dependency_handling import Define
import rivals_workshop_assistant.main as src
from rivals_workshop_assistant.aseprite_handling import (
    AsepritePathParams,
    AsepriteConfigParams,
)

pytestmark = pytest.mark.slow


def recursive_delete_directory(root: Path):
    if root.exists():
        for path in root.iterdir():
            if path.is_dir():
                recursive_delete_directory(path)
            else:
                path.unlink()
        root.rmdir()


@contextlib.contextmanager
def TempDirectoryWithSpace():
    tmpfile_with_space = tempfile.mkdtemp(prefix="prefix ")
    yield TempDirectory(path=tmpfile_with_space)
    recursive_delete_directory(Path(tmpfile_with_space))


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

bair = ScriptWithPath(
    path=Path("scripts/attacks/bair.gml"),
    content="""// previous content""",
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

        result = rivals_workshop_assistant.script_mod.read_scripts(Path(tmp.path), {})

        assert result == [
            make_script_from_script_with_path(tmp, script_1),
            make_script_from_script_with_path(tmp, script_subfolder),
        ]


def test_read_injection_library():
    with TempDirectory() as tmp:
        create_script(tmp, injection_at_root)
        create_script(tmp, injection_in_subfolder)

        result_library = injection.read_injection_library(Path(tmp.path))
        assert result_library == [func, another_func, needs_other, other]


def test_full_injection():
    with TempDirectoryWithSpace() as tmp:
        create_script(tmp, script_1)
        create_script(tmp, script_subfolder)
        create_script(tmp, injection_at_root)
        create_script(tmp, injection_in_subfolder)

        scripts = rivals_workshop_assistant.script_mod.read_scripts(Path(tmp.path), {})
        library = injection.read_injection_library(Path(tmp.path))

        apply_injection(scripts=scripts, injection_library=library, anims=[])

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

        assert scripts == [
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

        rivals_workshop_assistant.file_handling.save_scripts(
            root_dir=Path(tmp.path), scripts=scripts
        )

        actual_script_1 = tmp.read(script_1.path.as_posix(), encoding="utf8")
        assert actual_script_1 == expected_script_1

        actual_script_subfolder = tmp.read(
            script_subfolder.path.as_posix(), encoding="utf8"
        )
        assert actual_script_subfolder == expected_subfolder


def test__make_basic_folder_structure__make_missing_config():
    with TempDirectory() as tmp:
        make_basic_folder_structure(Path(tmp.path), Path(tmp.path))

        actual = info_files.YAML_HANDLER.load(
            (
                Path(tmp.path) / rivals_workshop_assistant.assistant_config_mod.PATH
            ).read_text()
        )

        expected = info_files.YAML_HANDLER.load(
            rivals_workshop_assistant.assistant_config_mod.DEFAULT_CONFIG
        )
        assert actual == expected


def test__make_basic_folder_structure__config_present():
    with TempDirectory() as tmp:
        config_path = (
            Path(tmp.path) / rivals_workshop_assistant.assistant_config_mod.PATH
        )
        create_script(tmp, ScriptWithPath(path=config_path, content="a"))

        make_basic_folder_structure(Path(tmp.path), Path(tmp.path))

        actual = config_path.read_text()
        assert actual == "a"


def test__make_basic_folder_structure__overwrites_config():
    with TempDirectory() as root_dir:
        with TempDirectory() as exe_dir:
            # ARRANGE
            exe_config_path = (
                Path(exe_dir.path)
                / rivals_workshop_assistant.assistant_config_mod.FILENAME
            )

            default_override = "field: value"
            create_script(
                exe_dir, ScriptWithPath(path=exe_config_path, content=default_override)
            )

            # ACT
            make_basic_folder_structure(
                exe_dir=Path(exe_dir.path), root_dir=Path(root_dir.path)
            )

            # ASSERT
            project_config_path = (
                Path(root_dir.path)
                / rivals_workshop_assistant.assistant_config_mod.PATH
            )

            actual = info_files.YAML_HANDLER.load(project_config_path.read_text())

            expected = info_files.YAML_HANDLER.load(
                rivals_workshop_assistant.assistant_config_mod.DEFAULT_CONFIG
            )
            expected.update(info_files.YAML_HANDLER.load(default_override))

            assert actual == expected


def test__read_aseprites():
    with TempDirectoryWithSpace() as tmp:
        supply_aseprites(tmp, TEST_ANIM_NAME)

        result = rivals_workshop_assistant.aseprite_handling.read_aseprites(
            root_dir=Path(tmp.path), dotfile={}, assistant_config={}
        )
        assert len(result) == 1
        assert result[0].path == Path(tmp.path) / paths.ANIMS_FOLDER / TEST_ANIM_NAME
        assert result[0].is_fresh


def assert_anim_matches_test_anim(
    root_dir,
    filename=f"{TEST_ANIM_NAME.stem}_strip3.png",
    has_small_sprites=False,
    num_frames=3,
    sprites_folder=paths.SPRITES_FOLDER,
):
    """Right now this assumes that the sprite is the absa dashstart anim stored in
    TEST_ANIM_NAME"""
    if has_small_sprites:
        scale = 1
    else:
        scale = 2

    with Image.open(root_dir / sprites_folder / filename) as img:
        assert img.height == 33 * scale
        assert img.width == 38 * num_frames * scale


@pytest.mark.parametrize("has_small_sprites", [pytest.param(False), pytest.param(True)])
@pytest.mark.aseprite
def test__save_aseprites(has_small_sprites):
    aseprite_path = get_aseprite_path()

    with TempDirectoryWithSpace() as tmp_root_dir, TempDirectoryWithSpace() as exe_dir:
        root_dir = Path(tmp_root_dir.path)
        aseprites = [supply_aseprites(tmp_root_dir)]

        rivals_workshop_assistant.aseprite_handling.save_anims(
            path_params=AsepritePathParams(
                exe_dir=Path(exe_dir.path),
                root_dir=root_dir,
                aseprite_program_path=Path(aseprite_path),
            ),
            config_params=AsepriteConfigParams(
                has_small_sprites=has_small_sprites,
            ),
            aseprites=aseprites,
        )

        assert_anim_matches_test_anim(root_dir, has_small_sprites=has_small_sprites)


@pytest.mark.aseprite
def test__save_aseprites__multiple_tag_colors():
    aseprite_path = get_aseprite_path()

    with TempDirectoryWithSpace() as tmp_root_dir, TempDirectoryWithSpace() as exe_dir:
        root_dir = Path(tmp_root_dir.path)
        aseprites = [
            supply_aseprites(
                tmp_root_dir,
                name="nair_multiple_colors.aseprite",
                anim_tag_colors=["blue", "yellow"],
                window_tag_colors=["red", "green"],
            )
        ]

        rivals_workshop_assistant.aseprite_handling.save_anims(
            path_params=AsepritePathParams(
                exe_dir=Path(exe_dir.path),
                root_dir=root_dir,
                aseprite_program_path=Path(aseprite_path),
            ),
            config_params=AsepriteConfigParams(),
            aseprites=aseprites,
        )

        assert_anim_matches_test_anim(
            root_dir,
            filename=f"anim1_strip1.png",
            has_small_sprites=False,
            num_frames=1,
        )

        assert_anim_matches_test_anim(
            root_dir,
            filename=f"bair_strip2.png",
            has_small_sprites=False,
            num_frames=2,
        )


@pytest.mark.aseprite
def test__save_aseprites__uses_subfolder_name():
    subfolder_name = "subfolder"
    aseprite_path = get_aseprite_path()

    with TempDirectoryWithSpace() as tmp_root_dir, TempDirectoryWithSpace() as exe_dir:
        root_dir = Path(tmp_root_dir.path)
        aseprites = [
            supply_aseprites(tmp_root_dir, relative_dest=Path("anims") / subfolder_name)
        ]

        rivals_workshop_assistant.aseprite_handling.save_anims(
            path_params=AsepritePathParams(
                exe_dir=Path(exe_dir.path),
                root_dir=root_dir,
                aseprite_program_path=Path(aseprite_path),
            ),
            config_params=AsepriteConfigParams(),
            aseprites=aseprites,
        )

        assert_anim_matches_test_anim(
            root_dir,
            filename=f"{subfolder_name}_{TEST_ANIM_NAME.stem}_strip3.png",
            has_small_sprites=False,
        )


@pytest.mark.aseprite
def test__save_aseprites__removes_old_spritesheet():
    aseprite_path = get_aseprite_path()

    with TempDirectory() as tmp_root_dir, TempDirectory() as exe_dir:
        root_dir = Path(tmp_root_dir.path)
        aseprites = [supply_aseprites(tmp_root_dir)]
        old_filename = (
            root_dir / paths.SPRITES_FOLDER / f"{TEST_ANIM_NAME.stem}_strip2.png"
        )
        make_empty_file(old_filename)
        other_filename = root_dir / paths.SPRITES_FOLDER / f"unrelated_strip2.png"
        make_empty_file(other_filename)

        rivals_workshop_assistant.aseprite_handling.save_anims(
            path_params=AsepritePathParams(
                exe_dir=Path(exe_dir.path),
                root_dir=root_dir,
                aseprite_program_path=Path(aseprite_path),
            ),
            config_params=AsepriteConfigParams(),
            aseprites=aseprites,
        )

        assert not old_filename.exists()
        assert other_filename.exists()


@pytest.mark.aseprite
def test__save_aseprites__removes_old_spritesheet__with_subfolder():
    aseprite_path = get_aseprite_path()
    subfolder_name = "subfolder"

    with TempDirectory() as tmp_root_dir, TempDirectory() as exe_dir:
        root_dir = Path(tmp_root_dir.path)
        aseprites = [
            supply_aseprites(tmp_root_dir, relative_dest=Path("anims") / subfolder_name)
        ]
        old_filename = (
            root_dir
            / paths.SPRITES_FOLDER
            / f"{subfolder_name}_{TEST_ANIM_NAME.stem}_strip2.png"
        )
        make_empty_file(old_filename)
        other_filename = (
            root_dir / paths.SPRITES_FOLDER / f"{subfolder_name}_unrelated_strip2.png"
        )
        make_empty_file(other_filename)

        rivals_workshop_assistant.aseprite_handling.save_anims(
            path_params=AsepritePathParams(
                exe_dir=Path(exe_dir.path),
                root_dir=root_dir,
                aseprite_program_path=Path(aseprite_path),
            ),
            config_params=AsepriteConfigParams(),
            aseprites=aseprites,
        )

        assert not old_filename.exists()
        assert other_filename.exists()


@pytest.mark.aseprite
def test__save_aseprites__multiple_aseprites():
    aseprite_path = get_aseprite_path()

    with TempDirectory() as tmp_root_dir, TempDirectory() as exe_dir:
        root_dir = Path(tmp_root_dir.path)
        aseprites = [
            supply_aseprites(
                tmp_root_dir, relative_dest=Path("anims"), anim_tag_colors="blue"
            )
        ]

        rivals_workshop_assistant.aseprite_handling.save_anims(
            path_params=AsepritePathParams(
                exe_dir=Path(exe_dir.path),
                root_dir=root_dir,
                aseprite_program_path=Path(aseprite_path),
            ),
            config_params=AsepriteConfigParams(),
            aseprites=aseprites,
        )

        assert_anim_matches_test_anim(
            root_dir,
            filename=f"anim1_strip1.png",
            has_small_sprites=False,
            num_frames=1,
        )

        assert_anim_matches_test_anim(
            root_dir,
            filename=f"bair_strip2.png",
            has_small_sprites=False,
            num_frames=2,
        )


@pytest.mark.aseprite
def test__aseprites_set_window_data():
    with TempDirectory() as tmp:
        root_dir = Path(tmp.path)

        # setup, make config.ini, make anim and bair
        testing_helpers.make_empty_file(root_dir / character_config.FILENAME)

        make_test_config(root_dir)
        create_script(tmp, bair)
        supply_aseprites(tmp, TEST_ANIM_NAME)

        src.main(exe_dir=root_dir, given_dir=root_dir, guarantee_root_dir=True)

        assert_anim_matches_test_anim(
            root_dir,
            filename=f"anim1_strip1.png",
            has_small_sprites=False,
            num_frames=1,
        )

        assert_anim_matches_test_anim(
            root_dir,
            filename=f"bair_strip2.png",
            has_small_sprites=False,
            num_frames=2,
        )

        assert (
            tmp.read(bair.path.as_posix(), encoding="utf8")
            == f"""\
{bair.content}

{injection.application.INJECTION_START_HEADER}
#macro WINDOW1_FRAMES 1
#define _get_window1_frames()
    return WINDOW1_FRAMES
#macro WINDOW1_FRAME_START 0
#define _get_window1_frame_start()
    return WINDOW1_FRAME_START

#macro WINDOW2_FRAMES 1
#define _get_window2_frames()
    return WINDOW2_FRAMES
#macro WINDOW2_FRAME_START 1
#define _get_window2_frame_start()
    return WINDOW2_FRAME_START
{injection.application.INJECTION_END_HEADER}"""
        )


def test__backup_made():
    with TempDirectory() as tmp:
        root_dir = Path(tmp.path)

        testing_helpers.make_empty_file(root_dir / character_config.FILENAME)

        make_test_config(root_dir)
        create_script(tmp, bair)
        supply_aseprites(tmp, TEST_ANIM_NAME)

        os.mkdir(root_dir / paths.SPRITES_FOLDER)
        shutil.copy(
            Path("tests/assets/sprites/anim1_strip1.png"),
            root_dir / paths.SPRITES_FOLDER,
        )

        src.main(exe_dir=root_dir, given_dir=root_dir, guarantee_root_dir=True)
        assert_anim_matches_test_anim(
            root_dir,
            filename=f"anim1_strip1.png",
            has_small_sprites=False,
            num_frames=1,
            sprites_folder=paths.BACKUP_FOLDER / paths.SPRITES_FOLDER,
        )

        assert (
            tmp.read(
                (paths.BACKUP_FOLDER / paths.ATTACKS_FOLDER / "bair.gml").as_posix(),
                encoding="utf8",
            )
            == f"""{bair.content}"""
        )


def test__empty_project_just_inits():
    with TempDirectory() as tmp:
        root_dir = Path(tmp.path)

        tmp_exe_dir = Path(tmp.path) / "tmp_exe_dir"
        tmp_exe_dir.mkdir()

        testing_helpers.make_empty_file(root_dir / character_config.FILENAME)
        create_script(tmp, script_1)

        src.main(exe_dir=tmp_exe_dir, given_dir=root_dir, guarantee_root_dir=True)

        assert {path.name for path in root_dir.glob("*")} == {
            "anims",
            "assistant",
            "scripts",
            character_config.FILENAME,
            "tmp_exe_dir",
        }

        # Assert dotfile hasn't been made yet. Should show it didn't actually run.
        assert not (root_dir / rivals_workshop_assistant.dotfile_mod.PATH).exists()
