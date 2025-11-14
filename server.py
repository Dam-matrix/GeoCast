from flask import Flask, render_template, request
from dotenv import load_dotenv
import requests, os, datetime
from opencage.geocoder import OpenCageGeocode

load_dotenv()

GEO_API_KEY = os.getenv("OPENCAGE_API_KEY")
geocoder = OpenCageGeocode(GEO_API_KEY)

APP_ID = os.getenv("API_KEY")
forecast_url = "https://api.openweathermap.org/data/2.5/forecast"
weather_url = "https://api.openweathermap.org/data/2.5/weather"


def weather_info(web_url, query):
    location = geocoder.geocode(query)

    latitude = location[0]["geometry"]["lat"]
    longitude = location[0]["geometry"]["lng"]
    params = {
        "lat": latitude,
        "lon": longitude,
        "appid": APP_ID,
    }
    response = requests.get(web_url, params=params)
    response.raise_for_status()
    data = response.json()

    return data


today = datetime.datetime.now()
today_str = today.strftime("%A %d %B %Y")

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/forecast')
def forecast():
    return render_template('forecast.html')

@app.route('/current-weather')
def current_weather():
    return render_template('current-weather.html')

@app.route('/view-forecast', methods=['POST'])
def view_forecast():
    if request.method == 'POST':
        weather_data = weather_info(forecast_url, request.form.get('location'))

        return render_template(
            'view-forecast.html',
            city=weather_data["city"]["name"],
            country=weather_data["city"]["country"],
            weather_condition=(weather_data["list"][0]["weather"][0]["description"]).capitalize(),
            temperature=round(int(weather_data["list"][0]["main"]["temp"]) - 273.15, 2),
            wind=int(weather_data["list"][0]["wind"]["speed"]),
            humidity=weather_data["list"][0]["main"]["humidity"],
            date=today_str,
        )
    else:
        return render_template('view-forecast.html', error_msg='Something went wrong, please enter your address in the correct format!')


@app.route('/view-weather', methods=['POST'])
def view_weather():
    if request.method == 'POST':
        weather_data = weather_info(weather_url, request.form.get('location'))

        return render_template(
            'view-weather.html',
            city=weather_data["name"],
            country=weather_data["sys"]["country"],
            weather_condition=(weather_data["weather"][0]["description"]).capitalize(),
            temperature=round(int(weather_data["main"]["temp"]) - 273.15, 2),
            wind=int(weather_data["wind"]["speed"]),
            humidity=weather_data["main"]["humidity"],
            date=today_str
        )

    else:
        return render_template('view-weather.html', error_msg='Something went wrong, please enter your address in the correct format!')


if __name__ == '__main__':
    app.run(debug=True)
