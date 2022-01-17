"""https://github.com/Eiyeron/py_aseprite"""

from .headers import Header, Frame
from .chunks import (
    Chunk,
    OldPaleteChunk_0x0004,
    OldPaleteChunk_0x0011,
    LayerChunk,
    LayerGroupChunk,
    CelChunk,
    CelExtraChunk,
    MaskChunk,
    FrameTagsChunk,
    PathChunk,
    PaletteChunk,
    UserDataChunk,
    SliceChunk,
)
from ..tags import AsepriteTag


class RawAsepriteFile:
    def __init__(self, data):
        self.header, self.frames = parse_data(data)
        self.build_layer_tree()

    def build_layer_tree(self):
        # Assuming that layers are stored in chunk #0.
        # Warn me if they're stored in another chunk
        self.layers = [
            chunk for chunk in self.frames[0].chunks if isinstance(chunk, LayerChunk)
        ]
        stack = []
        self.layer_tree = []
        for layer in self.layers:
            while layer.layer_child_level < len(stack):
                stack.pop()

            if len(stack) > 0:
                stack[len(stack) - 1].children.append(layer)
            else:
                self.layer_tree.append(layer)

            if isinstance(layer, LayerGroupChunk):
                stack.append(layer)

    def get_tags(self):
        if not self.frames:
            return []
        frame_0_chunks = self.frames[0].chunks
        tag_chunks = [
            chunk for chunk in frame_0_chunks if isinstance(chunk, FrameTagsChunk)
        ]
        if not tag_chunks:
            return []
        if len(tag_chunks) > 1:
            assert False
        tag_dicts = tag_chunks[0].tags
        tags = [
            AsepriteTag(
                name=tag_dict["name"],
                start=tag_dict["from"],
                end=tag_dict["to"],
                color=rgb_to_color_name(
                    r=tag_dict["color"]["red"],
                    g=tag_dict["color"]["green"],
                    b=tag_dict["color"]["blue"],
                ),
            )
            for tag_dict in tag_dicts
        ]
        return tags

    def get_num_frames(self):
        return len(self.frames)


RGB_TO_COLOR_NAME = {
    (0, 0, 0): "black",
    (254, 91, 89): "red",
    (247, 165, 71): "orange",
    (243, 206, 82): "yellow",
    (106, 205, 91): "green",
    (87, 185, 242): "blue",
    (209, 134, 223): "purple",
    (165, 165, 167): "gray",
}


def rgb_to_color_name(r, g, b) -> str:
    return RGB_TO_COLOR_NAME.get((r, g, b), (r, g, b))


def parse_data(data):
    head = Header(data)
    data_offset = Header.header_size
    frames = []
    layer_index = 0
    for i in range(head.num_frames):
        frame = Frame(data, data_offset)
        frames.append(frame)
        frame.chunks = []
        data_offset += frame.frame_size
        for c in range(frame.num_chunks):
            chunk = Chunk(data, data_offset)
            if chunk.chunk_type == 0x2004:
                layer = LayerChunk(data, layer_index, data_offset)
                if layer.layer_type & 1 == 1:
                    frame.chunks.append(LayerGroupChunk(layer))
                else:
                    frame.chunks.append(layer)
                layer_index += 1
            elif chunk.chunk_type == 0x2005:
                frame.chunks.append(CelChunk(data, data_offset))
            elif chunk.chunk_type == 0x2006:
                frame.chunks.append(CelExtraChunk(data, data_offset))
            elif chunk.chunk_type == 0x2016:
                frame.chunks.append(MaskChunk(data, data_offset))
            elif chunk.chunk_type == 0x0004:
                frame.chunks.append(OldPaleteChunk_0x0004(data, data_offset))
            elif chunk.chunk_type == 0x0011:
                frame.chunks.append(OldPaleteChunk_0x0011(data, data_offset))
            elif chunk.chunk_type == 0x2017:
                frame.chunks.append(PathChunk(data, data_offset))
            elif chunk.chunk_type == 0x2018:
                frame.chunks.append(FrameTagsChunk(data, data_offset))
            elif chunk.chunk_type == 0x2019:
                frame.chunks.append(PaletteChunk(data, data_offset))
            elif chunk.chunk_type == 0x2020:
                frame.chunks.append(UserDataChunk(data, data_offset))
            elif chunk.chunk_type == 0x2022:
                frame.chunks.append(SliceChunk(data, data_offset))
            else:
                print("Skipped 0x{:04x}".format(chunk.chunk_type))

            data_offset += chunk.chunk_size

    return head, frames
