# lepipelinedepatrick

## Basics 

This python script makes Copernicus Sentinel 2 data download easy. This script only downloads True Colour Images (TCI), which is faster and better for the planet, but might not be useful for those wanting to download all layers (ex: red/green/blue layers).

Sentinel 2 data uses a classification system that splits the world map into many tiles. For more information, including on how to know on which tile a specific location is, see here : https://eatlas.org.au/data/uuid/f7468d15-12be-4e3f-a246-b2882a324f59.

However, Sentinel 2 satellites often do not capture an entire tile on their passage, and several passages (with different orbits) are needed to capture the entire tile, see example below.

| Tile 36NUH, orbit 35  | Tile 36NUH, orbit 78 | Mosaic of two orbits |
| --- | --- | --- |
| ![alt text](https://github.com/memoirevive/lepipelinedepatrick/blob/main/example/36NUH_35.jpg?raw=true) | ![alt text](https://github.com/memoirevive/lepipelinedepatrick/blob/main/example/36NUH_78.jpg?raw=true) | ![alt text](https://github.com/memoirevive/lepipelinedepatrick/blob/main/example/36NUH.jpg?raw=true) |

Please note that sentinel data can be downloaded in several resolution (10m, 20m, 60m). 10m means 1px = 10m. 10m is the most precise, but also the largest files. 

## How to use

1. In params.py, users can select the tiles for which satellite imagery must be downloaded, the resolution, and a given time period (ex: tile 36NUH, 60m, between 1 July 2022 and now)
2. For each tile, the script fetches all satellites passages within this time period (for all orbits covering the tile)
3. All passages are displayed for each orbit, with info regarding the date of passage and the % of cloud coverage
4. Users are asked to select one passage for each orbit
5. The script then makes a mosaic of selected passages to create the entire tile
6. Output tiles are saved in the output folder
