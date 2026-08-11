import requests


def get_weather(city: str) -> dict:
    """
    Get current and upcoming weather information for a city or district.

    This tool provides:
    - Current weather
    - Today's forecast
    - Tomorrow's forecast
    - Tomorrow's rain probability

    Use this tool whenever the farmer asks about:
    - current weather
    - today's weather
    - tomorrow's weather
    - rain
    - rainfall
    - temperature
    - humidity
    - wind
    """

    try:
        # ----------------------------------------------------
        # Find the location
        # ----------------------------------------------------

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
                "message": (
                    f"I could not find weather information "
                    f"for {city}."
                ),
            }

        location = geo_data["results"][0]

        latitude = location["latitude"]
        longitude = location["longitude"]

        resolved_city = location["name"]
        country = location.get("country", "")

        # ----------------------------------------------------
        # Get current + forecast weather
        # ----------------------------------------------------

        weather_response = requests.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": latitude,
                "longitude": longitude,

                # Current weather
                "current": (
                    "temperature_2m,"
                    "relative_humidity_2m,"
                    "precipitation,"
                    "wind_speed_10m"
                ),

                # Daily forecast
                "daily": (
                    "temperature_2m_max,"
                    "temperature_2m_min,"
                    "precipitation_probability_max,"
                    "precipitation_sum,"
                    "wind_speed_10m_max"
                ),

                # Tomorrow requires forecast data
                "forecast_days": 2,

                "timezone": "auto",
            },
            timeout=8,
        )

        weather_response.raise_for_status()

        weather_data = weather_response.json()

        # ----------------------------------------------------
        # Current weather
        # ----------------------------------------------------

        current = weather_data["current"]

        # ----------------------------------------------------
        # Daily forecast
        # ----------------------------------------------------

        daily = weather_data["daily"]

        # Index 0 = today
        # Index 1 = tomorrow

        tomorrow_index = 1

        tomorrow_date = daily["time"][tomorrow_index]

        tomorrow_max_temp = daily[
            "temperature_2m_max"
        ][tomorrow_index]

        tomorrow_min_temp = daily[
            "temperature_2m_min"
        ][tomorrow_index]

        tomorrow_rain_probability = daily[
            "precipitation_probability_max"
        ][tomorrow_index]

        tomorrow_rainfall = daily[
            "precipitation_sum"
        ][tomorrow_index]

        tomorrow_wind = daily[
            "wind_speed_10m_max"
        ][tomorrow_index]

        # ----------------------------------------------------
        # Return weather information
        # ----------------------------------------------------

        return {
            "success": True,

            "city": resolved_city,

            "country": country,

            # Current weather
            "current": {
                "temperature": current[
                    "temperature_2m"
                ],
                "humidity": current[
                    "relative_humidity_2m"
                ],
                "rainfall": current[
                    "precipitation"
                ],
                "wind_speed": current[
                    "wind_speed_10m"
                ],
                "data_time": current["time"],
            },

            # Tomorrow's forecast
            "tomorrow": {
                "date": tomorrow_date,

                "min_temperature": tomorrow_min_temp,

                "max_temperature": tomorrow_max_temp,

                "rain_probability": (
                    tomorrow_rain_probability
                ),

                "rainfall": tomorrow_rainfall,

                "max_wind_speed": tomorrow_wind,
            },

            "unit": "°C",
        }

    except requests.exceptions.Timeout:

        return {
            "success": False,
            "message": (
                "The weather service took too long "
                "to respond."
            ),
        }

    except requests.exceptions.RequestException:

        return {
            "success": False,
            "message": (
                "The weather service is temporarily "
                "unavailable."
            ),
        }

    except Exception as e:

        print(
            f"Weather tool error: {e}"
        )

        return {
            "success": False,
            "message": (
                "I could not retrieve the weather "
                "information right now."
            ),
        }
