import numpy as np
import netCDF4 as nc
import pandas as pd
from operator import mul
from files import *
import os
import re

def pre_process(files, year, mode="basic"):
	"""
	A tedious pre-processing function that prepares data for plotting
	"""
	# pull cohort data
	rest_fin = files.restart[year]
	param_fin = files.param
	crown_area = carea_allom(rest_fin, param_fin)
	cohort_height = rest_fin.variables['fates_height'][:]
	pft = rest_fin.variables['fates_pft'][:]
	canopy_layer = rest_fin.variables['fates_canopy_layer'][:]
	trunk_width = rest_fin.variables['fates_dbh'][:]
	num_plants = rest_fin.variables['fates_nplant'][:]

	# pull patch data
	patch_area = rest_fin.variables['fates_area'][:]
	patch_area_clean = [area if area else np.nan for area in patch_area] # fills empty values with NaN
	patch_age = rest_fin.variables['fates_age'][:]
	patch_age_clean = [age if age else np.nan for age in patch_age] # fills empty values with NaN
	
	# make dataframe1: combined cohort and patch data
	data1 = {
		'crown_area':crown_area,
		'cohort_height': cohort_height,
		'pft': pft,
		'canopy_layer': canopy_layer,
		'trunk_width': trunk_width,
		'patch_area': patch_area_clean,
		'patch_age': patch_age_clean,
		'num_plants': num_plants*1600}
	df1 = pd.DataFrame(data1)
	df1[['patch_area', 'patch_age']] = df1[['patch_area', 'patch_age']].ffill() # fills NaN values
	df1 = df1[df1['cohort_height'] != 0] # gets rid of empty cohorts
	df1['canopy_layer'] = df1['canopy_layer'].replace({1: 'orange', 2: 'grey'})

	# make dataframe2: a master df that only has patch data
	# clean data
	patch_area_c = [area for area in patch_area if area] # gets rid of 0's
	patch_age_c = [age for age in patch_age if age] # gets rid of 0's
	data2 = {'patch_area': patch_area_c, 'patch_age': patch_age_c}
	try:
		df2 = pd.DataFrame(data2)
	except ValueError:
		patch_age_c.extend([0]*(len(patch_area_c)-len(patch_age_c)))
		df2 = pd.DataFrame(data2)

	# merge small areas
	small = df2[df2['patch_area'] <= find_small(df2, 1000)]
	small_areas = small['patch_area'].tolist()
	small_ages = small['patch_age'].tolist()
	sum_small_areas = mul([sum(small_areas)], len(small_areas))
	avg_small_ages = mul([np.average(small_ages)], len(small_ages))
	for df in [df1, df2]:
		df['patch_age'] = df['patch_age'].replace(to_replace=small_ages, value = avg_small_ages)
		df['patch_area'] = df['patch_area'].replace(to_replace = small_areas, value = sum_small_areas)
	df2 = df2.drop_duplicates(keep='first')

	# calculate coverage by patch
	coverages = []
	for patch in df2['patch_area'].tolist():
		to_sum = df1[df1['patch_area'] == patch]
		coverages.append(find_individual_coverage(to_sum, patch))
	df2 = df2.assign(coverages = coverages)

	# sort data by height
	df1 = df1.sort_values(['patch_area','cohort_height'])
	df2 = df2.sort_values('patch_area')
	# make data for plotting canopy and stem
	df1['canopy_bottom'] = df1['cohort_height'] * 0.6
	df1['canopy_width'] = df1['crown_area'] / (df1['cohort_height'] * 0.4)
	results = []
	for area in df2['patch_area'].to_list():
		patch = df1[df1['patch_area'] == area]['canopy_width'].to_list()
		patch = np.asarray(patch) + 10
		cumsum = np.cumsum(patch)
		processed = [a - (b/2) for a, b in zip(cumsum, patch)]
		results.extend(processed)
	df1['stem_location'] = results
	df1['year'], df2['year'] = year, year

	if mode == "basic":
		return df1, df2
	# create a simplified version of the data
	areas = df2['patch_area'].tolist()
	simplified_patches = pd.DataFrame()
	for area in areas:
		target = df1[df1['patch_area'] == area]
		max_dbh = max(target['trunk_width'])
		target = target.assign(dbh_binned = pd.cut(target['trunk_width'],
								np.array([0,5,10,15,20,30,40,50,60,70,80,90,100,max(101,max_dbh)]),
								labels = ['SC1', 'SC2', 'SC3', 'SC4', 'SC5', 'SC6', 'SC7', 'SC8',
										 'SC9', 'SC10', 'SC11', 'SC12', 'SC13']))
		grouped = target.groupby(['pft', 'canopy_layer', 'dbh_binned']).agg(
					trunk_width = ('trunk_width', np.median),
					num_plants=('num_plants', 'sum'),
					cohort_height = ('cohort_height', np.median),
					crown_area = ('crown_area', 'sum'),
					patch_area = ('patch_area', 'first'),
					patch_age = ('patch_age', 'first'))
		grouped = grouped.reset_index().dropna()
		grouped = grouped.assign(canopy_bottom = grouped['cohort_height'] * 0.6 )
		grouped = grouped.assign(canopy_width = grouped['crown_area'] / (grouped['cohort_height'] * 0.4))
		grouped = grouped.sort_values(by=['canopy_layer', 'pft'])
		patch = grouped['canopy_width'].to_list()
		patch = np.asarray(patch) + 10
		cumsum = np.cumsum(patch)
		processed = [a - (b/2) for a, b in zip(cumsum, patch)]
		grouped = grouped.assign(stem_location = processed)
		simplified_patches = simplified_patches.append(grouped, sort=True)
		simplified_patches['year'] = year

	if mode == "patch simplified":
		return simplified_patches, df2
	elif mode == "one patch":
		simplified_patches.sort_values(by="cohort_height", inplace=True)
		index = simplified_patches["canopy_width"].tolist()
		patch = np.array(index) + 10
		index = np.cumsum(patch)
		index = [a - (b/2) for a, b in zip(index, patch)]
		simplified_patches["stem_location"] = index
		simplified_patches["patch_age"] = 0
		simplified_patches["patch_area"] = 1
		df2 = pd.DataFrame({"patch_age":[0], "patch_area": [1]})
		return simplified_patches, df2


