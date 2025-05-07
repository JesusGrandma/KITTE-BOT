import discord
from discord.ext import commands, tasks
import asyncio
import yt_dlp as youtube_dl
import time

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.voice_client = None
        self.music_playing = False
        self.last_activity_time = time.time()
        self.song_queue = []  # Queue to handle multiple songs

    async def join_vc(self, ctx):
        if ctx.author.voice:
            channel = ctx.author.voice.channel
            self.voice_client = await channel.connect()
            print(f"Bot joined {channel.name}")
        else:
            await ctx.send("You must join a voice channel first.")

    async def leave_vc(self, ctx):
        if self.voice_client:
            await self.voice_client.disconnect()
            print("Bot has left the voice channel.")
        else:
            await ctx.send("I'm not in a voice channel!")

    def get_youtube_audio(self, url):
        ydl_opts = {
            'format': 'bestaudio/best',  # Ensure we get the best audio format
            'extractaudio': True,        # Extract audio
            'audioquality': 1,           # Best audio quality
            'outtmpl': 'downloads/%(id)s.%(ext)s',  # Output template
            'restrictfilenames': True,   # Restrict filenames to be safe
            'noplaylist': True,          # Avoid playlists
            'quiet': True,               # Silence logs
            'logtostderr': False,        # Disable stderr logging
            'forcegeneric': True         # Ensure generic audio format extraction
        }

        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            # Extract the audio URL directly from the info dictionary
            if 'formats' in info:
                # Select the audio stream with the best quality
                audio_url = next(
                    (item['url'] for item in info['formats'] if 'acodec' in item and item['acodec'] != 'none'), 
                    None
                )
                if audio_url:
                    print(f"Audio URL: {audio_url}")  # Log the URL to debug
                    return audio_url
                else:
                    raise ValueError("No valid audio stream found.")
            else:
                raise ValueError("Unable to extract info from URL.")

    @commands.command(name="play", help="Plays a song from YouTube")
    async def play(self, ctx, url: str):
        await self.join_vc(ctx)

        # Get the audio URL
        try:
            audio_url = self.get_youtube_audio(url)
        except ValueError as e:
            await ctx.send(str(e))
            return

        if self.voice_client.is_playing():
            self.song_queue.append(audio_url)
            await ctx.send(f"Added to queue: {url}")
            return

        # Play the audio
        self.music_playing = True
        self.last_activity_time = time.time()
        self.voice_client.play(discord.FFmpegPCMAudio(audio_url, **{'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5'}), after=self.after_play)
        await ctx.send(f"Now playing: {url}")

    def after_play(self, error):
        """Callback after a song finishes."""
        if error:
            print(f"Error: {error}")
        self.music_playing = False

        if self.song_queue:
            # Play the next song in the queue
            next_song = self.song_queue.pop(0)
            self.voice_client.play(discord.FFmpegPCMAudio(next_song, **{'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5'}), after=self.after_play)

    @commands.command(name="stop", help="Stops the current song and leaves the voice channel.")
    async def stop(self, ctx):
        if self.voice_client and self.music_playing:
            self.music_playing = False
            self.voice_client.stop()
            await self.leave_vc(ctx)
            await ctx.send("Stopped and left the voice channel.")
        else:
            await ctx.send("No music is currently playing.")

    @commands.command(name="pause", help="Pauses the currently playing song.")
    async def pause(self, ctx):
        if self.voice_client and self.voice_client.is_playing():
            self.voice_client.pause()
            await ctx.send("Paused the song.")
        else:
            await ctx.send("No music is currently playing.")

    @commands.command(name="resume", help="Resumes the paused song.")
    async def resume(self, ctx):
        if self.voice_client and self.voice_client.is_paused():
            self.voice_client.resume()
            await ctx.send("Resumed the song.")
        else:
            await ctx.send("No song is currently paused.")

    @tasks.loop(seconds=60)
    async def check_idle(self):
        """Check if the bot has been idle for too long and leave the voice channel"""
        if self.voice_client and time.time() - self.last_activity_time > 300:  # 5 minutes
            if not self.music_playing:
                print("No activity for 5 minutes, leaving voice channel.")
                await self.leave_vc(None)  # We can pass None since we're not responding to a specific command here

    @commands.Cog.listener()
    async def on_ready(self):
        """Starts the idle check loop when the bot is ready."""
        self.check_idle.start()

async def setup(bot):
    await bot.add_cog(music(bot))
