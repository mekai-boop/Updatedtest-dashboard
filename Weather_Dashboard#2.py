import streamlit as st
import pandas as pd
import requests
import matplotlib.pyplot as plt

# API Configuration
WEATHER_API_KEYS = {
    "OpenWeatherMap": "3e05a90825df15adcc4ea7d28d48e144",
    "WeatherStack": "30d14e69899d4562a95e01b4ca2e7790",
    "TomorrowIO": "rbdBVL09Uu1bZrW2nPdiQTu7Oe7BxY78",
    "VisualCrossing": "5CFJLHV2NAGBBF87WGD7CK5QD",
    "AccuWeather": "yn0bx3fIEwRSHDVrJKKtqAUhdsURmVjY"
}

API_URLS = {
    "OpenWeatherMap": "https://api.openweathermap.org/data/2.5/forecast",
    "WeatherStack": "http://api.weatherstack.com/forecast",
    "TomorrowIO": "https://api.tomorrow.io/v4/timelines",
    "VisualCrossing": "https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline",
    "AccuWeather": "https://dataservice.accuweather.com/forecasts/v1/daily/1day"
}

# Fetch Data from APIs
def fetch_weather_data(location, date):
    predictions = {}

    try:
        # OpenWeatherMap API
        params_owm = {
            "q": location,
            "appid": WEATHER_API_KEYS["OpenWeatherMap"],
            "units": "metric"
        }
        response_owm = requests.get(API_URLS["OpenWeatherMap"], params=params_owm)
        if response_owm.status_code == 200:
            data = response_owm.json()
            predictions["OpenWeatherMap"] = data['list'][0]['main']['temp']
    except Exception as e:
        st.warning(f"OpenWeatherMap API Error: {e}")

    try:
        # WeatherStack API
        params_ws = {
            "access_key": WEATHER_API_KEYS["WeatherStack"],
            "query": location
        }
        response_ws = requests.get(API_URLS["WeatherStack"], params=params_ws)
        if response_ws.status_code == 200:
            data = response_ws.json()
            predictions["WeatherStack"] = data.get('current', {}).get('temperature')
    except Exception as e:
        st.warning(f"WeatherStack API Error: {e}")

    try:
        # Tomorrow.io Integration
        params_tomorrow = {
            "location": location,
            "apikey": WEATHER_API_KEYS["TomorrowIO"],
            "fields": ["temperature"],
            "timesteps": "1d",
            "units": "metric"
        }
        response_tomorrow = requests.get(API_URLS["TomorrowIO"], params=params_tomorrow)
        if response_tomorrow.status_code == 200:
            data = response_tomorrow.json()
            forecast = data['data']['timelines'][0]['intervals']
            for entry in forecast:
                if entry['startTime'].startswith(str(date)):
                    predictions["TomorrowIO"] = entry['values']['temperature']
                    break
    except Exception as e:
        st.warning(f"Tomorrow.io API Error: {e}")

    try:
        # VisualCrossing API Integration
        params_visualcrossing = {
            "key": WEATHER_API_KEYS["VisualCrossing"],
            "unitGroup": "metric",
            "include": "days",
        }
        response_visualcrossing = requests.get(f"{API_URLS['VisualCrossing']}/{location}/{date}", params=params_visualcrossing)
        if response_visualcrossing.status_code == 200:
            data = response_visualcrossing.json()
            predictions["VisualCrossing"] = data['days'][0]['temp']
    except Exception as e:
        st.warning(f"VisualCrossing API Error: {e}")

    try:
        # AccuWeather API Integration
        params_accuweather = {
            "apikey": WEATHER_API_KEYS["AccuWeather"],
            "q": location,
            "metric": True
        }
        response_accuweather = requests.get(API_URLS["AccuWeather"], params=params_accuweather)
        if response_accuweather.status_code == 200:
            data = response_accuweather.json()
            predictions["AccuWeather"] = data['DailyForecasts'][0]['Temperature']['Maximum']['Value']
    except Exception as e:
        st.warning(f"AccuWeather API Error: {e}")

    return predictions

# Calculate Weighted Average
def calculate_weighted_average(predictions, weights):
    weighted_sum = sum(predictions[model] * weights.get(model, 1) for model in predictions)
    total_weight = sum(weights.get(model, 1) for model in predictions)
    return weighted_sum / total_weight if total_weight > 0 else None

# Mock Historical Accuracy Weights
HISTORICAL_WEIGHTS = {
    "OpenWeatherMap": 1.1,
    "WeatherStack": 1.0
}

# Streamlit App
st.title("Weather Model Dashboard")
st.subheader("Combine Multiple Weather Models for Precise Predictions")

# Input Section
location = st.text_input("Enter Location:", "Buffalo, NY")
date = st.date_input("Select Date:")

if location and date:
    predictions = fetch_weather_data(location, str(date))
    
    if predictions:
        # Calculate Prediction
        weighted_avg = calculate_weighted_average(predictions, HISTORICAL_WEIGHTS)
        
        # Display Combined Prediction
        st.markdown(f"### Combined Predicted Temperature: {weighted_avg:.2f} °C")
        
        # Model Comparison Table
        df = pd.DataFrame(
            {
                "Model": predictions.keys(),
                "Prediction (°C)": predictions.values(),
                "Weight": [HISTORICAL_WEIGHTS.get(model, 1) for model in predictions]
            }
        )
        st.dataframe(df)

        # Visualization
        st.markdown("### Temperature Predictions by Model")
        plt.figure(figsize=(10, 5))
        plt.bar(df["Model"], df["Prediction (°C)"], color="skyblue")
        plt.axhline(weighted_avg, color="red", linestyle="--", label=f"Weighted Avg: {weighted_avg:.2f} °C")
        plt.xlabel("Weather Model")
        plt.ylabel("Predicted Temperature (°C)")
        plt.title("Model Predictions")
        plt.legend()
        st.pyplot(plt)

        st.markdown("### Historical Weight Analysis")
        plt.figure(figsize=(10, 5))
        plt.bar(df["Model"], df["Weight"], color="orange")
        plt.xlabel("Weather Model")
        plt.ylabel("Weight")
        plt.title("Historical Accuracy Weights")
        st.pyplot(plt)

st.markdown("---")
st.markdown("*Note: Replace API keys and ensure correct API data extraction for real-world use.*")
