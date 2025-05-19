import discord
from discord.ext import commands
import os
import asyncio

class RushB(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="rushb", help="Cyka Blyat Rush B")
    async def rushb(self, ctx):
        if not ctx.author.voice or not ctx.author.voice.channel:
            await ctx.send("❌ You must be in a voice channel.")
            return

        vc = ctx.author.voice.channel

        # Connect to voice channel
        voice_client = await vc.connect()

        # Check audio file
        audio_file = "sounds/rush_b.mp3"
        if not os.path.exists(audio_file):
            await ctx.send("❌ Audio file not found.")
            await voice_client.disconnect()
            return

        # Play audio using FFMPEG
        source = discord.FFmpegPCMAudio(audio_file)
        voice_client.play(source)

        await ctx.send("**СУКА БЛЯТЬ, РАШ Б! ЗА РОДИНУ!**")

        # Wait for audio to finish
        while voice_client.is_playing():
            await asyncio.sleep(1)

        await voice_client.disconnect()

async def setup(bot):
    await bot.add_cog(RushB(bot))
