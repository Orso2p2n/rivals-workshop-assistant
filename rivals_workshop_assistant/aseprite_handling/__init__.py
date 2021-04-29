import os
import subprocess
from datetime import datetime
from pathlib import Path

from rivals_workshop_assistant import paths
from ._aseprite_loading import RawAsepriteFile
from rivals_workshop_assistant.script_mod import File
from .types import AsepriteTag, TagColor


class Anim:
    def __init__(self, name: str, start: int, end: int):
        """A part of an aseprite file representing a single spritesheet.
        An Aseprite file may contain multiple anims.
        """
        self.name = name
        self.start = start
        self.end = end

    @property
    def num_frames(self):
        return self.end - self.start + 1

    def __eq__(self, other):
        return self.name == other.name


class AsepriteData:
    def __init__(
        self,
        name: str,
        num_frames: int,
        anim_tag_color: TagColor,
        tags: list[AsepriteTag] = None,
    ):
        self.num_frames = num_frames
        if tags is None:
            tags = []
        self.tags = tags
        self.anims = self.get_anims(name, tags, anim_tag_color)

    @classmethod
    def from_path(cls, name: str, path: Path, anim_tag_color: TagColor):
        with open(path, "rb") as f:
            contents = f.read()
            raw_aseprite_file = RawAsepriteFile(contents)
        tags = raw_aseprite_file.get_tags()
        num_frames = raw_aseprite_file.get_num_frames()
        return cls(
            name=name, tags=tags, num_frames=num_frames, anim_tag_color=anim_tag_color
        )

    def get_anims(self, name: str, tags: list[AsepriteTag], anim_tag_color: TagColor):
        tag_anims = [
            Anim(name=tag.name, start=tag.start, end=tag.end)
            for tag in tags
            if tag.color == anim_tag_color
        ]
        if tag_anims:
            return tag_anims
        else:
            return [Anim(name=name, start=0, end=self.num_frames - 1)]


class Aseprite(File):
    def __init__(
        self,
        path: Path,
        anim_tag_color: TagColor,
        modified_time: datetime,
        processed_time: datetime = None,
        content=None,
    ):
        super().__init__(path, modified_time, processed_time)
        self.anim_tag_color = anim_tag_color
        self._content = content

    @property
    def content(self) -> AsepriteData:
        if self._content is None:
            self._content = AsepriteData.from_path(
                name=self.path.stem, path=self.path, anim_tag_color=self.anim_tag_color
            )
        return self._content

    @property
    def name(self):
        return self.path.stem

    def save(self, root_dir: Path, aseprite_path: Path, has_small_sprites: bool):
        for anim in self.content.anims:
            self._save_anim(
                anim=anim,
                root_dir=root_dir,
                aseprite_path=aseprite_path,
                has_small_sprites=has_small_sprites,
            )

    def _save_anim(
        self, anim: Anim, root_dir: Path, aseprite_path: Path, has_small_sprites: bool
    ):
        self._delete_old_save(root_dir, anim.name)
        dest_name = (
            f"{self.get_anim_base_name(root_dir, anim.name)}"
            f"_strip{anim.num_frames}.png"
        )
        dest = root_dir / paths.SPRITES_FOLDER / dest_name

        dest.parent.mkdir(parents=True, exist_ok=True)

        command_parts = [
            f'"{aseprite_path}"',
            "-b",
            f"--frame-range {anim.start},{anim.end}",
            f'"{self.path}"',
            f"--scale {int(has_small_sprites) + 1}",
            f'--sheet "{dest}"',
        ]

        export_command = " ".join(command_parts)

        subprocess.run(export_command)

    def _delete_old_save(self, root_dir: Path, name: str):
        old_paths = (root_dir / paths.SPRITES_FOLDER).glob(
            f"{self.get_anim_base_name(root_dir, name)}_strip*.png"
        )
        for old_path in old_paths:
            os.remove(old_path)

    def get_anim_base_name(self, root_dir: Path, name: str):
        relative_path = self.path.relative_to(root_dir / paths.ANIMS_FOLDER)
        subfolders = list(relative_path.parents)[:-1]
        path_parts = [path.name for path in reversed(subfolders)] + [name]
        base_name = "_".join(path_parts)
        return base_name
