import plotly.graph_objects as go
import plotly.express as px
import geojson
import numpy as np
import pandas as pd

def colored_map(files, var, token, title, file_name, mode="interactive", path="",
				center={"lat": 39.5, "lon": -121}, zoom=5.5, w=500, h=800):
	param = files.param
	vlon = param.variables["xv"][:]
	vlat = param.variables["yv"][:]
	var = files.hist.variables[var][0]

	feat_col = []
	real_var = []
	index = 0
	for i in range(np.shape(var)[0]):
		for j in range(np.shape(var)[1]):
			if np.ma.is_masked(var[i,j]) or var[i,j] == 0:
				continue
			lon = vlon[i,j]
			lat = vlat[i,j]
			vertices = [(lon[h], lat[h]) for h in range(4)]
			vertices.append(vertices[0])
			poly = geojson.Polygon([vertices])
			feature = geojson.Feature(geometry=poly, id=index)
			feat_col.append(feature)
			real_var.append(var[i,j])
			index += 1
	feature_collection = geojson.FeatureCollection(feat_col)

	fig = go.Figure(go.Choroplethmapbox(geojson=feature_collection, 
		locations=np.arange(len(real_var)), z=pd.Series(real_var),
		colorscale="viridis", marker_line_width=0, marker_opacity=0.95))
	fig.update_layout(mapbox_center = center, mapbox_zoom=zoom,
                 mapbox_style="streets", mapbox_accesstoken=token)
	fig.update_layout(width=w, height=h, title=title)
	extra = "/"
	if not path:
		extra = ""
	if mode == "interactive":
		fig.write_html(f"{path}{extra}{file_name}.html")
	else:
		fig.write_image(f"{path}{extra}{file_name}.png", scale=4)