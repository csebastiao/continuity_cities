# -*- coding: utf-8 -*-
"""
Process a sample of cities to test to workflow.
"""

import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import os

FOLDER_IN = "./data/processed/"
FOLDER_OUT = "./plots/"
CITY_LIST = [
    "Besançon, France",  # Small, effect of river
    "Vienna, Austria",
]

def main():
    for city_search_string in CITY_LIST:
        cityname = city_search_string.split(",")[0]
        foldersave = FOLDER_OUT + cityname + "/"
        if not os.path.exists(foldersave):
            os.makedirs(foldersave)
        gdf_strokes = gpd.read_file(FOLDER_IN + cityname + "/strokes.gpkg")
        # Plot in log-log scale the distribution of each metrics
        for met in [
            "stroke_degree",
            "stroke_betweenness",
        ]:
            fig, ax = plt.subplots(figsize=(16, 9))
            _, bins = np.histogram(gdf_strokes[met].values, bins=20)
            if met == "stroke_degree":
                minval = 1
            elif met == "stroke_betweenness":
                minval = 10**-7
            logbins = np.logspace(start=np.log10(max(bins[0], minval)), stop=np.log10(bins[-1]), num=len(bins))
            hist, bins = np.histogram(gdf_strokes[met].values, bins=logbins)
            hist = [val/sum(hist) for val in hist]
            bins_centroid = [(bins[i]+bins[i+1])/2 for i in range(len(bins)-1)]
            ax.scatter(bins_centroid, hist, color="black", s=80)
            ax.set_xscale("log")
            ax.set_yscale("log")
            ax.set_xlabel(met)
            ax.set_ylabel(f"Probability of {met}")
            fig.savefig(foldersave + f"hist_{met}.jpeg")


if __name__ == "__main__":
    main()
