import discord
from discord.ext import commands
import aiohttp

class RandomJoke(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="joke", help="Tells a random joke")
    async def joke(self, ctx):
        url = "https://v2.jokeapi.dev/joke/Miscellaneous,Dark,Pun?blacklistFlags=nsfw,racist,sexist"

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    await ctx.send("Couldn't fetch a joke right now. Try again later.")
                    return

                data = await resp.json()

                if data["type"] == "single":
                    # One-liner joke
                    joke_text = data["joke"]
                else:
                    # Two-part joke (setup + delivery)
                    joke_text = f"{data['setup']}\n\n||{data['delivery']}||"

                embed = discord.Embed(
                    title="KITTE make joke:",
                    description=joke_text,
                    color=discord.Color.orange()
                )
                await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(RandomJoke(bot))
