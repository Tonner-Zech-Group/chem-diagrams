# Examples

This page provides 9 examples of how to use the features of chemdiagrams.

## Example 1: Merging plateaus, x-axis breaks and images in plot

```python
from chemdiagrams import EnergyDiagram
import os.path

penguin = os.path.join("figures", "penguin.png")
penguin_TS = os.path.join("figures", "penguin_TS.png")
penguin_II = os.path.join("figures", "penguin_2.png")
untitled = os.path.join("figures", "untitled.jpeg")

dia = EnergyDiagram(
    style="twosided",
    extra_y_margin=(0, 0.25),
)

dia.draw_path(
    [0,1,2], [-32, 18, 0], "blue",
    path_name="Blue path",   
)

dia.draw_path(
    [2,3,4], [0, 25, -42], "red",
    path_name="Red path",
)

dia.draw_difference_bar(
    2, (-32, -42),
    r"$\Delta E_\mathrm{R}$: ",
    left_side=True,
    x_whiskers=(0,4),
    whiskercolor="red"
)
dia.bars[0].whisker_1.set_color("blue")

dia.add_image_series_in_plot(
    [penguin_II, penguin_TS, penguin, penguin_TS, penguin_II],
    y_placement="top",
    y_offsets=2
)

dia.add_numbers_average(color="black")
dia.merge_plateaus(2, "Blue path", "Red path")
dia.add_xaxis_break(2)
dia.set_xlabels(["P1", "TS1", "E", "TS2", "P2"])
dia.ax.set_ylabel(r"$\Delta E$ in kJ mol$^{-1}$", fontsize=8)
dia.legend(fontsize=5)
dia.ax.set_title("Penguin Reaction", fontsize=10)

dia.fig.savefig(os.path.join("..", "docs", "img", "title", "image_1.png"), dpi=300, bbox_inches="tight")
dia.show()
```

