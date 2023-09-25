from rivals_workshop_assistant.aseprite_handling._aseprite_loading.chunks import (LayerChunk,CelChunk)
from rivals_workshop_assistant.aseprite_handling._aseprite_loading.headers import (Frame)
from rivals_workshop_assistant.aseprite_handling.anims import Anim

import math

class Trackpoint:
    def __init__(self, anim: Anim, name: str, frame: int, x: int, y: int, width: int, height: int):
        self.anim = anim
        self.name = name
        self.frame = frame
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        
        self.init_gml()

    def init_gml(self):
        self.gml = "{" + f"frame: {self.frame}, x: {self.x} - sprite_get_xoffset(sprite_get(\"{self.anim.name}\")), y: {self.y} - sprite_get_xoffset(sprite_get(\"{self.anim.name}\")), width: {self.width}, height: {self.height}" + "}"

    def from_layer(anim: Anim, layer: LayerChunk, frames: [Frame]):
        trackpoints: [Trackpoint] = []

        cels_in_layer = []
        for i in range(len(frames)):
            frame = frames[i]
            for chunk in frame.chunks:
                if isinstance(chunk, CelChunk) and chunk.layer_index == layer.layer_index:
                    chunk.frame = frame
                    cels_in_layer.append({"frame_index": i, "cel_chunk": chunk})

        for cel_in_layer in cels_in_layer:
            frame_index = cel_in_layer.get("frame_index")
            cel_chunk = cel_in_layer.get("cel_chunk")

            if frame_index < anim.start or frame_index > anim.end:
                continue

            rel_frame = frame_index - anim.start

            width = cel_chunk.data.get("width")
            height = cel_chunk.data.get("height")
            x = cel_chunk.x_pos + math.floor(width/2)
            y = cel_chunk.y_pos + math.floor(height/2)

            name = layer.name.strip("TRACK").strip()

            trackpoint = Trackpoint(anim, name, rel_frame, x, y, width, height)
            trackpoints.append(trackpoint)

        return trackpoints
