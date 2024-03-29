# lepipelinedepatrick

## Basics 

This python script makes Copernicus Sentinel 2 data download easy. This script specifically downloads True Colour Images (TCI), which is faster and better for the planet, but might not be useful for those wanting to download the entire package (including red/green/blue layers...).

Sentinel 2 data uses a classification system that splits the world map into many tiles. For more information, including on how to know on which tile a specific location is, see here : https://eatlas.org.au/data/uuid/f7468d15-12be-4e3f-a246-b2882a324f59.

However, Sentinel 2 satellites often do not capture an entire tile on their passage, and several passages (with different orbits) are needed to capture the entire tile, see example below.

| Tile 36NUH, orbit 35  | Tile 36NUH, orbit 78 | Mosaic of two orbits |
| --- | --- | --- |
| ![alt text](https://github.com/memoirevive/lepipelinedepatrick/blob/main/example/36NUH_35.jpg?raw=true) | ![alt text](https://github.com/memoirevive/lepipelinedepatrick/blob/main/example/36NUH_78.jpg?raw=true) | ![alt text](https://github.com/memoirevive/lepipelinedepatrick/blob/main/example/36NUH.jpg?raw=true) |

Sentinel data can be downloaded in several resolution (10m, 20m, 60m). 10m means 1px = 10m. 10m is the most precise, but also the resolution with largest files. 

## How to use

1. In params.py, user must select the tiles for which satellite imagery must be downloaded, the resolution, and a given time period (ex: tile 36NUH, 60m, between 1 July 2022 and now). Other parameters are available. User can then run main.py.
2. For each tile, the script fetches all satellites passages within this time period (for all orbits covering the tile), and display a list of all passages for each orbit, with info regarding the date of passage and the % of cloud coverage
3. User is asked to select one passage for each orbit. Confirmation is asked before downloading images.
4. For each tile, the script then makes a mosaic of selected passages to create the entire tile, and save it in the output folder