def carea_allom(rest_fin, paramfin):
		"""REST_FIN: a restart file
		   PARAMFIN: a parameter file
		   Returns a list of crown area of each cohort?
		"""
		ncohorts_max = len(rest_fin.variables['fates_CohortsPerPatch'][:])
		# ncohorts_max: maximum number of cohorts (some of the rows in this variable are empty)
		# number of cohorts per patch
		pft = rest_fin.variables['fates_pft'][:]  # plant functional group
		dbh = rest_fin.variables['fates_dbh'][:]  # diameter at breast height
		carea = np.ma.masked_all(ncohorts_max)
		fates_allom_cmode = paramfin.variables['fates_allom_cmode'][:] # coarse root biomass allometry function index
		if np.any(fates_allom_cmode != 1):
			raise Exception
		carea_exp = paramfin.variables['fates_allom_d2bl2'][:]
		fates_allom_d2ca_coefficient_max = paramfin.variables['fates_allom_d2ca_coefficient_max'][:]
		fates_allom_d2ca_coefficient_min = paramfin.variables['fates_allom_d2ca_coefficient_min'][:]
		fates_allom_blca_expnt_diff = paramfin.variables['fates_allom_blca_expnt_diff'][:]
		fates_spread = rest_fin.variables['fates_spread'][:]
		fates_nplant = rest_fin.variables['fates_nplant'][:]
		fates_allom_dbh_maxheight = paramfin.variables['fates_allom_dbh_maxheight'][:]
		d2ca_coeff = fates_allom_d2ca_coefficient_max * fates_spread + fates_allom_d2ca_coefficient_min * (
					1. - fates_spread)
		for i in range(ncohorts_max):
			if pft[i] > 0:
				eff_dbh = np.min([dbh[i], fates_allom_dbh_maxheight[pft[i] - 1]])
				carea[i] = d2ca_coeff[pft[i] - 1] * (
							eff_dbh ** (carea_exp[pft[i] - 1] + fates_allom_blca_expnt_diff[pft[i] - 1])) * fates_nplant[i]
		return carea

# some helper functions
def find_max(self):
	"""find the max number of plants in a file upload"""
	for file in self.detailed:
		max_in_one_file = max(file['num_plants'].tolist())
		self.max_plants = max(self.max_plants, max_in_one_file)

def find_small(df, threshold):
	"""find the total area below THREAHOLD"""
	ranked = df.sort_values('patch_area')
	areas = ranked['patch_area'].tolist()
	total = 0
	maximum = 0
	while total + areas[0] <= threshold:
		total += areas[0]
		maximum = areas[0]
		areas = areas[1:]
	return maximum

def find_individual_coverage(df, total):
	grouped = df.groupby('canopy_layer', as_index=False)[['crown_area']].sum()
	try:
		canopy_raw = grouped[grouped['canopy_layer'] == "orange"].reset_index()['crown_area'][0]
	except (KeyError, IndexError):
		canpy_raw = 0
	try:
		understory_raw = grouped[grouped['canopy_layer'] == 'grey'].reset_index()['crown_area'][0]
	except (KeyError, IndexError):
		understory_raw = 0
	data = [canopy_raw, understory_raw, total - max(canopy_raw, understory_raw)]
	if data[2] < 0:
		data[2] = 0
	return data




