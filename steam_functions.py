import os
import aiohttp
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
steam_api_key = os.getenv("STEAM_API_KEY")

if not steam_api_key:
    raise ValueError("Missing STEAM_API_KEY in .env")

class Steam(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="steamprofile", help="Get Steam profile info using SteamID64 or vanity URL name")
    async def steam_profile(self, ctx, *, identifier):
        base_url = "http://api.steampowered.com"

        # Step 1: Resolve Vanity URL if needed
        if identifier.isdigit():
            steam_id = identifier
        else:
            steam_id = await self.resolve_vanity_url(identifier)
            if not steam_id:
                await ctx.send("❌ Could not resolve that Steam username.")
                return

        # Step 2: Get Player Summary
        profile_url = f"{base_url}/ISteamUser/GetPlayerSummaries/v0002/?key={steam_api_key}&steamids={steam_id}"
        async with aiohttp.ClientSession() as session:
            async with session.get(profile_url) as response:
                data = await response.json()
                players = data.get("response", {}).get("players", [])
                if not players:
                    await ctx.send("❌ Steam profile not found.")
                    return

                player = players[0]
                embed = discord.Embed(title=player["personaname"], url=player["profileurl"], color=discord.Color.blue())
                embed.set_thumbnail(url=player["avatarfull"])
                embed.add_field(name="Real Name", value=player.get("realname", "N/A"), inline=True)
                embed.add_field(name="Country", value=player.get("loccountrycode", "N/A"), inline=True)
                embed.add_field(name="Status", value=self._get_persona_state(player["personastate"]), inline=True)
                await ctx.send(embed=embed)

    async def resolve_vanity_url(self, vanity_name):
        url = f"http://api.steampowered.com/ISteamUser/ResolveVanityURL/v0001/?key={steam_api_key}&vanityurl={vanity_name}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                data = await response.json()
                if data["response"]["success"] == 1:
                    return data["response"]["steamid"]
                return None

    def _get_persona_state(self, state):
        states = {
            0: "Offline",
            1: "Online",
            2: "Busy",
            3: "Away",
            4: "Snooze",
            5: "Looking to Trade",
            6: "Looking to Play"
        }
        return states.get(state, "Unknown")

async def setup(bot):
    await bot.add_cog(Steam(bot))
