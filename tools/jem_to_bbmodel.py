#!/usr/bin/env python3
"""
Turns an OptiFine .jem model into a .bbmodel you can open straight in Blockbench.

The texture is embedded in the file, so the .bbmodel is all you need: open it,
edit the texture in the paint tab, then save the image back over the pack's PNG.

    tools/jem_to_bbmodel.py <model.jem> [output.bbmodel]

The coordinate handling mirrors Blockbench's own JEM reader, so what you see is
what the pack actually renders: bone pivots are negated, nested pivots stack up
from their parent, and cubes inside a sub-bone are offset by that bone's pivot.
"""
import base64, json, sys, uuid
from pathlib import Path

FACES = ("north", "east", "south", "west", "up", "down")


def new_uuid():
    return str(uuid.uuid4())


class Converter:
    def __init__(self, jem_path):
        self.jem_path = Path(jem_path)
        self.model = json.loads(self.jem_path.read_text(encoding="utf-8"))
        self.elements = []
        self.outliner = []
        self.textures = []
        self.subcount = 0

    # ---------------------------------------------------------------- texture
    def resolve_texture(self, ref):
        """An OptiFine texture path is relative to the assets/<namespace> folder."""
        if not ref:
            return None
        parts = self.jem_path.resolve().parts
        if "optifine" in parts:
            root = Path(*parts[: parts.index("optifine")])
        else:
            root = self.jem_path.parent
        path = root / ref
        if path.suffix == "":
            path = path.with_suffix(".png")
        return path if path.is_file() else None

    def add_texture(self, ref):
        path = self.resolve_texture(ref)
        if path is None:
            return None
        size = self.model.get("textureSize", [16, 16])
        data = base64.b64encode(path.read_bytes()).decode("ascii")
        self.textures.append({
            "path": str(path),
            "name": path.name,
            "folder": "entity",
            "namespace": "minecraft",
            "id": str(len(self.textures)),
            "width": size[0],
            "height": size[1],
            "uv_width": size[0],
            "uv_height": size[1],
            "particle": False,
            "use_as_default": True,
            "render_mode": "default",
            "render_sides": "auto",
            "visible": True,
            "internal": True,
            "saved": False,
            "mode": "bitmap",
            "uuid": new_uuid(),
            "relative_path": ref,
            "source": "data:image/png;base64," + data,
        })
        return self.textures[-1]

    # ------------------------------------------------------------------ cubes
    def add_cube(self, box, group_name, offset):
        coords = box.get("coordinates")
        if coords:
            frm = [coords[i] + offset[i] for i in range(3)]
            to = [coords[i] + coords[i + 3] + offset[i] for i in range(3)]
        else:
            frm = to = [0, 0, 0]

        cube = {
            "name": box.get("name") or group_name,
            "box_uv": "textureOffset" in box,
            "rescale": False,
            "locked": False,
            "render_order": "default",
            "allow_mirror_modeling": True,
            "from": frm,
            "to": to,
            "autouv": 0,
            "color": 0,
            "origin": [0, 0, 0],
            "uv_offset": box.get("textureOffset", [0, 0]),
            "faces": {f: {"uv": [0, 0, 0, 0], "texture": 0} for f in FACES},
            "type": "cube",
            "uuid": new_uuid(),
        }
        if "sizeAdd" in box:
            cube["inflate"] = box["sizeAdd"]
        # Per-face UVs are used when the box does not carry a single offset.
        for face in FACES:
            key = "uv" + face.capitalize()
            if key in box:
                cube["box_uv"] = False
                cube["faces"][face]["uv"] = box[key]
        self.elements.append(cube)
        return cube["uuid"]

    # ------------------------------------------------------------------ bones
    def read_content(self, submodel, node, origin, depth, part_name, is_root_bone):
        children = []
        for box in submodel.get("boxes", []) or []:
            # Cubes sit in bone-local space; only sub-bones shift them.
            offset = [0, 0, 0] if is_root_bone else origin
            children.append(self.add_cube(box, node["name"], offset))

        for sub in submodel.get("submodels", []) or []:
            translate = list(sub.get("translate", [])) or None
            if depth >= 1 and translate:
                translate = [translate[i] + origin[i] for i in range(3)]
            if translate is None:
                translate = list(submodel.get("translate", [0, 0, 0])) if depth >= 1 else [0, 0, 0]

            name = sub.get("id") or sub.get("comment") or f"{part_name}_sub_{self.subcount}"
            self.subcount += 1
            group = {
                "name": name,
                "origin": translate,
                "rotation": sub.get("rotate", [0, 0, 0]),
                "color": 0,
                "uuid": new_uuid(),
                "export": True,
                "mirror_uv": bool(sub.get("mirrorTexture", "")) and "u" in sub.get("mirrorTexture", ""),
                "isOpen": True,
                "locked": False,
                "visibility": True,
                "autouv": 0,
                "children": [],
            }
            group["children"] = self.read_content(sub, group, translate, depth + 1, part_name, False)
            children.append(group)

        return children

    def convert(self):
        self.add_texture(self.model.get("texture"))
        for bone in self.model.get("models", []):
            if not isinstance(bone, dict):
                continue
            if self.textures == [] and bone.get("texture"):
                self.add_texture(bone["texture"])
            origin = [-v for v in bone.get("translate", [0, 0, 0])]
            group = {
                "name": bone.get("part") or bone.get("id") or "part",
                "origin": origin,
                "rotation": bone.get("rotate", [0, 0, 0]),
                "color": 0,
                "uuid": new_uuid(),
                "export": True,
                "mirror_uv": "u" in (bone.get("mirrorTexture") or ""),
                "isOpen": True,
                "locked": False,
                "visibility": True,
                "autouv": 0,
                "children": [],
            }
            group["children"] = self.read_content(
                bone, group, origin, 0, group["name"], is_root_bone=True)
            self.outliner.append(group)

        size = self.model.get("textureSize", [16, 16])
        return {
            "meta": {
                "format_version": "4.10",
                "model_format": "optifine_entity",
                "box_uv": True,
            },
            "name": self.jem_path.stem,
            "model_identifier": "",
            "visible_box": [1, 1, 0],
            "variable_placeholders": "",
            "variable_placeholder_buttons": [],
            "unhandled_root_fields": {},
            "resolution": {"width": size[0], "height": size[1]},
            "elements": self.elements,
            "outliner": self.outliner,
            "textures": self.textures,
        }


def main(argv):
    if len(argv) < 2:
        sys.exit(__doc__.strip())
    src = Path(argv[1])
    out = Path(argv[2]) if len(argv) > 2 else src.with_suffix(".bbmodel")
    project = Converter(src).convert()
    out.write_text(json.dumps(project, indent=2), encoding="utf-8")
    print(f"{out}  ({len(project['elements'])} cubes, "
          f"{len(project['textures'])} texture, "
          f"{project['resolution']['width']}x{project['resolution']['height']} UV)")


if __name__ == "__main__":
    main(sys.argv)
