from flask import Flask, request, jsonify
from flask_cors import CORS
import folium
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
import time

app = Flask(__name__)
CORS(app)

def get_location(address):
    geolocator = Nominatim(user_agent="payday_map_api_v1")
    try:
        return geolocator.geocode(address)
    except GeocoderTimedOut:
        time.sleep(1)
        return get_location(address)

@app.route('/map', methods=['POST'])
def generate_map():
    data = request.json
    receipts = data.get('receipts', [])
    selected_index = data.get('selectedIndex', -1)

    if selected_index != -1 and selected_index < len(receipts):
        selected_receipt = receipts[selected_index]
        selected_location = get_location(selected_receipt['address'])
        if selected_location:
            map_location = [selected_location.latitude, selected_location.longitude]
        else:
            map_location = [37.5665, 126.9780]
    else:
        map_location = [37.5665, 126.9780]

    folium_map = folium.Map(
        location=map_location,
        zoom_start=10,
        width='100%',
        height='100%'
    )

    for idx, receipt in enumerate(receipts):
        address = receipt['address']
        store_name = receipt['storeName']
        location = get_location(address)

        if location:
            color = 'red' if idx == selected_index else 'blue'
            icon = folium.Icon(color=color, icon='info-sign')
            folium.Marker(
                [location.latitude, location.longitude],
                popup=store_name,
                tooltip=f"영수증 {idx + 1}",
                icon=icon
            ).add_to(folium_map)
        else:
            print(f"주소를 찾을 수 없습니다: {address}")

    return jsonify({"map_html": folium_map._repr_html_()})

if __name__ == '__main__':
    app.run(debug=True)
