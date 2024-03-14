import requests
import argparse
import sys
from PIL import Image
import io
import math


def get_request(path, params):
    response = requests.get(path, params)
    if not response:
        print(f"Ошибка! Код ошибки: {response.status_code}")
        sys.exit(1)
    return response


parser = argparse.ArgumentParser()
parser.add_argument("address", type=str)
args = parser.parse_args()

path = "http://geocode-maps.yandex.ru/1.x/"
TOKEN = "40d1649f-0493-4b70-98ba-98533de7710b"
params = {
    "apikey": TOKEN,
    "geocode": args.address,
    "format": "json"}

response = get_request(path, params)
json_response = response.json()
coords = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]["Point"]["pos"]
float_coords = tuple(map(float, coords.split()))
coords = coords.replace(" ", ",")

path = "https://search-maps.yandex.ru/v1/"
TOKEN = "dda3ddba-c9ea-4ead-9010-f43fbc15c6e3"
drug_store_search = "аптека"
params = {
    "apikey": TOKEN,
    "text": drug_store_search,
    "lang": "ru_RU",
    "ll": coords,
    "results": 10,
    "format": "json"}
response = get_request(path, params)
json_response = response.json()
orgs = json_response["features"]

org_points = []
for org in orgs:
    org_coords = org["geometry"]["coordinates"]
    try:
        org_worktime = org["properties"]["CompanyMetaData"]["Hours"]["Availabilities"][0]
    except KeyError:
        org_points.append(",".join(map(str, org_coords)) + ",pm2grm")
    else:
        if "TwentyFourHours" in org_worktime:
            org_points.append(",".join(map(str, org_coords)) + ",pm2gnm")
        else:
            org_points.append(",".join(map(str, org_coords)) + ",pm2blm")


path = "http://static-maps.yandex.ru/1.x/"
params = {
    "l": "map",
    "pt": "~".join(org_points)
}
response = get_request(path, params)
Image.open(io.BytesIO(response.content)).show()
