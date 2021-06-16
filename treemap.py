import numpy as np
import netCDF4 as nc
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from matplotlib import colors
from matplotlib.colors import LinearSegmentedColormap
import squarify
from operator import mul
import os
import animatplot as amp
import re
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from files import *
from treemap_utils import *
import imageio
from pygifsicle import optimize
import shutil


def animate_treemap(files, mode="basic", path="", file_name="animated treemap",
	save_individuals=False, folder_name="individuals"):
	print(path)
	os.mkdir(path+"/"+folder_name)
	for year in range(1, len(files.restart)+1):
		print(year, end=" ")
		treemap(files, year, mode, path+"/"+folder_name)
		plt.close()
	with imageio.get_writer(f"{path}/{file_name}.gif", mode="I", fps=5) as writer:
		for year in range(1, len(files.restart)+1):
			writer.append_data(imageio.imread(f"{path+'/individuals'}/{year}.png"))
	if not save_individuals:
		shutil.rmtree(path+"/"+folder_name)



def treemap(files, year, mode="basic", path=None, name=None):
	df1, df2 = pre_process(files, year, mode)
	ages = df2['patch_age'].tolist()
	areas = df2['patch_area'].tolist()
	ages, areas = [list(t) for t in zip(*sorted(zip(ages, areas)))]

	# generate figures and axes
	fig, mainax = plt.subplots(figsize=(10, 6))
	fig.suptitle("*Stem Color: orange: canopy, grey: understory", x=0.32, y=0.19)
	mainax.set_title(f"Year {year}", fontsize = 45, position=(0.15,1.01))
	mainax.set_xticks([])
	mainax.set_yticks([])
	mainax.grid(False)
	plt.subplots_adjust(bottom=0.2)

	# set color scale
	norm=plt.Normalize(vmin=0, vmax=80)

	if mode != "one patch":
		colorbar = plt.colorbar(plt.cm.ScalarMappable(cmap=blue, norm=norm), label='Years since disturbance')
		colorbar.ax.yaxis.set_label_position("left")

	#make rectangles
	pos = mainax.get_position()
	normalized_values = squarify.normalize_sizes(areas, pos.width, pos.height)
	rects = squarify.squarify(normalized_values, pos.x0, pos.y0, pos.width, pos.height)
	axes = [fig.add_axes([rect['x'], rect['y'], rect['dx'], rect['dy'] ]) for rect in rects];
	bar = fig.add_axes()

	#iterate over cohorts
	for ax, area, age, n  in zip(axes, areas, ages, range(len(axes))):
		ax.set_xticks([])
		ax.set_ylim(0, 75)
		ax.set_zorder(len(axes)-n)
		ax.tick_params(axis="y", direction="in", pad=-17)
		ax.yaxis.get_major_ticks()[0].label1.set_visible(False)
		ax.yaxis.get_major_ticks()[-1].label1.set_visible(False)
		if mode != "one patch":
			ax.set_facecolor(blue(norm(age)))
			ax.tick_params(axis='y', colors='white')
		filtered_pre = df1[df1['patch_area'] == area]
		for i, c in zip([1,2], [purple, yellow]):
			filtered = filtered_pre[filtered_pre['pft'] == i]
			tree_height = filtered['cohort_height']
			index = filtered['stem_location']
			tree_width = filtered['trunk_width']
			crown_size = filtered['crown_area']
			crown_bottom = filtered['canopy_bottom']
			crown_width = filtered['canopy_width']
			layer = filtered['canopy_layer']
			num_plants = filtered['num_plants'].to_list()
			ax_norm = colors.LogNorm(vmin=1, vmax=1000000)
			bars = ax.bar(np.array(index), tree_height*0.4,width = crown_width, bottom = np.array(crown_bottom),
				   #alpha=0.5,
				   edgecolor='none',
				   color = c(ax_norm(num_plants)))
			ax.bar(np.array(index), crown_bottom, width = 10, color=layer, linewidth=2)

	# set cohort color bars
	if mode != "one patch":
		cbaxes_yellow = fig.add_axes([pos.x0 + pos.x1, pos.y0, 0.02, pos.height/2 - 0.02])
		cbaxes_purple = fig.add_axes([pos.x0 + pos.x1, pos.y0 + pos.height/2 + 0.02, 0.02, pos.height/2 -0.02])
	else:
		cbaxes_yellow = fig.add_axes([pos.x0 + pos.x1 - 0.08, pos.y0, 0.02, pos.height/2 - 0.02])
		cbaxes_purple = fig.add_axes([pos.x0 + pos.x1 - 0.08, pos.y0 + pos.height/2 + 0.02, 0.02, pos.height/2 -0.02])


	ax_norm = colors.LogNorm(vmin=1, vmax=1000000)
	colorbar1 = plt.colorbar(plt.cm.ScalarMappable(cmap=yellow, norm=ax_norm),
								 cax = cbaxes_yellow, label=' Cedar: # plants in cohort')
	colorbar2 = plt.colorbar(plt.cm.ScalarMappable(cmap=purple, norm=ax_norm),
								 cax = cbaxes_purple, label = 'Ponderosa: # plants in cohort')
	colorbar1.ax.yaxis.set_label_position("left")
	colorbar2.ax.yaxis.set_label_position("left")

	mainax.set_facecolor('none')
	mainax.set_zorder(20)
	if path:
		if not name:
			name = year
		fig.savefig(path + f"/{name}.png")



blue = LinearSegmentedColormap.from_list('blue', ['#96ffff', '#000080'])
yellow = LinearSegmentedColormap.from_list('yellow', ['#fffd98', '#fc7753'])
matplotlib.cm.register_cmap("myyellow", yellow)
red = LinearSegmentedColormap.from_list('red', ['#03edfc', '#e80013'])
interval = np.hstack(np.linspace(0.25,1))
purple_cm = plt.cm.Purples(interval)
purple = LinearSegmentedColormap.from_list('name', purple_cm)
matplotlib.cm.register_cmap("mypurple", purple)
