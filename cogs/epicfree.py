import discord
from discord.ext import commands
import aiohttp

class EpicFree(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="epicfree", help="Shows the current free game(s) on Epic Games Store")
    async def epicfree(self, ctx):
        url = "https://store-site-backend-static.ak.epicgames.com/freeGamesPromotions?locale=en-US&country=US&allowCountries=US"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    if resp.status != 200:
                        await ctx.send("❌ Failed to fetch Epic Games data.")
                        return
                    data = await resp.json()

            games = data["data"]["Catalog"]["searchStore"]["elements"]
            free_games = []
            for game in games:
                promotions = game.get("promotions")
                if not promotions:
                    continue
                offers = promotions.get("promotionalOffers", [])
                if offers and offers[0].get("promotionalOffers"):
                    offer = offers[0]["promotionalOffers"][0]
                    if offer.get("discountSetting", {}).get("discountPercentage") == 0:
                        free_games.append(game)

            if not free_games:
                await ctx.send("No free games found right now.")
                return

            for game in free_games:
                title = game.get("title", "Unknown Title")
                desc = game.get("description", "No description available.")
                product_slug = game.get("productSlug")
                url = f"https://store.epicgames.com/en-US/p/{product_slug}" if product_slug else "https://store.epicgames.com/en-US/free-games"
                embed = discord.Embed(title=title, description=desc, url=url, color=discord.Color.blue())
                embed.add_field(name="Link", value=f"[View on Epic Games Store]({url})", inline=False)
                await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"❌ Error: {str(e)}")

def setup(bot):
    bot.add_cog(EpicFree(bot)) 