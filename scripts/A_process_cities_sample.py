# -*- coding: utf-8 -*-
"""
Process a sample of cities to test to workflow.
"""

import momepy as mp
import neatnet
import networkx as nx
import os
import osmnx as ox
from time import time

FOLDEROOT = "./data/processed/"
CITY_LIST = [
    "Besançon, France"
]
USE_BUILDINGS = True


def main():
    for city_search_string in CITY_LIST:
        beg = time()
        print(f"Starting {city_search_string}")
        cityname = city_search_string.split(",")[0]
        foldersave = FOLDEROOT + cityname + "/"
        if not os.path.exists(foldersave):
            os.makedirs(foldersave)
        print(time() - beg, "Load graph")
        G = ox.graph_from_place(city_search_string, simplify=True, network_type="drive")
        gdf_streets = ox.graph_to_gdfs(
            ox.convert.to_undirected(G),
            nodes=False,
            edges=True,
            fill_edge_geometry=True,
        )
        # Project to simplify
        gdf_streets = gdf_streets.to_crs(gdf_streets.estimate_utm_crs())
        gdf_streets.to_file(foldersave + "streets_raw.gpkg")
        # Use buildings to improve simplification
        if USE_BUILDINGS:
            print(time() - beg, "Load buildings")
            gdf_buildings = (
                ox.features_from_place(city_search_string, tags={"building": True})
                .query('building != "roof"')
                .to_crs(gdf_streets.crs)
            )
            gdf_buildings.to_file(foldersave + "buildings.gpkg")
            print(time() - beg, "Simplify graph")
            gdf_simplified = neatnet.neatify(
                gdf_streets, exclusion_mask=gdf_buildings.geometry
            )
        else:
            print(time() - beg, "Simplify graph")
            gdf_simplified = neatnet.neatify(gdf_streets)
        gdf_simplified.to_file(foldersave + "streets_simplified.gpkg")
        print(time() - beg, "Create continuity graph")
        coins = mp.COINS(gdf_simplified)
        G_c = mp.coins_to_nx(coins)
        # Add metrics to continuity graph
        print(time() - beg, "Compute metrics")
        nx.set_node_attributes(G_c, values=dict(nx.degree(G_c)), name="stroke_degree")
        nx.set_node_attributes(
            G_c, values=dict(nx.betweenness_centrality(G_c)), name="stroke_betweenness"
        )
        # nx.set_node_attributes(
        #     G_c, values=dict(nx.closeness_centrality(G_c)), name="stroke_closeness"
        # )
        # G_c = mp.stroke_access(G_c)
        # G_c = mp.stroke_spacing(G_c)
        G_c = mp.stroke_orthogonality(G_c)
        # Save results on strokes and on initial graph
        strokes, edges = mp.nx_to_gdf(G_c)
        strokes.to_file(foldersave + "strokes.gpkg")
        for met in [
            "stroke_degree",
            "stroke_betweenness",
            # "stroke_closeness",
            # "stroke_access",
            # "stroke_spacing",
            "stroke_orthogonality",
        ]:
            gdf_simplified[met] = strokes.explode("edge_indices").set_index(
                "edge_indices"
            )[met]
        gdf_simplified.to_file(foldersave + "streets_enriched.gpkg")
        print(time() - beg, "Finished!")


if __name__ == "__main__":
    main()
