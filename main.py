"""
Lab second task
"""
import doctest
import argparse
from math import sin, cos, radians, atan2, sqrt
import folium
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter


parser = argparse.ArgumentParser()
parser.add_argument("year")
parser.add_argument("latitude")
parser.add_argument("longitude")
parser.add_argument("path_to_dataset")

args = parser.parse_args()

def haversin(latitude, longitude, latitude_1, longitude_1):
    """
    Returns great-circle distance between two points on a sphere
    given their longitudes and latitudes
    >>> haversin(51.5007, 0.1246, 40.6892, 74.0445)
    5574.84
    >>> haversin(11.111, 1.1246, 41.151715, 74.0445)
    7771.423
    >>> haversin(3.33, 1.1246, 5.555, 1.357)
    248.746
    """
    earth_radius = 6371 # Earth radius in kilometers
    delta_latitude = radians(latitude - latitude_1)
    delta_longitude = radians(longitude - longitude_1)
    phi_1 = radians(latitude)
    phi_2 = radians(latitude_1)

    root = (sin(delta_latitude/2)**2 + cos(phi_1) * cos(phi_2) * sin(delta_longitude/2)**2)

    distance = 2 * earth_radius * atan2(sqrt(root), sqrt(1 - root))
    return round(distance, 3)


def find_by_year(path, skip, year_find, latitude_fixed, longitude_fixed):
    """
    This function parses file with "path", skiping "skip" row and returns list of tuples in which:
    1) Name of film,
    2) Distance from given point ("latitude_fixed", "longitude_fixed"),
    3) latitude,
    4) longitude,
    5) address
    """
    data = []
    geolocator = Nominatim(user_agent="movie")
    geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)
    try:
        with open(path, "r") as file:
            lines = set(file.readlines()[skip:])
            for index, line in enumerate(lines):
                try:
                    left_part = str(line).strip().replace("\\t", "").replace("\\n", "").split(")")
                    year = left_part[0][-4:]
                    if int(year) == year_find:
                        name = left_part[0][1:-7]
                        address = left_part[-1].strip().replace("\\t", "").replace("\\n", "")
                        if left_part[-1] == "":
                            address = left_part[-2].strip().replace("\\t", "").replace("\\n", "")
                        if ".," in address:
                            address = address.split(".,")[-1]

                        location = geocode(address)
                        distance = haversin(location.latitude, location.longitude,
                            latitude_fixed, longitude_fixed)
                        data.append((name, distance,location.latitude,
                            location.longitude, location.address))
                except (ValueError, AttributeError):
                    continue
    except:
        print("Unable to read file")
        exit()
    return data

def find_near_unique(data_list, number_movies):
    '''
    Gets nearest and unique places and returns dictionary with:
    key - (latitude, longitude)
    value - list of lists with films
    >>> find_near_unique([("Start", 100, 1.101, 10.1, "USA"),\
    ("Glory", 170, 3.975, 10.7, "USA"), ("Student", 1700 , 1.975, 3.7, "USA")], 1)
    {(1.101, 10.1): [('Start', 100, 1.101, 10.1, 'USA')]}

    >>> find_near_unique([("Start", 100, 1.101, 10.1, "USA"),\
    ("Glory", 170, 3.975, 10.7, "USA"), ("Student", 1700, 1.975, 3.7, "USA")], 3)
    {(1.101, 10.1): [('Start', 100, 1.101, 10.1, 'USA')],\
 (3.975, 10.7): [('Glory', 170, 3.975, 10.7, 'USA')],\
 (1.975, 3.7): [('Student', 1700, 1.975, 3.7, 'USA')]}

    >>> find_near_unique([("Start", 100, 1.101, 1.101, "USA"),\
    ("Glory", 100, 1.101, 1.101, "USA"), ("Student", 1700, 1.975, 3.7, "USA")], 3)
    {(1.101, 1.101): [('Start', 100, 1.101, 1.101, 'USA'), ('Glory', 100, 1.101, 1.101, 'USA')],\
 (1.975, 3.7): [('Student', 1700, 1.975, 3.7, 'USA')]}
    '''
    display_dictionary = {}
    index = 0
    while len(display_dictionary) != number_movies:
        if index >= len(data_list):
            break
        if (data_list[index][2], data_list[index][3]) not in display_dictionary:
            display_dictionary[(data_list[index][2], data_list[index][3])] = []
        display_dictionary[(data_list[index][2], data_list[index][3])].append(data_list[index])
        index += 1
    return display_dictionary


def build_map(year, latitude, longitude, path_to_dataset):
    """
    Builds and saves map as html file with name Map_Movies.
    """
    data_list = find_by_year(path_to_dataset, 15, int(year), float(latitude), float(longitude))

    if not data_list:
        print("There are no films found this year")
        exit()

    data_list = sorted(data_list, key = lambda x: x[1])

    dictionary_display = find_near_unique(data_list, 10)

    map = folium.Map(location=[latitude, longitude],
    zoom_start = 2)
    marker_groups = folium.FeatureGroup(name="Movie")
    html = """<h4>Movie/es information:</h4>
    Film name/s: {},<br>
    Address: {},<br>
    Quantity of films: {},<br>
    Distance: {}
    """
    fg_pp = folium.FeatureGroup(name="Distance lines")
    for coordinates, films in dictionary_display.items():
        film_names = "; ".join([film[0] for film in films])
        iframe = folium.IFrame(html=html.format(film_names, films[0][-1], len(films), films[0][1]),
                          width=300,
                          height=100)

        marker_groups.add_child(folium.Marker(location=[coordinates[0], coordinates[1]],
                    popup=folium.Popup(iframe),
                    icon=folium.Icon(color = "red")))
        fg_pp.add_child(folium.GeoJson({"type": "LineString", "coordinates":
                    [[longitude, latitude],list((coordinates[1], coordinates[0]))]},
                    highlight_function = lambda x: {
            'color' :   "green",
            'opacity' : 0.90,
            'dashArray' : 3
            },
                    style_function = lambda x:{'color':
        'green' if haversin(float(x["geometry"]["coordinates"][0][1]),
            float(x["geometry"]["coordinates"][0][0]), float(x["geometry"]["coordinates"][1][1]),
            float(x["geometry"]["coordinates"][1][0])) < 300
            else 'orange' if 300 <=  haversin(float(x["geometry"]["coordinates"][0][1]),
            float(x["geometry"]["coordinates"][0][0]), float(x["geometry"]["coordinates"][1][1]),
            float(x["geometry"]["coordinates"][1][0])) < 700
            else 'red'}
    ))
    map.add_child(fg_pp)
    map.add_child(marker_groups)
    map.add_child(folium.LayerControl())
    map.save('Map_Movies.html')
def check_input(year, latitude, longitude):
    """
    Checks if year, latitude and longitude are numeric
    """
    try:
        float(year), float(latitude), float(longitude)
    except ValueError:
        print("Unappropriate data format")
        exit()

if __name__ == "__main__":
    doctest.testmod()
    check_input(args.year, args.latitude, args.longitude)
    build_map(args.year, args.latitude, args.longitude, args.path_to_dataset)
