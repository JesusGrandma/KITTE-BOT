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

@bot.command(name="help")
async def help_command(ctx):
    help_text = "**🎵 Available Commands:**\n\n"
    for command in bot.commands:
        help_text += f"`/{command.name}` - {command.help or 'No description'}\n"
    await ctx.send(help_text)

# Just regular function (not async)
def load_extensions():
    bot.load_extension("music")
    bot.load_extension("reddit_memes")

# Main
if __name__ == "__main__":
    load_extensions()
    bot.run(TOKEN)
