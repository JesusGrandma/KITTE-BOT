import os
import aiohttp

async def get_weather(city, session):
    WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")  # <-- moved inside function
    url = "http://api.weatherapi.com/v1/current.json"
    params = {
        "key": WEATHER_API_KEY,
        "q": city,
        "aqi": "no"
    }
    async with session.get(url, params=params) as resp:
        if resp.status != 200:
            return None
        data = await resp.json()
        return data
