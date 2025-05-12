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
        self.song_queue = []

    async def join_vc(self, ctx):
        if ctx.author.voice:
            channel = ctx.author.voice.channel
            if not self.voice_client or not self.voice_client.is_connected():
                self.voice_client = await channel.connect()
                print(f"Bot joined {channel.name}")
            elif self.voice_client.channel != channel:
                await self.voice_client.move_to(channel)
                print(f"Bot moved to {channel.name}")
        else:
            await ctx.send("You must join a voice channel first.")

    async def leave_vc(self, ctx):
        if self.voice_client:
            await self.voice_client.disconnect()
            self.voice_client = None
            print("Bot has left the voice channel.")
        elif ctx:
            await ctx.send("I'm not in a voice channel!")

    def get_youtube_audio(self, query):
        ydl_opts = {
            'format': 'bestaudio/best',
            'default_search': 'ytsearch1',  # This enables keyword search
            'noplaylist': True,
            'quiet': True,
        }
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(query, download=False)
            # If it's a search, info will have 'entries'
            if 'entries' in info and info['entries']:
                video = info['entries'][0]
                return video['url'], video['webpage_url'], video['title']
            # If it's a direct URL
            return info['url'], info.get('webpage_url', query), info.get('title', 'Unknown Title')

    @commands.command(name="play", help="Play music from YouTube by URL or search keywords.")
    async def play(self, ctx, *, query: str):
        if not ctx.author.voice:
            await ctx.send("You must join a voice channel first.")
            return

        await self.join_vc(ctx)
        
        try:
            # If not a URL, yt-dlp will handle it as a search due to default_search
            audio_url, page_url, title = self.get_youtube_audio(query)
            
            if self.voice_client.is_playing() or self.voice_client.is_paused():
                self.song_queue.append((audio_url, page_url, title))
                await ctx.send(f"Added to queue: [{title}]({page_url})")
                return

            self.music_playing = True
            self.last_activity_time = time.time()
            self.voice_client.play(
                discord.FFmpegPCMAudio(audio_url, before_options='-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5'),
                after=lambda e: self.bot.loop.create_task(self.after_play(e, ctx))
            )
            await ctx.send(f"Now playing: [{title}]({page_url})")

        except Exception as e:
            await ctx.send(f"Error: {str(e)}")

    async def after_play(self, error, ctx):
        if error:
            print(f"Error: {error}")
        self.music_playing = False
        if self.song_queue:
            next_song = self.song_queue.pop(0)
            audio_url, page_url, title = next_song
            self.last_activity_time = time.time()
            self.voice_client.play(
                discord.FFmpegPCMAudio(audio_url, before_options='-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5'),
                after=lambda e: self.bot.loop.create_task(self.after_play(e, ctx))
            )
            await ctx.send(f"Now playing: [{title}]({page_url})")

    @commands.command(name="stop", help="Stops the current song and leaves the voice channel.")
    async def stop(self, ctx):
        if self.voice_client and (self.voice_client.is_playing() or self.voice_client.is_paused()):
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
        if self.voice_client and not self.voice_client.is_playing() and not self.voice_client.is_paused():
            if time.time() - self.last_activity_time > 300:
                print("Idle timeout reached, leaving VC.")
                await self.leave_vc(None)

    @commands.Cog.listener()
    async def on_ready(self):
        self.check_idle.start()

async def setup(bot):
    await bot.add_cog(Music(bot))
