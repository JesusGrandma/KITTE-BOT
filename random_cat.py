import discord
from discord.ext import commands
import aiohttp

class RandomCat(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="cat", help="Sends a random cat image")
    async def cat(self, ctx):
        url = "https://api.thecatapi.com/v1/images/search"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    await ctx.send("Could not fetch cat image at this time. Please try again later.")
                    return
                data = await resp.json()
                image_url = data[0]["url"]  # Extract the image URL
                embed = discord.Embed(
                    title="Here's a random cat:",
                    color=discord.Color.orange()
                )
                embed.set_image(url=image_url)
                await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(RandomCat(bot))
