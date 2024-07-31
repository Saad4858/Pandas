import requests

import json 

weather_api_key = "daa0520e018242bb963113925243107"
base_url = "http://api.weatherapi.com/v1"

def get_current_weather_data(city):
    endpoint = "/current.json"
    parameters = {
        "key": weather_api_key,
        "q": city
    }

    url = base_url + endpoint
    response = requests.get(url=url, params=parameters)
    data = response.json()
    current_data = data['current']

    # Extracting detailed information from the response
    temp_c = current_data['temp_c']
    temp_f = current_data['temp_f']
    condition = current_data['condition']['text']
    wind_kph = current_data['wind_kph']
    wind_degree = current_data['wind_degree']
    precip_mm = current_data['precip_mm']
    humidity = current_data['humidity']

    # Creating a comprehensive print statement
    weather_summary = (
        f"The current weather in {city} is {condition}. "
        f"The temperature is {temp_c}°C ({temp_f}°F). "
        f"Wind is blowing at {wind_kph} km/h from {wind_degree} degrees. "
        f"There has been {precip_mm} mm of precipitation. "
        f"The humidity level is at {humidity}%. "
    )

    # print(weather_summary)
    return weather_summary

def get_six_hour_weather(data):
    weather_summary = ""
    for forecast_day in data['forecast']['forecastday']:
        date = forecast_day['date']
        weather_summary += f"Weather data for {date}:\n"
        for hour_data in forecast_day['hour']:
            time = hour_data['time']
            temp = hour_data['temp_c']
            condition = hour_data['condition']['text']
            wind_kph = hour_data['wind_kph']
            humidity = hour_data['humidity']
            
            # Filter out every 6-hour data starting from 00:00
            if time.endswith("00:00") or time.endswith("06:00") or time.endswith("12:00") or time.endswith("18:00"):
                hourly_summary = f"At {time}, the temperature is {temp}°C, condition '{condition}', "
                hourly_summary += f"wind speed {wind_kph} kph, and humidity {humidity}%.\n"
                weather_summary += hourly_summary
        weather_summary += "\n"  # Separate days by a newline for clarity
    return weather_summary


def get_forecast(city,days):
    endpoint = "/forecast.json"
    parameters = {
        "key": weather_api_key,
        "q": city,
        "days" : days
    }

    url = base_url + endpoint
    response = requests.get(url=url, params=parameters)
    data = response.json()
    pretty_data = json.dumps(data,indent=1)
    weather_summary = ""
    for day in data['forecast']['forecastday']:
        date = day['date']
        max_temp = day['day']['maxtemp_c']
        min_temp = day['day']['mintemp_c']
        condition = day['day']['condition']['text']
        max_wind = day['day']['maxwind_kph']
        total_precip = day['day']['totalprecip_mm']
        avg_humidity = day['day']['avghumidity']
        sunrise = day['astro']['sunrise']
        sunset = day['astro']['sunset']
        
        # Build the summary string for each day
        daily_summary = f"On {date}, the weather will be '{condition}' with temperatures ranging from {min_temp}°C to {max_temp}°C. "
        daily_summary += f"The maximum wind speed will be {max_wind} kph with total precipitation of {total_precip} mm. "
        daily_summary += f"Average humidity will be around {avg_humidity}%. Sunrise at {sunrise} and sunset at {sunset}.\n"
        
        weather_summary += daily_summary

    six_hour_weather_summary = get_six_hour_weather(data=data)
    
    # print(weather_summary)

    
    
    return weather_summary ,six_hour_weather_summary

    print(pretty_data)




current_weather_summary = get_current_weather_data("Lahore")

# print(current_weather_summary)

forecast ,six_hour_forecast = get_forecast("Lahore",3)