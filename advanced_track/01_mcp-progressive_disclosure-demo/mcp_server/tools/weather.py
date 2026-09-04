"""Read-only-Wettertools mit festen, simulierten Workshop-Daten."""

from mcp_server.server import mcp


@mcp.tool
def get_weather(city: str) -> dict:
    """
    Get the current weather for a city.

    Use this tool when the user asks about current temperature,
    weather conditions, precipitation or general weather information.

    Args:
        city: Name of the city.

    Returns:
        Current temperature and weather condition.
    """
    return {
        "city": city,
        "temperature": 21,
        "condition": "sunny",
        "humidity": 65,
        "wind_speed": 12,
    }


@mcp.tool
def get_forecast(city: str, days: int = 3) -> list[dict]:
    """
    Get the weather forecast for a city for the next N days.

    Use this tool when the user wants to know future weather conditions,
    like tomorrow's weather or the weekend forecast.

    Args:
        city: Name of the city.
        days: Number of days to forecast (1-7, default 3).

    Returns:
        List of daily forecast entries.
    """
    conditions = ["sunny", "cloudy", "rainy", "partly cloudy", "clear"]
    return [
        {
            "day": i + 1,
            "city": city,
            "temperature_high": 20 + i,
            "temperature_low": 12 + i,
            "condition": conditions[i % len(conditions)],
        }
        for i in range(min(days, 7))
    ]


@mcp.tool
def get_humidity(city: str) -> dict:
    """
    Get the current humidity level for a city.

    Use this tool when the user specifically asks about humidity,
    moisture levels or dew point.

    Args:
        city: Name of the city.

    Returns:
        Humidity percentage and dew point.
    """
    return {
        "city": city,
        "humidity": 65,
        "dew_point": 14,
    }


@mcp.tool
def get_temperature(city: str) -> dict:
    """
    Get the current temperature for a city.

    Use this tool when the user asks specifically about temperature
    (in Celsius or Fahrenheit), without needing full weather data.

    Args:
        city: Name of the city.

    Returns:
        Temperature in Celsius and Fahrenheit.
    """
    celsius = 21
    return {
        "city": city,
        "celsius": celsius,
        "fahrenheit": celsius * 9 // 5 + 32,
    }


@mcp.tool
def get_wind_speed(city: str) -> dict:
    """
    Get the current wind speed and direction for a city.

    Use this tool when the user asks about wind, breeze, storms
    or air movement.

    Args:
        city: Name of the city.

    Returns:
        Wind speed in km/h and direction.
    """
    return {
        "city": city,
        "wind_speed_kmh": 12,
        "wind_direction": "NW",
        "gusts_kmh": 25,
    }


@mcp.tool
def get_precipitation(city: str) -> dict:
    """
    Get the current precipitation data for a city.

    Use this tool when the user asks about rain, snow, hail
    or general precipitation.

    Args:
        city: Name of the city.

    Returns:
        Precipitation amount in mm and probability.
    """
    return {
        "city": city,
        "precipitation_mm": 0,
        "probability": 10,
        "type": "none",
    }


@mcp.tool
def get_uv_index(city: str) -> dict:
    """
    Get the current UV index for a city.

    Use this tool when the user asks about sun exposure, UV radiation,
    sunscreen recommendations or sun safety.

    Args:
        city: Name of the city.

    Returns:
        UV index value and risk level.
    """
    return {
        "city": city,
        "uv_index": 5,
        "risk_level": "moderate",
        "protection_required": True,
    }


@mcp.tool
def get_air_quality(city: str) -> dict:
    """
    Get the current air quality index for a city.

    Use this tool when the user asks about air quality, pollution,
    smog, AQI or air purity.

    Args:
        city: Name of the city.

    Returns:
        Air quality index and pollutant details.
    """
    return {
        "city": city,
        "aqi": 42,
        "category": "good",
        "pm25": 8,
        "pm10": 15,
        "o3": 45,
    }


@mcp.tool
def get_weather_alerts(city: str) -> list[dict]:
    """
    Get active weather alerts for a city.

    Use this tool when the user asks about weather warnings, alerts,
    storms, heatwaves or other weather-related hazards.

    Args:
        city: Name of the city.

    Returns:
        List of active weather alerts (empty if none).
    """
    return [
        {
            "city": city,
            "alert_type": "none",
            "severity": "low",
            "message": "No active weather alerts.",
        }
    ]


@mcp.tool
def get_sunrise_sunset(city: str) -> dict:
    """
    Get sunrise and sunset times for a city.

    Use this tool when the user asks about daylight hours, sunrise,
    sunset, golden hour or twilight times.

    Args:
        city: Name of the city.

    Returns:
        Sunrise and sunset times in local timezone.
    """
    return {
        "city": city,
        "sunrise": "06:42",
        "sunset": "20:15",
        "daylight_hours": 13.5,
    }
