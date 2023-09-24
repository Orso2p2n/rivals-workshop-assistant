from rivals_workshop_assistant.aseprite_handling._aseprite_loading.chunks import (LayerChunk,CelChunk)
from rivals_workshop_assistant.aseprite_handling._aseprite_loading.headers import (Frame)
from rivals_workshop_assistant.aseprite_handling.anims import Anim

from enum import Enum

class HitboxShape(Enum):
    CIRCLE = 0
    RECTANGLE = 1
    ROUNDED_RECTANGLE = 2

class Hitbox:
    def __init__(self, start: int, end: int, x: int, y: int, width: int, height: int, shape: HitboxShape):
        self.start = start
        self.end = end
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.shape = shape

    def from_layer(anim: Anim, layer: LayerChunk, frames: [Frame]):
        hitboxes: [Hitbox] = []

        cels_in_layer = []
        for i in range(len(frames)):
            frame = frames[i]
            for chunk in frame.chunks:
                if isinstance(chunk, CelChunk) and chunk.layer_index == layer.layer_index:
                    chunk.frame = frame
                    cels_in_layer.append({"frame_index": i, "cel_chunk": chunk})

        print(cels_in_layer)

        skip = 0

        for i in range(len(cels_in_layer)):
            if skip > 0:
                skip -= 1
                continue

            cel_in_layer = cels_in_layer[i]

            frame_index = cel_in_layer.get("frame_index")
            cel_chunk = cel_in_layer.get("cel_chunk")

            if frame_index < anim.start or frame_index > anim.end:
                continue
            
            shape = HitboxShape.CIRCLE
            if layer.name.startswith("HITBOX_R"):
                shape = HitboxShape.RECTANGLE
            elif layer.name.startswith("HITBOX_RC"):
                shape = HitboxShape.ROUNDED_RECTANGLE

            start = frame_index
            end = start

            x = cel_chunk.x_pos
            y = cel_chunk.y_pos
            width = cel_chunk.data.get("width")
            height = cel_chunk.data.get("height")
            
            index_offset = 1

            if i + index_offset < len(cels_in_layer):
                next_cel_in_layer = cels_in_layer[i + index_offset]

                next_frame_index = next_cel_in_layer.get("frame_index")
                next_cel_chunk = next_cel_in_layer.get("cel_chunk")

                while (
                    next_frame_index == frame_index + index_offset
                    and next_cel_chunk.x_pos == x
                    and next_cel_chunk.y_pos == y
                    and next_cel_chunk.data.get("width") == width
                    and next_cel_chunk.data.get("height") == height):
                        
                        end += 1

                        index_offset += 1
                        if i + index_offset >= len(cels_in_layer):
                            break
                        
                        next_cel_in_layer = cels_in_layer[i + index_offset]

                        next_frame_index = next_cel_in_layer.get("frame_index")
                        next_cel_chunk = next_cel_in_layer.get("cel_chunk")

                skip = index_offset - 1

            hitbox = Hitbox(start, end, x, y, width, height, shape)
            hitboxes.append(hitbox)

        return hitboxes
