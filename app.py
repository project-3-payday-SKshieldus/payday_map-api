from flask import Flask, request, render_template
import folium
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
import time

app = Flask(__name__)

def get_location(address):
    geolocator = Nominatim(user_agent="payday_map_api_v1")
    try:
        return geolocator.geocode(address)
    except GeocoderTimedOut:
        time.sleep(1)
        return get_location(address)

@app.route('/', methods=['GET', 'POST'])
def index():

    folium_map = folium.Map(location=[37.5665, 126.9780], zoom_start=12)

    if request.method == 'POST':

        addresses = request.form.get('addresses', '')  
        if addresses:
            address_list = [address.strip() for address in addresses.split(',')]

            for address in address_list:
                location = get_location(address)
                if location:
                    folium.Marker(
                        [location.latitude, location.longitude],
                        popup=f"{address}",
                        tooltip="클릭하세요!"
                    ).add_to(folium_map)
                else:
                    print(f"주소를 찾을 수 없습니다: {address}")  

   
    map_html = folium_map._repr_html_()

    return render_template('index.html', map_html=map_html)

if __name__ == '__main__':
    app.run(debug=True)
