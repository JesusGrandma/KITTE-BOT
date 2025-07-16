import discord
from discord.ext import commands
import aiohttp

class Urban(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="urban", help="Get a slang definition from Urban Dictionary. Usage: /urban <word>")
    async def urban(self, ctx, *, word: str):
        url = f"https://api.urbandictionary.com/v0/define?term={word}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    await ctx.send(f"❌ No Urban Dictionary entry found for '{word}'.")
                    return
                data = await resp.json()
                try:
                    if not data["list"]:
                        await ctx.send(f"❌ No Urban Dictionary entry found for '{word}'.")
                        return
                    entry = data["list"][0]
                    definition = entry["definition"].replace("[", "").replace("]", "")
                    example = entry["example"].replace("[", "").replace("]", "")
                    embed = discord.Embed(title=f"Urban Dictionary: {word}", description=definition, color=discord.Color.blue())
                    if example:
                        embed.add_field(name="Example", value=example, inline=False)
                    await ctx.send(embed=embed)
                except Exception:
                    await ctx.send(f"❌ Could not parse Urban Dictionary entry for '{word}'.")

    @commands.command(name="urbanrandom", help="Get a random Urban Dictionary entry. Usage: /urbanrandom")
    async def urbanrandom(self, ctx):
        url = "https://api.urbandictionary.com/v0/random"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    await ctx.send("❌ Could not fetch a random Urban Dictionary entry.")
                    return
                data = await resp.json()
                try:
                    if not data["list"]:
                        await ctx.send("❌ No random Urban Dictionary entries found.")
                        return
                    entry = data["list"][0]
                    word = entry["word"]
                    definition = entry["definition"].replace("[", "").replace("]", "")
                    example = entry["example"].replace("[", "").replace("]", "")
                    embed = discord.Embed(title=f"Urban Dictionary: {word}", description=definition, color=discord.Color.blue())
                    if example:
                        embed.add_field(name="Example", value=example, inline=False)
                    await ctx.send(embed=embed)
                except Exception:
                    await ctx.send("❌ Could not parse random Urban Dictionary entry.")

def setup(bot):
    bot.add_cog(Urban(bot)) 