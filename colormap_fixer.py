import json
import os
import shutil
from distutils.dir_util import copy_tree

from PIL import ImageOps, Image


class ColormapFixerError(Exception):
    def __init__(self, message: str):
        self.message = message

    def __str__(self):
        return self.message


class ColormapFixer:
    main_path = "assets/minecraft/"
    colormaps_path = main_path + "optifine/colormap/blocks/"
    block_textures_path = main_path + "textures/block/"
    ctm_path = main_path + "optifine/ctm/"
    model_path = main_path + "models/block/"

    color_prefix = [
        'yellow', 'white', 'red',
        'purple', 'pink', 'orange',
        'magenta', 'lime', 'light_gray',
        'light_blue', 'green', 'gray',
        'cyan', 'brown', 'blue', 'black'
    ]
    texture_placed_suffix = ["top", "side"]

    def _generate_color_hex_and_parents(self, texture_pack_path: str) -> \
            tuple[dict[str, dict[str, str]], list[str]]:
        color_hex: dict[str, dict[str, str]] = {}
        color_hex_parent: list[str] = []
        for property_file in os.listdir(f"{texture_pack_path}/{self.colormaps_path}"):
            if property_file.split(".")[1] != "properties":
                continue
            color, block_name = self._remove(self.color_prefix, property_file.split(".")[0])
            if not color or not block_name:
                continue
            if not block_name in color_hex_parent:
                color_hex_parent.append(block_name)
            with open(f"{texture_pack_path}/{self.colormaps_path}{property_file}", "r") as file:
                file_blocks_colored = []
                for line in file.readlines():
                    if line.startswith("blocks"):
                        file_blocks_colored = line.split("=")[1].split()
                    elif line.startswith("color"):
                        file_color = line.split("=")[1].rstrip()
                if not file_blocks_colored:
                    if not block_name in color_hex:
                        color_hex[block_name] = {}
                    color_hex[block_name].update({color: file_color})
                for file_block in file_blocks_colored:
                    file_block_name = self._remove(self.color_prefix, file_block)[1]
                    if not file_block_name in color_hex:
                        color_hex[file_block_name] = {}
                    color_hex[file_block_name].update({color: file_color})

        shutil.rmtree(f"{texture_pack_path}/{self.colormaps_path}")

        color_hex.update({'stained_glass_pane_top': color_hex['stained_glass_pane']})
        color_hex.update({'terracotta_top': color_hex['terracotta']})
        color_hex.update({'terracotta_side': color_hex['terracotta']})
        return color_hex, color_hex_parent

    def _recolor_textures(self, texture_pack_path: str, color_hex: dict[str, dict[str, str]],
                          color_hex_parents: list[str], *, recolor_ctm=True) -> None:
        for texture in os.listdir(f"{texture_pack_path}/{self.block_textures_path}"):
            name = texture.split(".")[0]
            if name not in color_hex:
                continue
            for color_name in color_hex[name]:
                color_name_hex = color_hex[name][color_name]

                self._recolor_image(f"{texture_pack_path}/{self.block_textures_path}{texture}", color_name_hex,
                                    f"{texture_pack_path}/{self.block_textures_path}{color_name}_{texture}")

                if not recolor_ctm or not os.path.isdir(f"{texture_pack_path}/{self.ctm_path}{name}"):
                    continue

                copy_tree(f"{texture_pack_path}/{self.ctm_path}{name}",
                          f"{texture_pack_path}/{self.ctm_path}{color_name}_{name}/")
                os.rename(f"{texture_pack_path}/{self.ctm_path}{color_name}_{name}/{name}.properties",
                          f"{texture_pack_path}/{self.ctm_path}{color_name}_{name}/{color_name}_{name}.properties")

                with open(f"{texture_pack_path}/{self.ctm_path}{color_name}_{name}/{color_name}_{name}.properties",
                          "r") as file:
                    lines = file.readlines()
                for count, line in enumerate(lines):
                    if line.startswith(("matchTiles=", "matchBlocks=")):
                        lines[count] = lines[count].replace(name, f"{color_name}_{name}")
                with open(f"{texture_pack_path}/{self.ctm_path}{color_name}_{name}/{color_name}_{name}.properties",
                          "w") as file:
                    file.writelines(lines)

                for ctm_texture in os.listdir(f"{texture_pack_path}/{self.ctm_path}{color_name}_{name}"):
                    if ctm_texture.split(".")[0].isdigit():
                        self._recolor_image(f"{texture_pack_path}/{self.ctm_path}{color_name}_{name}/{ctm_texture}",
                                            color_name_hex)

            if recolor_ctm:
                try:
                    shutil.rmtree(f"{texture_pack_path}/{self.ctm_path}{name}")
                except:
                    pass

    def _rewrite_model_properties(self, texture_pack_path: str, color_hex: dict[str, dict[str, str]]) -> None:
        for model in os.listdir(f"{texture_pack_path}/{self.model_path}"):
            if not model.startswith(tuple(self.color_prefix)) and not model.endswith(".json"):
                continue

            name = model.split(".")[0]
            color, _ = self._remove(self.color_prefix, name)

            if not color:
                continue

            with open(f"{texture_pack_path}/{self.model_path}{model}", "r") as file:
                json_context = json.loads("\n".join(file.readlines()))

            if len(json_context) == 1 and list(json_context.keys())[0] == "parent":
                location = f"{json_context['parent'].split('/')[1]}.json"
                with open(f"{texture_pack_path}/{self.model_path}{location}", 'r') as file:
                    json_context = json.loads("\n".join(file.readlines()))

            if "textures" not in json_context.keys():
                continue
            for texture in json_context["textures"]:
                block = json_context["textures"][texture].split("/")[1]
                if block in color_hex.keys():
                    json_context["textures"][texture] = json_context["textures"][texture].replace(
                        "block/" + block, f"block/{color}_{block}")

            with open(f"{texture_pack_path}/{self.model_path}{model}", "w") as file:
                file.writelines(json.dumps(json_context))

    @staticmethod
    def _remove(things_to_remove: list[str], string: str, space="_"):
        for thing in things_to_remove:
            if string[:len(thing + space)] == thing + space:
                # if thing_in_end:
                #     return string[-len(thing):], string[:-len(thing + space)]
                return string[:len(thing)], string[len(thing + space):]
        return None, None

    @staticmethod
    def _recolor_image(image_path, color, output_path=""):
        image = Image.open(image_path).convert("RGBA")
        alpha = image.getchannel('A')

        image = image.convert('L')
        output = ImageOps.colorize(image, black="black", white=f"#{color}")
        output.putalpha(alpha)

        output.save(output_path if output_path else image_path)

    def fix(self, texture_pack_path: str) -> None:
        if not os.path.isdir(f"{texture_pack_path}/{self.colormaps_path}"):
            raise ColormapFixerError("Colormaps not found. Texture pack seems to be already fixed or corrupted.")

        print("Generating color table... ", end="")
        color_hex, color_hex_parents = self._generate_color_hex_and_parents(texture_pack_path)
        print("done")

        if not color_hex:
            raise ColormapFixerError("Colormaps not found. Texture pack seems to be corrupted.")
        elif not os.path.isdir(f"{texture_pack_path}/{self.block_textures_path}"):
            raise ColormapFixerError("Block textures not found. Texture pack seems to be corrupted.")

        print("Recoloring textures... ", end="")

        self._recolor_textures(texture_pack_path, color_hex,
                               color_hex_parents, recolor_ctm=os.path.isdir(f"{texture_pack_path}/{self.ctm_path}"))

        print("done")
        print("Editing models to use new textures... ", end="")

        if not os.path.isdir(f"{texture_pack_path}/{self.model_path}"):
            raise ColormapFixerError("Models not found. Texture pack seems to be corrupted.")

        self._rewrite_model_properties(texture_pack_path, color_hex)
        print("done")
