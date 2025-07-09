from discord.ext import commands
import discord

class GifCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="nip", help="Send a benny nip gif by link")
    async def nip(self, ctx):
        gif_url = "https://media1.giphy.com/media/v1.Y2lkPTc5MGI3NjExNG10dzgzaXNhb2s5Nm5vZ3lnMHo2dnh4dG1vOHF2ZGE2dXYxc2dtaiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/YUQzKWdsTpq0DroDNr/giphy.gif"  # Replace with your desired GIF link
        await ctx.send(gif_url)

async def setup(bot):
    await bot.add_cog(GifCommands(bot))
