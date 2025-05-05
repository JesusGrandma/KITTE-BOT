import discord
from discord.ext import commands
import asyncio
import yt_dlp

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="play", help="Plays music from a YouTube URL")
    async def play(self, ctx, url: str):
        # Check if user is in a voice channel
        if not ctx.author.voice:
            await ctx.send("You need to be in a voice channel to play music.")
            return

        voice_channel = ctx.author.voice.channel

        # Connect to VC if not already
        if not ctx.voice_client:
            await voice_channel.connect()
        elif ctx.voice_client.channel != voice_channel:
            await ctx.voice_client.move_to(voice_channel)

        vc = ctx.voice_client

        # Download audio stream with yt-dlp
        ydl_opts = {
            'format': 'bestaudio/best',
            'quiet': True,
            'noplaylist': True,
            'extract_flat': 'in_playlist',
            'default_search': 'auto',
            'outtmpl': 'song.%(ext)s',
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            url2 = info['url']

        # Stop current audio if needed
        if vc.is_playing():
            vc.stop()

        # Play audio
        ffmpeg_options = {
            'options': '-vn'
        }
        vc.play(discord.FFmpegPCMAudio(url2, **ffmpeg_options))

        await ctx.send(f"Now playing: {info.get('title')}")

def setup(bot):
    bot.add_cog(Music(bot))
