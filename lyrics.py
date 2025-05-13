import os
import discord
from discord.ext import commands
import lyricsgenius
from dotenv import load_dotenv

load_dotenv()
GENIUS_TOKEN = os.getenv("GENIUS_ACCESS_TOKEN")
genius = lyricsgenius.Genius(GENIUS_TOKEN)

class Lyrics(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="lyrics", help="Get the lyrics of a song")
    async def get_lyrics(self, ctx, *, query: str):
        try:
            song = genius.search_song(query)
            if song:
                lyrics = song.lyrics
                if len(lyrics) > 1900:
                    await ctx.send(f"Lyrics too long to display. Here's a link instead:\n{song.url}")
                else:
                    await ctx.send(f"**{song.title}** by **{song.artist}**\n\n{lyrics}")
            else:
                await ctx.send("❌ No lyrics found.")
        except Exception as e:
            await ctx.send(f"❌ Error: {str(e)}")

async def setup(bot):
    await bot.add_cog(Lyrics(bot))
