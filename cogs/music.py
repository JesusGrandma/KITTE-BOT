import discord
from discord.ext import commands, tasks
import asyncio
import yt_dlp as youtube_dl
import time
import logging

logger = logging.getLogger(__name__)

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.voice_client = None
        self.music_playing = False
        self.last_activity_time = time.time()
        self.song_queue = []
        self.loop_enabled = False  
        self.current_song = None   

    async def join_vc(self, ctx):
        if ctx.author.voice:
            channel = ctx.author.voice.channel
            if not self.voice_client or not self.voice_client.is_connected():
                self.voice_client = await channel.connect()
                logger.info(f"Joined voice channel: {channel.name}")
            elif self.voice_client.channel != channel:
                await self.voice_client.move_to(channel)
                logger.info(f"Moved to voice channel: {channel.name}")
            return True
        await ctx.send("❌ You must be in a voice channel first!")
        return False

    async def leave_vc(self, ctx=None):
        if self.voice_client:
            await self.voice_client.disconnect()
            self.voice_client = None
            logger.info("Left voice channel")
        elif ctx:
            await ctx.send("❌ Not in a voice channel")

    async def get_youtube_audio(self, query):
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._sync_ytdl_extract, query)

    def _sync_ytdl_extract(self, query):
        ydl_opts = {
            'format': 'bestaudio/best',
            'default_search': 'ytsearch1',
            'noplaylist': True,
            'quiet': True,
            'socket_timeout': 30,
            'nocheckcertificate': True
        }
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            try:
                info = ydl.extract_info(query, download=False)
                if 'entries' in info:
                    video = info['entries'][0]
                else:
                    video = info
                return (
                    video['url'],
                    video.get('webpage_url', query),
                    video.get('title', 'Unknown Title')
                )
            except Exception as e:
                logger.error(f"YTDL Error: {str(e)}")
                raise

    @commands.command(name="play", help="Play a song from YouTube. Usage: /play <song name or URL>")
    async def play(self, ctx, *, query: str):
        """Play audio from YouTube"""
        if not await self.join_vc(ctx):
            return

        # Ensure voice_client is connected before proceeding
        if not self.voice_client or not self.voice_client.is_connected():
            await ctx.send("Not connected to voice. Please try again.")
            return

        try:
            audio_url, page_url, title = await self.get_youtube_audio(query)
            logger.info(f"Playing: {title} ({audio_url})")

            if self.voice_client.is_playing() or self.voice_client.is_paused():
                self.song_queue.append((audio_url, page_url, title))
                await ctx.send(f"🎶 Added to queue: [{title}]({page_url})")
                return

            self._play_audio(ctx, audio_url, page_url, title)
            await ctx.send(f"🎵 Now playing: [{title}]({page_url})")

        except Exception as e:
            logger.error(f"Play error: {str(e)}")
            await ctx.send(f" Error: {str(e)}")

    @commands.command(name="loop", help="Toggle looping the current song")
    async def loop(self, ctx):
        """Toggle loop for the current song."""
        self.loop_enabled = not self.loop_enabled
        if self.loop_enabled:
            await ctx.send("Loop enabled for the current song.")
        else:
            await ctx.send("Loop disabled.")

    def _play_audio(self, ctx, audio_url, page_url, title):
        self.music_playing = True
        self.last_activity_time = time.time()
        self.current_song = (audio_url, page_url, title)  # Track the current song

        ffmpeg_options = {
            'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
            'options': '-vn -b:a 128k -ac 2'
        }

        self.voice_client.play(
            discord.FFmpegOpusAudio(
                executable="ffmpeg",
                source=audio_url,
                **ffmpeg_options
            ),
            after=lambda e: self.bot.loop.create_task(self._after_play(e, ctx))
        )

    async def _after_play(self, error, ctx):
        self.music_playing = False
        if error:
            logger.error(f"Playback error: {error}")
            await ctx.send(f"❌ Playback error: {error}")

        if self.loop_enabled and self.current_song:
            # Replay the current song
            audio_url, page_url, title = self.current_song
            self._play_audio(ctx, audio_url, page_url, title)
            await ctx.send(f"Replaying: [{title}]({page_url})")
            return

        if self.song_queue:
            next_url, next_page, next_title = self.song_queue.pop(0)
            self._play_audio(ctx, next_url, next_page, next_title)
            await ctx.send(f"Now playing: [{next_title}]({next_page})")
        else:
            await self.leave_vc()

    @commands.command(name="stop", help="Stops the song and removes the bot from VC")
    async def stop(self, ctx):
        """Stop playback and clear queue"""
        if self.voice_client:
            self.song_queue.clear()
            self.voice_client.stop()
            await self.leave_vc()
            await ctx.send("Stopped playback")
        else:
            await ctx.send("Not playing anything")

    @commands.command(name="skip", help="Skips to next song in the queue")
    async def skip(self, ctx):
        """Skip current track"""
        if self.voice_client and self.voice_client.is_playing():
            self.voice_client.stop()
            await ctx.send("Skipped current track")
        else:
            await ctx.send("Nothing to skip")

    @commands.command(name="queue", help="Shows songs in queue")
    async def queue(self, ctx):
        """Show current queue"""
        if not self.song_queue:
            await ctx.send("Queue is empty")
            return

        queue_list = "\n".join(
            [f"{i+1}. [{song[2]}]({song[1]})" for i, song in enumerate(self.song_queue)]
        )
        await ctx.send(f"🎶 Current queue:\n{queue_list}")

    @tasks.loop(seconds=60)
    async def _check_inactivity(self):
        if (self.voice_client and
            not self.voice_client.is_playing() and
            (time.time() - self.last_activity_time) > 300):
            logger.info("Inactivity timeout - leaving voice channel")
            await self.leave_vc()

    @commands.Cog.listener()
    async def on_ready(self):
        self._check_inactivity.start()

async def setup(bot):
    await bot.add_cog(Music(bot))
