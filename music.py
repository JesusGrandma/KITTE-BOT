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
            self.voice_client = await channel.connect()
            print(f"Bot joined {channel.name}")
        else:
            await ctx.send("You must join a voice channel first.")

    async def leave_vc(self, ctx):
        if self.voice_client:
            await self.voice_client.disconnect()
            self.voice_client = None
            print("Bot has left the voice channel.")
        elif ctx:
            await ctx.send("I'm not in a voice channel!")

    def get_youtube_audio(self, url):
        ydl_opts = {
            'format': 'bestaudio/best',
            'extractaudio': True,
            'audioquality': 1,
            'outtmpl': 'downloads/%(id)s.%(ext)s',
            'restrictfilenames': True,
            'noplaylist': True,
            'quiet': True,
            'logtostderr': False,
            'forcegeneric': True
        }

        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            if 'formats' in info:
                audio_url = next(
                    (item['url'] for item in info['formats'] if 'acodec' in item and item['acodec'] != 'none'),
                    None
                )
                if audio_url:
                    print(f"Audio URL: {audio_url}")
                    return audio_url
                else:
                    raise ValueError("No valid audio stream found.")
            else:
                raise ValueError("Unable to extract info from URL.")

    @commands.command(name="search", help="Searches YouTube and asks if you'd like to play it.")
    async def search(self, ctx, *, query: str):
        ydl_opts = {
            'format': 'bestaudio/best',
            'noplaylist': True,
            'quiet': True,
            'default_search': 'ytsearch1',
        }

        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            try:
                info = ydl.extract_info(query, download=False)
                if 'entries' in info and len(info['entries']) > 0:
                    video = info['entries'][0]
                    url = video['webpage_url']
                    message = await ctx.send(f"Top result for **{query}**:\n{url}\nReact with ▶️ to play or ❌ to cancel.")
                    await message.add_reaction('▶️')
                    await message.add_reaction('❌')

                    def check(reaction, user):
                        return user == ctx.author and str(reaction.emoji) in ['▶️', '❌'] and reaction.message.id == message.id

                    try:
                        reaction, user = await self.bot.wait_for('reaction_add', timeout=30.0, check=check)
                        if str(reaction.emoji) == '▶️':
                            await ctx.invoke(self.bot.get_command("play"), url=url)
                        else:
                            await ctx.send("Cancelled.")
                    except asyncio.TimeoutError:
                        await ctx.send("Timed out.")
                else:
                    await ctx.send("No results found.")
            except Exception as e:
                await ctx.send(f"Search failed: {e}")

    @commands.command(name="play", help="Plays a song from YouTube")
    async def play(self, ctx, url: str):
        await self.join_vc(ctx)

        try:
            audio_url = self.get_youtube_audio(url)
        except ValueError as e:
            await ctx.send(str(e))
            return

        if self.voice_client.is_playing() or self.voice_client.is_paused():
            self.song_queue.append(audio_url)
            await ctx.send(f"Added to queue: {url}")
            return

        self.music_playing = True
        self.last_activity_time = time.time()
        self.voice_client.play(
            discord.FFmpegPCMAudio(audio_url, before_options='-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5'),
            after=self.after_play
        )
        await ctx.send(f"Now playing: {url}")

    def after_play(self, error):
        if error:
            print(f"Error: {error}")
        self.music_playing = False

        if self.song_queue:
            next_song = self.song_queue.pop(0)
            self.last_activity_time = time.time()
            self.voice_client.play(
                discord.FFmpegPCMAudio(next_song, before_options='-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5'),
                after=self.after_play
            )

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
