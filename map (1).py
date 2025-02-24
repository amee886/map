import json
import requests
from geopy import distance
import folium
from decouple import config


APIKEY = config('APIKEY')


def fetch_coordinates(apikey, address):
    base_url = "https://geocode-maps.yandex.ru/1.x"
    response = requests.get(base_url, params={
        "geocode": address,
        "apikey": APIKEY,
        "format": "json",
    })
    response.raise_for_status()
    found_places = response.json()['response']['GeoObjectCollection']['featureMember']

    if not found_places:
        return None

    most_relevant = found_places[0]
    lon, lat = most_relevant['GeoObject']['Point']['pos'].split(" ")
    return lon, lat


def load_coffee_data(file_path):
    with open(file_path, "r", encoding="CP1251") as file:
        file_contents = file.read()
        return json.loads(file_contents)


def calculate_distances(coord_fetch, capitals):
    new_list_append = []
    for coffee in capitals:
        coffee_name = coffee["Name"]
        coffee_coordinates_Lat = coffee["Latitude_WGS84"]
        coffee_coordinates_Log = coffee["Longitude_WGS84"]
        coffee_coordinates = (coffee_coordinates_Lat, coffee_coordinates_Log)
        distance_plane = (distance.distance(coord_fetch, coffee_coordinates).km)
        new_list = {
            "title": coffee_name,
            "distance": distance_plane,
            "latitude": coffee_coordinates_Lat,
            "longitude": coffee_coordinates_Log
        }
        new_list_append.append(new_list)
    return new_list_append


def create_map(coord_fetch, capitals):

    m = folium.Map(location=coord_fetch, zoom_start=12)

    folium.Marker(
        location=coord_fetch,
        tooltip="Click me!",
        popup="me",
        icon=folium.Icon(color="red"),
    ).add_to(m)

    for coffee in capitals:
        location_lat = coffee['latitude']
        location_log = coffee['longitude']
        popup_title = coffee['title']

        folium.Marker(
            location=[location_lat, location_log],
            tooltip="Click me!",
            popup=popup_title,
            icon=folium.Icon(color="green"),
        ).add_to(m)

    m.save("index.html")


def main():
    place = input()
    coords = fetch_coordinates(APIKEY, place)
    coord_fetch = coords[::-1]

    coords = fetch_coordinates(APIKEY, place)

    capitals = load_coffee_data("coffee.json")

    distance = calculate_distances(coord_fetch, capitals)

    sorted_list = sorted(distance, key=lambda x: x['distance'])[:5]

    create_map(coords[::-1], sorted_list)


if __name__ == "__main__":
    main()
