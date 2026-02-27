from __future__ import annotations
from typing import TYPE_CHECKING


from dataclasses import dataclass
from collections.abc import Sequence

import matplotlib.image as mpimg

if TYPE_CHECKING:
    from matplotlib.lines import Line2D
    from matplotlib.text import Annotation
    from matplotlib.text import Text
    from matplotlib.image import AxesImage



from ..validation import Validators
from .. import constants
from . import FigureManager
from . import NumberManager


class ImageManager:
    """
    Manages the placement and storage of image overlays within the energy diagram.

    Supports two modes: standalone images placed at an explicit data-coordinate
    position, and image series where one image is placed per x-position with
    automatic collision avoidance against energy bars, number annotations, and
    x-axis labels. Series images are redrawn whenever number annotations change.
    All rendered artists are stored in ``mpl_objects`` for later access.
    """

    def __init__(
            self,
            figure_manager: FigureManager,
        ) -> None:
        self.figure_manager = figure_manager
        self.image_series_data = {}
        self.has_image_series = False
        self.solo_image_data = {}
        self.mpl_objects = {}

    def add_image_in_plot(
            self,
            img_path: str,
            position: tuple[float, float] | list[float],
            margins: dict[str, tuple],
            figsize: dict[str, tuple],
            img_name: str | None = None,
            width: float | None = None,
            height: float | None = None,
            framed: bool = False,
            frame_color: str = "black",
            horizontal_alignment: str = "center",
            vertical_alignment: str = "center",
        ) -> None:
        
        # Sanity checks
        Validators.validate_numeric_sequence(position, "position", required_length=2)
        if img_name is not None:
            if not isinstance(img_name, str):
                raise TypeError("img_series_name must be a string or None.")
        Validators.validate_number(width, "width", allow_none=True, min_value=0)
        Validators.validate_number(height, "height", allow_none=True, min_value=0)
        if not isinstance(framed, bool):
            raise TypeError("framed must be a bool.")
        
        # Construct the image
        img_object = self._construct_image(
            img_path=img_path,
            position=position,
            margins=margins,
            figsize=figsize,
            vertical_alignment=vertical_alignment,
            horizontal_alignment=horizontal_alignment,
            width=width,
            height=height,
            framed=framed,
            frame_color=frame_color,
        )

        #Save mpl objects
        if img_name is None:
            img_name = f"__Image_{len(self.mpl_objects)}"
        self.mpl_objects[img_name] = img_object

        # Save underlying data
        self.solo_image_data[img_name] = {
            "img_name": img_name,
            "img_path": img_path,
            "position": position,
            "width": width,
            "height": height,
            "framed": framed,
            "frame_color": frame_color,
            "horizontal_alignment": horizontal_alignment,
            "vertical_alignment": vertical_alignment,
        }

    def add_image_series_in_plot(
            self,
            img_paths: Sequence[str],
            margins: dict[str, tuple],
            figsize: dict[str, tuple],
            path_data: dict,
            number_mpl_objects: dict,
            xlabel_mpl_objects: dict,
            img_x_places: Sequence[float] | None = None,
            y_placement: Sequence[str] | str = "auto",
            y_offsets: Sequence[float] | float = 0,
            img_series_name: str | None = None,
            width: Sequence[float | None] | float | None = None,
            height: Sequence[float| None] | float | None = None,
            framed: Sequence[bool] | bool = False,
            frame_colors: Sequence[str] | str = "black",
        ) -> None:
        # Sanity checks
        Validators.validate_string_sequence(img_paths, "img_paths")
        Validators.validate_numeric_sequence(img_x_places, "img_places", allow_none=True)

        # Sanity checks y_placement
        ALLOWED_Y_PLACEMENT = ["top", "bottom", "auto"]
        if isinstance(y_placement, (list, tuple)):
            Validators.validate_string_sequence(y_placement, "y_placement")
            if len(img_paths) != len(y_placement):
                raise ValueError("There must be the same number of images and elements in y_placement.")
            
            for value in y_placement:
                if value not in ALLOWED_Y_PLACEMENT:
                    raise ValueError(f"All values of y_placement must be one of {ALLOWED_Y_PLACEMENT}.")
        else:
            if not y_placement in ALLOWED_Y_PLACEMENT:
                raise ValueError(f"y_placement must be one of {ALLOWED_Y_PLACEMENT}.")
            y_placement = [y_placement] * len(img_paths)

        # Sanity checks y_offsets
        if isinstance(y_offsets, Sequence):
            Validators.validate_numeric_sequence(y_offsets, "y_offsets")
            if len(img_paths) != len(y_offsets):
                raise ValueError("There must be the same number of images and elements in y_offsets.")
        else:
            if not isinstance(y_offsets, (int, float)):
                raise ValueError(f"y_offsets must be a float.")
            y_offsets = [y_offsets] * len(img_paths)

        # Sanity checks img_series_name
        if img_series_name is not None:
            if not isinstance(img_series_name, str):
                raise TypeError("img_series_name must be a string or None.")

        # Sanity checks img_x_places
        if img_x_places is not None:
            if len(img_paths) != len(img_x_places):
                raise ValueError("There must be the same number of images and img_x_places.")
        else:
            img_x_places = list(range(len(img_paths)))
        
        # Sanity checks height
        if isinstance(height, Sequence):
            Validators.validate_numeric_sequence(
                height, "height", allow_none_elements=True,
            )
            if len(img_paths) != len(height):
                raise ValueError("height must have the same length as img_paths.")
        elif isinstance(height, (int, float)):
            height = [height] * len(img_paths)
        elif height is None:
            height = [None] * len(img_paths)
        else:
            raise TypeError("height must be a Sequence, numeric value or None.")

        # Sanity checks width
        if isinstance(width, Sequence):
            Validators.validate_numeric_sequence(
                width, "width",allow_none_elements=True,
            )
            if len(img_paths) != len(width):
                raise ValueError("width must have the same length as img_paths.")
        elif isinstance(width, (int, float)):
            width = [width] * len(img_paths)
        elif width is None:
            # Only set width to default if no height value for same image
            width = [
                constants.STD_IMAGE_WIDTH if value is None 
                else None 
                for value in height
            ]
        else:
            raise TypeError("width must be a Sequence, numeric value or None.")
        
        # Sanity checks framed
        if isinstance(framed, (list, tuple)):
            if any([not isinstance(entry, bool) for entry in framed]):
                raise TypeError("Elements in framed must be a bool.")
            if len(framed) != len(height):
                raise ValueError("framed must have the same length as img_paths.")
        elif isinstance(framed, bool):
            framed = [framed] * len(img_paths)
        else:
            raise TypeError("framed must be a Sequence of bools, or a bool.")
        
        # Sanity checks frame colors
        if isinstance(frame_colors, (list, tuple)):
            if len(img_paths) != len(frame_colors):
                raise ValueError("frame_colors must have the same length as img_paths.")
        elif isinstance(frame_colors, str):
            frame_colors = [frame_colors] * len(img_paths)
        else:
            raise TypeError("frame_colors must be a Sequence, or a string")
        
        self.has_image_series = True
        # Print the image for each x
        series_mpl_objects = {}
        for index in range(len(img_paths)):
            x = img_x_places[index]

            # Avoid collision with plateaus
            diff_to_plateau = ImageManager._get_diff_plateau(margins, figsize)
            all_values_at_x = NumberManager._get_all_values_at_x(path_data, x)
            if all_values_at_x:
                y_min_top = max(all_values_at_x) + diff_to_plateau
                y_max_bottom = min(all_values_at_x) - diff_to_plateau
            else:
                print(f"Warning: No plateaus at x = {x}. Placing image at y = 0.")
                y_min_top = 0
                y_max_bottom = 0

            # Avoid collision with numbers
            for _, numbers in number_mpl_objects.items():
                try: 
                    number_fontsize = numbers[f"{x:.1f}"].get_fontsize()
                    number_y = numbers[f"{x:.1f}"].get_position()[1]
                    diff_to_number = ImageManager._get_diff_number(
                        margins, figsize, number_fontsize
                    )
                    if number_y + diff_to_number > y_min_top:
                        y_min_top = number_y + diff_to_number
                    if number_y - diff_to_number < y_max_bottom:
                        y_max_bottom = number_y - diff_to_number
                except KeyError:
                    pass
            
            # Avoid collision with label
            try:
                label_fontsize = xlabel_mpl_objects[f"{x:.1f}"].get_fontsize()
                label_y = xlabel_mpl_objects[f"{x:.1f}"].get_position()[1]
                diff_to_label = ImageManager._get_diff_label(
                    margins, figsize, label_fontsize
                )
                if label_y + diff_to_label > y_min_top:
                    y_min_top = label_y + diff_to_label
                if label_y - diff_to_label < y_max_bottom:
                    y_max_bottom = label_y - diff_to_label
            except KeyError:
                pass

            # Determine current vertival alignment and position
            if y_placement[index] == "auto":
                space_on_top = margins["y"][1] - y_min_top
                space_on_bottom = y_max_bottom - margins["y"][0]
                if space_on_top > space_on_bottom:
                    vertical_alignment_current = "bottom"
                    position_current = (x, y_min_top + y_offsets[index])
                else:
                    vertical_alignment_current = "top"
                    position_current = (x, y_max_bottom - y_offsets[index])
            elif y_placement[index] == "top":
                vertical_alignment_current = "bottom"
                position_current = (x, y_min_top + y_offsets[index])
            elif y_placement[index] == "bottom":
                vertical_alignment_current = "top"
                position_current = (x, y_max_bottom - y_offsets[index])

            # Construct the image
            img_object = self._construct_image(
                img_path=img_paths[index],
                position=position_current,
                margins=margins,
                figsize=figsize,
                vertical_alignment=vertical_alignment_current,
                width=width[index],
                height=height[index],
                framed=framed[index],
                frame_color=frame_colors[index]
            )

            series_mpl_objects[f"{x:.1f}"] = img_object

        #Save mpl objects
        if img_series_name is None:
            img_series_name = f"__Series_{len(self.mpl_objects)}"
        self.mpl_objects[img_series_name] = series_mpl_objects

        # Save underlying data if redrawing is neccesary
        self.image_series_data[img_series_name] = {
            "img_series_name": img_series_name,
            "img_paths": img_paths,
            "img_x_places": img_x_places,
            "y_placement": y_placement,
            "y_offsets": y_offsets,
            "width": width,
            "height": height,
            "framed": framed,
            "frame_colors": frame_colors,
        }

    def reset_image_series(
            self,
            margins: dict[str, tuple],
            figsize: dict[str, tuple],
            path_data: dict,
            number_mpl_objects: dict,
            xlabel_mpl_objects: dict, 
        ) -> None:
        # Series images are removed and redrawn; standalone images are permanent
        self._remove_image_series()
        for _, image_series in self.image_series_data.items():
            self.add_image_series_in_plot(
                margins=margins,
                figsize=figsize,
                path_data=path_data,
                number_mpl_objects=number_mpl_objects,
                xlabel_mpl_objects=xlabel_mpl_objects,
                **image_series,
            )

    ############################################################
    # Internal helper methods
    ############################################################

    def _remove_image_series(self) -> None:
        for _, series in self.mpl_objects.items():
            if isinstance(series, dict):
                for __, image in series.items():
                    image.remove()

    def _construct_image(
            self,
            img_path: str,
            position: tuple[float, float] | list[float],
            margins: dict[str, tuple],
            figsize: dict[str, tuple],
            vertical_alignment: str = "bottom",
            horizontal_alignment: str = "center",
            width: float | None = None,
            height: float | None = None,
            framed: bool = False,
            frame_color: str = "black",
        ) -> ImageObject:
        def draw_frame_part(x_coords, y_coords):
            return self.figure_manager.ax.plot(
                        x_coords, y_coords, 
                        zorder=0.5, 
                        ls='-', 
                        lw=0.5, 
                        color=frame_color
                     )[0]
        # Sanity checks
        Validators.validate_numeric_sequence(
            position, "position", required_length=2
        )
        Validators.validate_number(
            width, "width", allow_none=True, min_value=0
        )
        Validators.validate_number(
            height, "height", allow_none=True, min_value=0
        )

        ALLOWED_VA_VALUES = ["top", "bottom", "center"]
        if vertical_alignment not in ALLOWED_VA_VALUES:
            raise ValueError(f"vertical_alignment must be in {ALLOWED_VA_VALUES}.")
        ALLOWED_HA_VALUES = ["left", "center", "right"]
        if horizontal_alignment not in ALLOWED_HA_VALUES:
            raise ValueError(f"horizontal alignment must be in {ALLOWED_HA_VALUES}")

        # Read and scale image
        img_file = mpimg.imread(img_path)
        positimg_height_px = img_file.shape[0]
        img_width_px = img_file.shape[1]
        if width is None and height is None:
            width = constants.STD_IMAGE_WIDTH
            height = (width 
                    * positimg_height_px / img_width_px
                    * (margins["y"][1] - margins["y"][0])
                    / (margins["x"][1] - margins["x"][0])
                    * figsize[0] / figsize[1]
                    )
        elif width is None:
            width = (height 
                    * img_width_px / positimg_height_px
                    / (margins["y"][1] - margins["y"][0])
                    * (margins["x"][1] - margins["x"][0])
                    / figsize[0] * figsize[1]
                    )
        elif height is None:
            height = (width 
                    * positimg_height_px / img_width_px
                    * (margins["y"][1] - margins["y"][0])
                    / (margins["x"][1] - margins["x"][0])
                    * figsize[0] / figsize[1]
                    )
            
        if horizontal_alignment == "center":
            img_x_extent = [
                position[0] - width / 2, 
                position[0] + width / 2,
            ]
        elif horizontal_alignment == "left":
            img_x_extent = [
                position[0], 
                position[0] + width,
            ]
        elif horizontal_alignment == "right":
            img_x_extent = [
                position[0] - width, 
                position[0],
            ]

        if vertical_alignment == "bottom":
            img_y_extent = [
                    position[1],
                    position[1] + height,
                ]
        elif vertical_alignment == "top":
            img_y_extent = [
                    position[1] - height,
                    position[1],
                ]
        elif vertical_alignment == "center":
            img_y_extent = [
                    position[1] - height / 2,
                    position[1] + height / 2,
                ]

        img_extent = img_x_extent + img_y_extent

        # Draw image
        img_artist = self.figure_manager.ax.imshow(
            img_file,
            extent=img_extent,
            interpolation="bilinear", #nearest/bilinear/bicubic (nearest ugly)
            aspect="auto",
        )

        # Draw borders
        border_objects = {}
        if framed:
            border_objects["top"] = draw_frame_part(
                (img_extent[0], img_extent[1]),
                (img_extent[3], img_extent[3])
            )
            border_objects["bottom"] = draw_frame_part(
                (img_extent[0], img_extent[1]),
                (img_extent[2], img_extent[2])
            )
            border_objects["left"] = draw_frame_part(
                (img_extent[0], img_extent[0]),
                (img_extent[2], img_extent[3])
            )
            border_objects["right"] = draw_frame_part(
                (img_extent[1], img_extent[1]),
                (img_extent[2], img_extent[3])
            )
        return ImageObject(img_artist, border_objects)
        
    @staticmethod
    def _get_diff_plateau(
            margins: dict[str, tuple], 
            figsize: tuple[float, float],
        ) -> float:
        diff_to_plateau = (
            (margins["y"][1] - margins["y"][0])
            / figsize[1] 
            * constants.DISTANCE_IMAGE_LINE
        )
        return diff_to_plateau

    @staticmethod
    def _get_diff_number(
            margins: dict[str, tuple], 
            figsize: tuple[float, float],
            fontsize
        ) -> float:
        diff_to_number = (
            (fontsize / constants.STD_FONTSIZE)
            * (margins["y"][1] - margins["y"][0])
            / figsize[1] 
            * constants.DISTANCE_NUMBER_LINE
        )
        return diff_to_number
    
    @staticmethod
    def _get_diff_label(
            margins: dict[str, tuple], 
            figsize: tuple[float, float],
            fontsize
        ) -> float:
        diff_to_label = (
            (fontsize / constants.STD_FONTSIZE)
            * (margins["y"][1] - margins["y"][0])
            / figsize[1] 
            * constants.DISTANCE_IMAGE_LABEL
        )
        return diff_to_label



@dataclass
class ImageObject:
    """
    Container for the Matplotlib artists that make up a single diagram image.

    Attributes
    ----------
    image : AxesImage
        The rendered image artist.
    borders : dict of str to Line2D
        Frame border lines keyed by side (``"top"``, ``"bottom"``, ``"left"``,
        ``"right"``). Empty when ``framed=False``.
    """
    image: AxesImage
    borders: dict[str, Line2D]

    def remove(self):
        self.image.remove()
        for _, border in self.borders.items():
            border.remove()

    def remove_frame(self):
        for _, border in self.borders.items():
            border.remove()
        self.borders = {}



