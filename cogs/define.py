import discord
from discord.ext import commands
import aiohttp

class Define(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="define", help="Get the definition of a word. Usage: /define <word>")
    async def define(self, ctx, *, word: str):
        url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    await ctx.send(f"❌ No definition found for '{word}'.")
                    return
                data = await resp.json()
                try:
                    meanings = data[0]["meanings"]
                    defs = []
                    for meaning in meanings:
                        part = meaning["partOfSpeech"]
                        for d in meaning["definitions"]:
                            defs.append(f"**{part}:** {d['definition']}")
                    defs_text = '\n'.join(defs[:3])  # Show up to 3 definitions
                    embed = discord.Embed(title=f"Definition of '{word}'", description=defs_text, color=discord.Color.green())
                    await ctx.send(embed=embed)
                except Exception:
                    await ctx.send(f"❌ Could not parse definition for '{word}'.")

def setup(bot):
    bot.add_cog(Define(bot)) 