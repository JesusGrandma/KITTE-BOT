from discord.ext import commands
import discord
import os

class GifCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="nip", help="benny nip gif")
    async def nip(self, ctx):
        gif_path = "gifs/henigin1.gif"
        if not os.path.isfile(gif_path):
            await ctx.send("❌ GIF file not found.")
            return
        file = discord.File(gif_path)
        await ctx.send(file=file)

async def setup(bot):
    await bot.add_cog(GifCommands(bot))
