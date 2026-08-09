import requests


def get_weather(city: str) -> dict:
    """
    Get current real-time weather information for a city or district.

    Use this tool whenever the farmer asks about current weather,
    today's temperature, rain, rainfall, humidity, wind, or
    current weather conditions.

    Do not guess current weather information.
    """

    try:
        # Find the location
        geo_response = requests.get(
            "https://geocoding-api.open-meteo.com/v1/search",
            params={
                "name": city,
                "count": 1,
                "language": "en",
                "format": "json",
            },
            timeout=8,
        )

        geo_response.raise_for_status()
        geo_data = geo_response.json()

        if not geo_data.get("results"):
            return {
                "success": False,
                "message": f"I could not find weather information for {city}."
            }

        location = geo_data["results"][0]

        latitude = location["latitude"]
        longitude = location["longitude"]

        resolved_city = location["name"]
        country = location.get("country", "")

        # Get current weather
        weather_response = requests.get(
             "https://api.open-meteo.com/v1/forecast",
           # "https://invalid-weather-api-example.com/v1/forecast",
            params={
                "latitude": latitude,
                "longitude": longitude,
                "current": (
                    "temperature_2m,"
                    "relative_humidity_2m,"
                    "precipitation,"
                    "wind_speed_10m"
                ),
                "timezone": "auto",
            },
            timeout=8,
        )

        weather_response.raise_for_status()
        weather_data = weather_response.json()

        current = weather_data["current"]

        return {
            "success": True,
            "city": resolved_city,
            "country": country,
            "temperature": current["temperature_2m"],
            "humidity": current["relative_humidity_2m"],
            "rainfall": current["precipitation"],
            "wind_speed": current["wind_speed_10m"],
            "unit": "°C",
            "data_time": current["time"],
        }

    except requests.exceptions.Timeout:
        return {
            "success": False,
            "message": "The weather service took too long to respond."
        }

    except requests.exceptions.RequestException:
        return {
            "success": False,
            "message": "The weather service is temporarily unavailable."
        }

    except Exception:
        return {
            "success": False,
            "message": "I could not retrieve the weather information right now."
        }
