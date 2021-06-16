# FATES Visualization Tool Documentation

# Reading in Files

All visualization functions in the toolbox take in FATES output files in the Files class object, so that output files only need to be read in once to create any visualization. Restart files, a parameter file, and a history file can be passed in at the same time.

class **`Files`(rest_folder=None, param_path=None, hist_path=None, address="relative")**

`rest_folder` folder path for restart files, the folder must only contain restart files

`param_path` file path to parameter file. If a restart path is passed in, it must be accompanied by a parameter path

`hist_path` file path to history file

`address` ("relative" or "absolute") format of paths

Here is an example using relative paths

```python
from files import *
#restart files need to be in a folder by themselves
restart_path = "sample_data/restart"
param_path = "sample_data/sample_param"
hist_path = "sample_data/sample_hist"

files = Files(restart_path, param_path, hist_path)
```

# Treemap

Treemaps capture both patch-level(patch age and area) and cohort-level(crown area, cohort height, pft, canopy layer, dbh, and number of trees in a cohort) statistics. The user has the option to create treemaps of a particular year, or a gif of treemaps of multiple years. 

## Single-Year Treemap

**`treemap`(files, year, mode="basic", path=None, name=None)**

`files` an instance of the Files object

`year` year number starting with year 1

`path` the relative path where the figure is saved, if not passed in, the figure will not be saved (if plotting in a notebook the plot will show and not be saved if no path is passed in)

`name` the name the figure is saved as (default is year number)

Here are the three modes of treemaps:

```python
from treemap import *
treemap(files, year=1, mode="basic", path="example_plots", name="basic_treemap")
```

![FATES%20Visualization%20Tool%20Documentation%20ca920971efbc429594247cf2b1d63cb2/basic_treemap.png](FATES%20Visualization%20Tool%20Documentation%20ca920971efbc429594247cf2b1d63cb2/basic_treemap.png)

```python
treemap(files, year=1, mode="patch simplified", path="example_plots", 
					name="patch_treemap")
```

![FATES%20Visualization%20Tool%20Documentation%20ca920971efbc429594247cf2b1d63cb2/patch_treemap.png](FATES%20Visualization%20Tool%20Documentation%20ca920971efbc429594247cf2b1d63cb2/patch_treemap.png)

```python
treemap(files, year=1, mode="one patch", path="example_plots", 
					name="one_treemap")
```

![FATES%20Visualization%20Tool%20Documentation%20ca920971efbc429594247cf2b1d63cb2/one_treemap.png](FATES%20Visualization%20Tool%20Documentation%20ca920971efbc429594247cf2b1d63cb2/one_treemap.png)

## Animated Treemap

The function to generate animated treemaps is quite similar to plotting a single-year treemap:

**`animate_treemap`(files, mode="basic", path="", file_name="animated treemap",
save_individuals=False, folder_name="individuals")**

`files` an instance of the Files object

`mode` type of treemap plotted. The tool supports 3 types of treemaps:

- "basic": everything is plotted the same as the original data, except small areas are aggregated to be visible in the visualization
- "patch simplified": cohorts in each patch are aggregated by pft and size classes, with the median of height and dbh, and the canopy area and number of plants added.
- "one patch": the simplified patches are aggregated and plotted together

`path` the relative path to which the animated plot is saved

`file_name` the filename of the animated plot

`save_individuals` During the process of generating the animated plot, treemaps of individual years will be temporarily saved in a folder in the path specified. After the plot is finished, the folder will be deleted by default unless specified in this argument

`folder_name` if choosing to save individual plots, the folder name where the plots are saved can be specified

An example of generating animated treemaps:

```python
from treemap import *
animate_treemap(files, mode="one patch", path="example_plots", 
								file_name="example_animated_treemap")
```

![FATES%20Visualization%20Tool%20Documentation%20ca920971efbc429594247cf2b1d63cb2/example_animated_treemap.gif](FATES%20Visualization%20Tool%20Documentation%20ca920971efbc429594247cf2b1d63cb2/example_animated_treemap.gif)

# Sunburst Matrix

A sunburst matrix is a good way to visualize the proportions of each category of a feature relative to the total amount and draw comparisons across different simulation parameters. For example, we can visualize the ratio of the number of understory and canopy Ponderosa and Cedar trees in a simulation.

**`sunburst_matrix`(files, var_dict, pfts, file_name, mode="gif", path="", save_individuals=False, folder_name="individuals")**

`files` matrix of tuples of run name and instances of the File object, tuples are in
the form `(run_name, File_object)`. The position of each sunburst plot corresponds to the position of the file object in the matrix passed in

`var_dict` a dictionary of variable names to be plotted in the format of `{label: variable_name}`. `label` is what will be on the sunburst plot

`pfts` a list of names of pfts

`file_name` the filename of the animated plot

`mode` type of sunburst matrix plotted. The tool supports 2 types of plots:

- "gif": the default option. Generates a gif file of animated sunburst matrix
- "interactive": generates an html file of the compiled plots with a slider that allows year selection

`path` the relative path to which the animated plot is saved

`save_individuals` During the process of generating the animated plot, plots of individual years will be temporarily saved in a folder in the path specified. After the plot is finished, the folder will be deleted by default unless specified in this argument

`folder_name` if choosing to save individual plots, the folder name where the plots are saved can be specified

Hypothetically, the sunburst_matrix function allows an infinite number of plots, features, and pfts. However, in practice, the number of plots, features, and pfts should be kept low to avoid overcrowding of the plot. Here is an example of a two-item matrix:

```python
from sunburst_matrix import *
files = [[("test1", files)],
					[("test2", files)]]
var = {"understory": "NPLANT_UNDERSTORY_SCPF", "canopy": "NPLANT_CANOPY_SCPF"}
pfts = ["Pine", "Cedar"]

sunburst_matrix(files, var_dict=var, 
                pfts=pfts, file_name="animated_matrix", mode="gif", 
								path="example_plots")
```

![FATES%20Visualization%20Tool%20Documentation%20ca920971efbc429594247cf2b1d63cb2/animated_matrix.gif](FATES%20Visualization%20Tool%20Documentation%20ca920971efbc429594247cf2b1d63cb2/animated_matrix.gif)

Here is an example of an interactive sunburst matrix:

```python
sunburst_matrix(files, var_dict=var, 
                pfts=pfts, file_name="interactive_matrix", mode="interactive", 
								path="example_plots")
```

![FATES%20Visualization%20Tool%20Documentation%20ca920971efbc429594247cf2b1d63cb2/Untitled.png](FATES%20Visualization%20Tool%20Documentation%20ca920971efbc429594247cf2b1d63cb2/Untitled.png)

To view the html file, click here