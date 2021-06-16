import numpy as np
import pandas as pd
import netCDF4 as nc
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from plotly.io import write_image
import copy
import imageio
import os
import shutil


def sunburst_matrix(files, var_dict, pfts, file_name, mode="gif", path="",
                    save_individuals=False, folder_name="individuals"):
    one_val = list(var_dict.values())[0]
    num_years = files[0][0][1].hist.variables[one_val].shape[0] - 1
    processed = scpf_param(files, var_dict, pfts, range(1, num_years + 1))

    fig = make_subplots(rows=np.shape(files)[0], cols=np.shape(files)[1],
                        specs=processed["specs"],
                        subplot_titles=processed["titles"],
                        vertical_spacing=0.1)
    extra = "/"
    if not path:
        extra = ""
    if mode == "gif":
        os.mkdir(path + extra + folder_name)
    counter = 0
    for year in range(num_years):
        for i in range(len(files)):
            for j in range(len(files[i])):
                target = processed["cleaned"][i][j]
                data = target[1][year]
                fig.add_trace(go.Sunburst(ids=np.arange(len(data)),
                                          labels=processed["labels"], parents=processed["parents"],
                                          values=data, branchvalues="total", name=str(year)),
                              row=i + 1, col=j + 1)
                if mode == "gif":
                    fig.update_layout(title={'text': f"Year {year+1}"})
                if mode != "gif" and year != 0:
                    fig.data[counter].visible = False
                    counter += 1
        if mode == "gif":
            write_image(fig, f"{path}{extra}{folder_name}/{year}.png", "png")
            fig.data = []

    if mode == "gif":
        with imageio.get_writer(f"{path}{extra}{file_name}.gif", mode="I", fps=5) as writer:
            for year in range(num_years):
                writer.append_data(imageio.imread(f"{path + extra + 'individuals'}/{year}.png"))
        if not save_individuals:
            shutil.rmtree(path + extra + folder_name)
    else:
        steps = []
        step_size = np.shape(files)[0] * np.shape(files)[1]
        for i in range(0, len(fig.data), step_size):
            step = dict(
                method="update",
                args=[{"visible": [False] * len(fig.data)}],
                label=str(round(i/step_size + 1)))
            for j in range(step_size):
                step["args"][0]["visible"][i + j] = True
            steps.append(step)
        sliders = [dict(
            currentvalue={"prefix": "Year: "},
            pad={"t": 50},
            steps=steps)]
        fig.update_layout(sliders=sliders)
        fig.write_html(f"{path}{extra}{file_name}.html")
    return fig


def scpf_param(files, var_dict, pfts, years):
    """
    Plots sunburst charts of the proportion of variable by scpf
    FILES: matrix of tuples of run name and file path, tuples are in
        the form (run_name, file_path)
    VAR_DICT: dict of variable names to be plotted in the format of
        {label: variable_name}
    PFTS: list of names of pfts
    YEARS: array of time range of data
    """
    cleaned = files
    specs = np.copy(files)
    titles = []
    specs = [[{"type": "sunburst"} for j in range(len(files[i]))] for i in range(len(files))]
    for i in range(len(files)):
        for j in range(len(files[i])):
            cleaned[i][j] = (files[i][j][0], process(files[i][j][1], var_dict, pfts, len(years)))
            titles.append(files[i][j][0])

    labels = copy.deepcopy(pfts)
    for v in var_dict:
        labels.extend([v] * len(pfts))

    parents = [""] * len(pfts)
    parents += list(range(len(pfts))) * len(var_dict)
    return {"cleaned": cleaned,
            "specs": specs,
            "titles": titles,
            "parents": parents,
            "labels": labels
            }


def process(file, var_dict, pfts, year_len):
    results = {}
    file = file.hist
    final_top = np.zeros((len(var_dict), year_len))
    final_bottom = []
    # iterate over each variable, in each variable, seperate each pft and sum up
    # values across size classes
    for label in var_dict:
        variable = file.variables[var_dict[label]][1:, :, 0]
        df = pd.DataFrame(variable)
        for i in range(len(pfts)):
            pft = df.iloc[:, 13 * i: 13 * (i + 1)].apply(sum, axis=1)
            final_bottom.append(pft.tolist())
            final_top[i] += pft
    final_top = np.transpose(final_top)
    final_bottom = np.transpose(final_bottom)
    return np.concatenate((final_top, final_bottom), axis=1)