![Diagram 1](https://raw.githubusercontent.com/Tonner-Zech-Group/chem-diagrams/main/docs/img/title/image_1.png)

## Example 2: Multiple paths

```python
from chemdiagrams import EnergyDiagram
import os.path

dia = EnergyDiagram()

dia.draw_path(
    [0,1,2,3,4], [0, 32, 5, 25, -15], "blue",
    path_name="Blue path",
    linetypes=2
)

dia.draw_path(
    [0,1,2,3,4], [0, 26, 6, 15, -18], "red",
    path_name="Red path",
    linetypes=2
)

dia.draw_path(
    [0,1,4], [0, 12, -32], "green",
    path_name="Green path",
    linetypes=[2,1]
)

dia.draw_path(
    [0,1,2,3,4], [0, 20, 8, 12, -20], "orange",
    path_name="Orange path",
    linetypes=2
)


dia.add_numbers_auto()

dia.legend(fontsize=5)
dia.set_xlabels(["Educt", "Transition\nState 1", "Intermediate", "Transition\nState 2", "Product"], weight="normal", fontsize=6)
dia.ax.set_ylabel(r"$\Delta E$ in kJ mol$^{-1}$", fontsize=8)

dia.fig.savefig(os.path.join("..", "docs", "img", "title", "image_2.png"), dpi=300, bbox_inches="tight")
dia.show()
```
![Diagram 2](https://raw.githubusercontent.com/Tonner-Zech-Group/chem-diagrams/main/docs/img/title/image_2.png)

## Example 3: Customization of one state

```python
from chemdiagrams import EnergyDiagram
import os.path

dia = EnergyDiagram(style="boxed")

dia.draw_path(
    [0,1,2,3,4], [0, 32, 5, 25, -15], "blue",
    path_name="Blue path",
    linetypes=[1,1,1,-1]
)
dia.add_path_labels("Blue path", [None, None, "Important\nIntermediate", None, None], color="red", fontsize=6)

dia.add_numbers_auto()
dia.lines["Blue path"].plateaus["2.0"].set_color("red")
dia.numbers["Blue path"]["2.0"].set_color("red")

dia.draw_difference_bar(
    1, 
    (0, 5), 
    r"$\Delta E_\mathrm{R,1}$", 
    left_side=True, 
    x_whiskers=(0,2), 
    whiskercolor="blue", 
    add_difference=False
)
dia.bars[0].whisker_2.set_color("red")

dia.draw_difference_bar(
    3, 
    (5, -15), 
    r"$\Delta E_\mathrm{R,2}$", 
    left_side=True, 
    x_whiskers=(2,4), 
    whiskercolor="blue", 
    add_difference=False
)
dia.bars[1].whisker_1.set_color("red")


dia.set_xlabels(["E", "TS1", "I", "TS2", "P"])
dia.ax.set_ylabel(r"$\Delta E$ in kJ mol$^{-1}$", fontsize=8)

dia.fig.savefig(os.path.join("..", "docs", "img", "title", "image_3.png"), dpi=300, bbox_inches="tight")
dia.show()
```
![Diagram 3](https://raw.githubusercontent.com/Tonner-Zech-Group/chem-diagrams/main/docs/img/title/image_3.png)

## Example 4: Images in plot

```python
from chemdiagrams import EnergyDiagram
import os.path

ester_1 = os.path.join("figures", "ester_1.png")
ester_2 = os.path.join("figures", "ester_2.png")
ester_3 = os.path.join("figures", "ester_3.png")
ester_4 = os.path.join("figures", "ester_4.png")
ester_5 = os.path.join("figures", "ester_5.png")

dia = EnergyDiagram(
    style="borderless",
    extra_y_margin=(0, 0.25),
)

dia.draw_path(
    [0,1,2,3,4], [0, 32, 5, 25, -15], "blue",
    path_name="Blue path",
    linetypes=3   
)

dia.add_numbers_average(color="black")
dia.set_xlabels(["Ester", "TS1", "Hemiacetal", "TS2", "Carboxylic\nAcid"], in_plot=True, fontsize=6, weight="normal")

dia.add_image_series_in_plot(
    [ester_1, ester_2, ester_3, ester_4, ester_5],
    y_placement="top",
    width=[0.6, 0.7, 0.6, 0.7, 0.6],
    y_offsets=1.5,
    framed=[True, False, False, False, True],
    frame_colors="blue"
)

dia.ax.set_title("Ester hydrolysis", fontsize=10)
dia.fig.savefig(os.path.join("..", "docs", "img", "title", "image_4.png"), dpi=300, bbox_inches="tight")
dia.fig.savefig(os.path.join("..","docs","img","example_image_series.png"),format="png", bbox_inches="tight")
dia.show()
```
![Diagram 4](https://raw.githubusercontent.com/Tonner-Zech-Group/chem-diagrams/main/docs/img/title/image_4.png)

## Example 5: Path labels

```python
from chemdiagrams import EnergyDiagram
import os.path

dia = EnergyDiagram()

dia.draw_path(
    [0,1,2,3], [0, 18, 12, 26], "blue",
    path_name="Blue path",
    linetypes=[4,4,3]
)

dia.add_path_labels("Blue path", [None, "TS", "P", "P2"])

dia.draw_path(
    [0,1,2,3], [0, 7, -10, -5], "red",
    path_name="Red path",
    linetypes=[4,4,3]
)

dia.add_path_labels("Red path", ["E", "TS", "P", "P2"])
dia.lines["Red path"].labels["0.0"].set_color("black")

dia.add_numbers_auto(x_min_max=(1,3))
dia.add_numbers_average(color="black", x_min_max=0)

dia.legend(fontsize=5)
dia.ax.set_ylabel(r"$\Delta E$ in kJ mol$^{-1}$", fontsize=8)

dia.fig.savefig(os.path.join("..", "docs", "img", "title", "image_5.png"), dpi=300, bbox_inches="tight")
dia.show()
```
![Diagram 5](https://raw.githubusercontent.com/Tonner-Zech-Group/chem-diagrams/main/docs/img/title/image_5.png)

## Example 6: Difference bar customization

```python
from chemdiagrams import EnergyDiagram
import os.path

dia = EnergyDiagram(extra_x_margin=[0,0.5])

dia.draw_path(
    [0, 2], [3, 18], "blue",
    path_name="Blue states",
    linetypes=0
)

dia.add_path_labels("Blue states", ["S1", "S1"])

dia.draw_path(
    [0, 2], [-5, -12], "red",
    path_name="Red states",
    linetypes=0
)

dia.add_path_labels("Red states", ["S2", "S2"])

dia.draw_difference_bar(
    0.8, 
    (3, 18), 
    r"$\Delta E_\mathrm{R1}$: ",
    color="blue",  
    x_whiskers=(0,2),  
    arrowstyle="<->"
)

dia.draw_difference_bar(
    0.8, 
    (-5, -12), 
    r"$\Delta E_\mathrm{R2}$: ",
    color="red",  
    x_whiskers=(0,2), 
    arrowstyle="<->"
)

dia.draw_difference_bar(
    2.8, 
    (-12, 18), 
    r"$\Delta E_\mathrm{P}$: ",
    left_side=True,
    color="black",  
    x_whiskers=(2,2), 
    arrowstyle="<->",
    whiskercolor="blue"
)
dia.bars[2].whisker_1.set_color("red")

dia.add_numbers_auto()

dia.set_xlabels(["Educt\nStates", "Product\nStates"], labelplaces=[0,2], fontsize=6, weight="normal")
dia.ax.set_ylabel(r"$\Delta E$ in kJ mol$^{-1}$", fontsize=8)
dia.legend(fontsize=5)
dia.ax_objects.axes["x_axis"].set_visible(False)

dia.fig.savefig(os.path.join("..", "docs", "img", "title", "image_6.png"), dpi=300, bbox_inches="tight")
dia.show()
```
![Diagram 6](https://raw.githubusercontent.com/Tonner-Zech-Group/chem-diagrams/main/docs/img/title/image_6.png)

## Example 7: Smooth paths, number modification

```python
from chemdiagrams import EnergyDiagram

dia = EnergyDiagram(style="halfboxed")

dia.draw_path(
    [0, 2, 4], [0, 78, -20], "blue",
    path_name="No catalyst",
    linetypes=4,
    width_plateau=0,
)

dia.draw_path(
    [0,1.2 ,1.8, 2.5, 4], [0, 32, 24, 38, -20], "red",
    path_name="With catalyst",
    linetypes=4,
    width_plateau=0,
)

dia.add_numbers_auto()

dia.modify_number_values(
    2, 
    x_add=2, 
    x_subtract=0,
    include_paths=["No catalyst"],
    brackets=("[", "]"), 
)

dia.modify_number_values(
    1.2, 
    x_add=1.2, 
    x_subtract=0,
    include_paths=["With catalyst"],
    brackets=("[", "]"), 
)

dia.modify_number_values(
    2.5, 
    x_add=2.5, 
    x_subtract=1.8,
    include_paths=["With catalyst"],
    brackets=("[", "]"), 
)

dia.ax.set_xlabel("Reaction Coordinate", fontsize=8)
dia.ax.set_ylabel(r"$\Delta E$ in kJ mol$^{-1}$", fontsize=8)

dia.legend(fontsize=5)
dia.fig.savefig(os.path.join("..", "docs", "img", "title", "image_7.png"), dpi=300, bbox_inches="tight")
dia.show()
```
![Diagram 7](https://raw.githubusercontent.com/Tonner-Zech-Group/chem-diagrams/main/docs/img/title/image_7.png)

## Example 8: Float energy values and image in plot

```python
from chemdiagrams import EnergyDiagram
import os.path

dia = EnergyDiagram(style="open")

penguin = os.path.join("figures", "penguin.png")

dia.draw_path(
    [0, 1, 2, 3, 4], [0, 0.154, -0.382, -0.287, -0.748], "black",
)

dia.add_numbers_auto(
    n_decimals=2
)

dia.ax.set_ylabel(r"$\Delta E$ in eV", fontsize=8)
dia.set_xlabels(["E", "TS1", "I", "TS2", "P"], in_plot=True)

dia.add_image_in_plot(
    penguin,
    position=(0.6, -0.4),
    height=0.4
)

dia.fig.savefig(os.path.join("..", "docs", "img", "title", "image_8.png"), dpi=300, bbox_inches="tight")
dia.fig.savefig(os.path.join("..","docs","img","example_single_image.png"),format="png", bbox_inches="tight")
dia.show()
```
![Diagram 8](https://raw.githubusercontent.com/Tonner-Zech-Group/chem-diagrams/main/docs/img/title/image_8.png)

## Example 9: Connector line customization and number modification

```python
from chemdiagrams import EnergyDiagram
import os.path

dia = EnergyDiagram()
dia.set_diagram_style("borderless")

dia.draw_path(
    [0,1,2,3,4,5,6], [0, 67, 42, 87, 15, 38, -20], "blue",
    path_name="Blue path",
    linetypes=2   
)

dia.draw_path(
    [0,1,2,3,4,5,6], [0, 37, 15, 23, -29, -12, -45], "red",
    path_name="Red path",
    linetypes=2   
)

dia.add_numbers_auto()
dia.add_path_labels("Blue path", ["E", "TS1", "I", "TS2", "I2", "TS3", "P"], color="black", fontsize=6)
dia.add_path_labels("Red path", [None, "TS1", "I", "TS2", "I2", "TS3", "P"], color="black", fontsize=6)

dia.modify_number_values(
    x=1,
    x_add=1,
    x_subtract=0
)

dia.modify_number_values(
    x=3,
    x_add=3,
    x_subtract=2
)

dia.modify_number_values(
    x=5,
    x_add=5,
    x_subtract=4
)

for path in dia.lines.values():
    for connector in path.connections.values():
        connector.set_lw(0.5)

dia.legend(fontsize=6)

dia.fig.savefig(os.path.join("..", "docs", "img", "title", "image_9.png"), dpi=300, bbox_inches="tight")
dia.show()
```
![Diagram 9](https://raw.githubusercontent.com/Tonner-Zech-Group/chem-diagrams/main/docs/img/title/image_9.png)