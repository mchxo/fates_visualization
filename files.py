import numpy as np
import netCDF4 as nc
import pandas as pd
from operator import mul
import os
import re

class Files:
	restart = {}
	param = None
	hist = None

	def __init__(self, rest_folder=None, param_path=None, 
		hist_path=None, address="relative"):
		assert rest_folder or param_path, "no file path specified"
		if rest_folder:
			assert param_path, "no parameter file specified"
			print("reading restart files ...")
			if address =="relative":
				current = os.getcwd()
				rest_folder = f"{current}/{rest_folder}"
			file_paths = [rest_folder +"/"+ name for name in os.listdir(rest_folder)]
			file_paths.sort()
			year = 1
			for path in file_paths:
				if re.findall(r'\.(\d{4})-', path):
					f = nc.Dataset(path)
					self.restart[year] = f
					year += 1
			self.param = nc.Dataset(param_path)
			print("done!")
		if hist_path:
			self.hist = nc.Dataset(hist_path)


	def readin(self, rest_folder_path, param_path, hist_path):
		"""Read in restart and parameter files"""
		file_paths = [rest_folder_path + name for name in os.listdir(rest_folder_path) if name != '.DS_Store']
		file_paths.sort()
		self.rest = {}
		print('Reading Files...')
		if self.kind == "restart":
			for path in file_paths:
				year = re.findall(r'\.(\d{4})-', path)[0]
				f = nc.Dataset(path)
				self.rest[int(year)] = f
		self.param = nc.Dataset(param_path)
		if hist_path:
			self.hist = nc.Dataset(hist_path)  