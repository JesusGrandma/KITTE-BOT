import discord
from discord.ext import commands
import aiohttp

class RandomDog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="dog", help="Sends a random dog image")
    async def dog(self, ctx):
        async with aiohttp.ClientSession() as session:
            async with session.get("https://random.dog/woof.json") as resp:
                if resp.status != 200:
                    await ctx.send("Could not fetch dog image at this time. Please try again later.")
                    return
                data = await resp.json()
                url = data["url"]
                # Filter out videos
                if url.endswith(('.mp4', '.webm')):
                    # Try again recursively (could also loop, but recursion is simple here)
                    await self.dog(ctx)
                    return
                embed = discord.Embed(title="Here's a random dog:", color=discord.Color.orange())
                embed.set_image(url=url)
                await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(RandomDog(bot))
