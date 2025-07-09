import discord
from discord.ext import commands

class ServerStats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name="serverstats",
        help="Displays statistics about the server, such as member count, online members, channels, and creation date.",
        brief="Shows server statistics."
    )
    async def serverstats(self, ctx):
        guild = ctx.guild
        total_members = guild.member_count
        text_channels = len(guild.text_channels)
        voice_channels = len(guild.voice_channels)
        online_members = sum(1 for m in guild.members if m.status == discord.Status.online)
        embed = discord.Embed(
            title=f"Server Stats - {guild.name}",
            color=discord.Color.green()
        )
        embed.add_field(name="Total Members", value=total_members)
        embed.add_field(name="Online Members", value=online_members)
        embed.add_field(name="Text Channels", value=text_channels)
        embed.add_field(name="Voice Channels", value=voice_channels)
        embed.add_field(name="Server Created", value=guild.created_at.strftime("%Y-%m-%d"))
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(ServerStats(bot))

