import discord
from discord.ext import commands
from dotenv import load_dotenv
import os

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

bot = commands.Bot(command_prefix="/", intents=intents, help_command=None)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

@bot.command(help="Replies with Pong!")
async def ping(ctx):
    await ctx.send("Pong!")

@bot.command(name="help",help="General help command")
async def help_command(ctx):
    embed = discord.Embed(title="🐱 KITTIE-BOT Commands", color=discord.Color.purple())
    
    cogs = {}
    for command in bot.commands:
        if command.hidden:
            continue
        cog_name = command.cog_name or "General"
        if cog_name not in cogs:
            cogs[cog_name] = []
        cogs[cog_name].append(command)

    for cog_name, commands_list in cogs.items():
        value = "\n".join(f"`/{cmd.name}` - {cmd.help or 'No description'}" for cmd in commands_list)
        embed.add_field(name=f"🐱 {cog_name}", value=value, inline=False)

    await ctx.send(embed=embed)


# Just regular function (not async)
def load_extensions():
    bot.load_extension("music")
    bot.load_extension("reddit_memes")

# Main
if __name__ == "__main__":
    load_extensions()
    bot.run(TOKEN)
