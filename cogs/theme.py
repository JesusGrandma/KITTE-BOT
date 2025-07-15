import discord
from discord.ext import commands
import os
import asyncio

class Theme(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="theme", help="Play KITTE Bot's Theme")
    async def play_theme(self, ctx):
        if not ctx.author.voice or not ctx.author.voice.channel:
            await ctx.send("❌ You must be in a voice channel.")
            return

        vc = ctx.author.voice.channel

        # Connect to voice channel
        voice_client = await vc.connect()

        # Check audio file
        audio_file = "theme_song/KITTIE.mp3"
        if not os.path.exists(audio_file):
            await ctx.send("❌ Audio file not found.")
            await voice_client.disconnect()
            return

        # Play audio using FFMPEG
        source = discord.FFmpegPCMAudio(audio_file)
        voice_client.play(source)

        await ctx.send("**Now Playing:** __KITTE Bot's Theme__")

        # Wait for audio to finish
        while voice_client.is_playing():
            await asyncio.sleep(1)

        await voice_client.disconnect()
        

    @commands.command(name="leave", help="Force the bot to leave the voice channel")
    async def leave(self, ctx):
        voice_client = ctx.guild.voice_client
        if voice_client and voice_client.is_connected():
            await voice_client.disconnect()
            await ctx.send("Disconnected from the voice channel.")
        else:
            await ctx.send("I'm not connected to a voice channel.")

async def setup(bot):
    await bot.add_cog(Theme(bot))
