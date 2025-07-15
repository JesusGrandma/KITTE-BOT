import os
import discord
from discord.ext import commands
import aiohttp

class WeatherCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.api_key = os.getenv("WEATHER_API_KEY")
        if not self.api_key:
            raise ValueError("WEATHER_API_KEY environment variable not set.")

    async def get_weather(self, city):
        url = "http://api.weatherapi.com/v1/current.json"
        params = {
            "key": self.api_key,
            "q": city,
            "aqi": "no"
        }
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as resp:
                if resp.status != 200:
                    return None
                return await resp.json()

    @commands.command(name="weather", help="Get the current weather for a city. Usage: /weather <city>")
    async def weather(self, ctx, *, city: str):
        """Get the current weather for a city."""
        data = await self.get_weather(city)
        if data is None or "error" in data:
            await ctx.send("❌ Couldn't fetch weather data. Please check the city name.")
            return

        location = data['location']['name']
        country = data['location']['country']
        condition = data['current']['condition']['text']
        temp_f = data['current']['temp_f']
        feelslike_f = data['current']['feelslike_f']
        humidity = data['current']['humidity']
        wind_kph = data['current']['wind_kph']

        embed = discord.Embed(
            title=f"Weather in {location}, {country}",
            description=condition,
            color=discord.Color.blue()
        )
        embed.add_field(name="Temperature", value=f"{temp_f}°F (Feels like {feelslike_f}°F)")
        embed.add_field(name="Humidity", value=f"{humidity}%")
        embed.add_field(name="Wind", value=f"{wind_kph} kph")
        embed.set_thumbnail(url=f"http:{data['current']['condition']['icon']}")

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(WeatherCog(bot))
