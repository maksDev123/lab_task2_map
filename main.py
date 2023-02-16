"""
Lab second task
"""

import argparse
import folium
import pandas
import re
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
from math import sin, cos, asin, radians, atan2, sqrt

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
    
    """
    radius = 6371 # Earth radius in kilometers
    delta_latitude = radians(latitude - latitude_1)
    delta_longitude = radians(longitude - longitude_1)
    phi_1 = radians(latitude)
    phi_2 = radians(latitude_1)

    root = (sin(delta_latitude/2)**2 + cos(phi_1) * cos(phi_2) * sin(delta_longitude/2)**2)

    distance = 2 * radius * atan2(sqrt(root), sqrt(1 - root))
    return distance


def find_by_year(path, skip, year_find, latitude_fixed, longitude_fixed):
    data = []
    geolocator = Nominatim(user_agent="movie")
    geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)
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
                    print(address)
                    print(index)
                    if ".," in address:
                        address = address.split(".,")[-1]

                    location = geocode(address)
                    distance = haversin(location.latitude, location.longitude,
                        latitude_fixed, longitude_fixed)
                    data.append((name, distance,location.latitude,
                        location.longitude, location.address))
            except (ValueError, AttributeError):
                continue
    return data

def find_near_unique(data_list):
    '''
    Gets nearest and unique places and returns dictionary with:
    key - (latitude, longitude)
    value - list of lists with films
    '''
    display_dictionary = {}
    index = 0
    while len(display_dictionary) != 10:
        if (data_list[index][2], data_list[index][3]) not in display_dictionary:
            display_dictionary[(data_list[index][2], data_list[index][3])] = []
        display_dictionary[(data_list[index][2], data_list[index][3])].append(data_list[index])
        index += 1
    return display_dictionary

roads_highlight_function = lambda x: {
  'color' :   "green",
  'opacity' : 0.90,
  'dashArray' : 3
}

def build_map(year, latitude, longitude, path_to_dataset):

    data_list = find_by_year(path_to_dataset, 15, int(year), float(latitude), float(longitude))
    data_list = sorted(data_list, key = lambda x: x[1])

    dictionary_display = find_near_unique(data_list)

    map = folium.Map(location=[latitude, longitude],
    zoom_start = 1)
    fg = folium.FeatureGroup(name="Movie")
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

        fg.add_child(folium.Marker(location=[coordinates[0], coordinates[1]],
                    popup=folium.Popup(iframe),
                    icon=folium.Icon(color = "red")))
        fg_pp.add_child(folium.GeoJson({"type": "LineString", "coordinates": [[longitude, latitude],list((coordinates[1], coordinates[0]))]},
    highlight_function = roads_highlight_function,style_function=lambda x:{'color':
      'green' if haversin(float(x["geometry"]["coordinates"][0][1]), float(x["geometry"]["coordinates"][0][0]), float(x["geometry"]["coordinates"][1][1]), float(x["geometry"]["coordinates"][1][0])) < 500
  else 'orange' if 500 <=  haversin(float(x["geometry"]["coordinates"][0][1]), float(x["geometry"]["coordinates"][0][0]), float(x["geometry"]["coordinates"][1][1]), float(x["geometry"]["coordinates"][1][0])) < 1000
  else 'red'}
    ))


    map.add_child(fg_pp)
    map.add_child(fg)
    map.add_child(folium.LayerControl())
    map.save('Map_Different_Color.html')

if __name__ == "__main__":
    build_map(args.year, args.latitude, args.longitude, args.path_to_dataset)
