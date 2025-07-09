from discord.ext import commands
import discord

class GifCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="nip", help="Send a benny nip gif by link")
    async def nip(self, ctx):
        gif_url = "https://media1.giphy.com/media/v1.Y2lkPTc5MGI3NjExNG10dzgzaXNhb2s5Nm5vZ3lnMHo2dnh4dG1vOHF2ZGE2dXYxc2dtaiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/YUQzKWdsTpq0DroDNr/giphy.gif"
        await ctx.send(gif_url)

    @commands.command(name="dmonkey", help="monke dance")
    async def dance(self, ctx):
        gif_url = "https://media4.giphy.com/media/v1.Y2lkPTc5MGI3NjExbG5sa2psaDM3MXA2cTg4aXYyNmFhZW92Ym9iYzBjM2ttNWk3cjUzOCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/M8kTFe827hE6c8GeN9/giphy.gif"
        await ctx.send(gif_url)

    @commands.command(name="throat", help="dave")
    async def dance(self, ctx):
        gif_url = "https://media3.giphy.com/media/v1.Y2lkPTc5MGI3NjExY295dmxuanNzaGkwZXp1cjdiMXFsMDY5emppYjJscGhwd3kzYTFleCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/ViJwRZ8bvMTT73YAMC/giphy.gif"  
        await ctx.send(gif_url)

async def setup(bot):
    await bot.add_cog(GifCommands(bot))
