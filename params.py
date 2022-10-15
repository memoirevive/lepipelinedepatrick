# PARAMETERS 

# list of tiles to download
tiles = [
'36NUH',
#'36NTH',
#'36MZV',
#'36MXA',
#'37MDP',
#'36MYV',
#'36NUG',
#'36NUF',
#'36NTG',
#'36NTF',
#'36MTE',
#'36MUE',
#'36MTD',
#'36MUD',
#'36MTC',
#'36MUC',
#'36MUB',
#'36MVB',
#'36MUA',
#'36MVA',
#'36MWA',
#'36MWV',
#'36MXV',
#'37MBP',
#'36MZU',
#'36MYU',
#'37MBQ',
#'37MCP'
#'37MCQ',
#'37MDQ',
#'37MEQ',
# those are not on EACOP route but added to the map to make it look better
#'36MVE',
#'36MVD',
#'36MVC',
#'37MEP',
]

# for each tile, show shots taken between begin and end date
# this allows user to select shots (recent versus little cloud coverage)
begin_date = '20220701'
end_date = 'NOW'

# resolution  : choose between 10 (1px = 10 meters), 20 and 60
# 60 files are lighter but less detailed
resolution = 60

# max % of cloud coverage for shots to be listed for choice
max_cloud_coverage = 60

# for uploading to the internet, rescale 60 images to reduce the size (output image is X % as large)
# does nothing if resolution is 10 or 20
scale_percent = 50

# always download last image from sentinel, without asking user to choose a date for each tile
download_last = False

# speed up the work via multi-threading (set a value greater than 1 only when download_last = True)
parallel_jobs = 1

# sentinel api login details
user = 'user' # go to api_mirror website and sign up
password = 'password'
api_mirror =  'https://data.sentinel.zamg.ac.at/dhus' # (faster) or 'https://scihub.copernicus.eu/dhus' (more historical data)

