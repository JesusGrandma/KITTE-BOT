# bot.py
import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
from image_gen import generate_image
import io
import random

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
intents.members = True  # ✅ Needed for welcome message

bot = commands.Bot(command_prefix="/", intents=intents, help_command=None)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

@bot.event
async def on_member_join(member):
    # Try to find a channel named 'general' to send the welcome message
    channel = discord.utils.get(member.guild.text_channels, name="welcome")
    if channel:
        await channel.send(f"🎉 Welcome to the server, {member.mention}! We're glad to have you here! 🐱")

@bot.command(help="Replies with Pong!")
async def ping(ctx):
    await ctx.send("Pong!")

@bot.command(name="image", help="Generate an AI image from a prompt")
async def imagine(ctx, *, prompt):
    await ctx.send(f"🎨 Generating image for: `{prompt}`...")
    image_url = generate_image(prompt)
    
    if image_url:
        await ctx.send(image_url)  # Send the image URL to Discord
    else:
        await ctx.send("❌ Failed to generate image.")

@bot.command(name="kittyuh", help="Sends a random cat picture")
async def cat(ctx):
    folder = "cat-pics"
    files = [f for f in os.listdir(folder) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]

    if not files:
        await ctx.send("😿 No cat pics found.")
        return

    chosen = random.choice(files)
    file_path = os.path.join(folder, chosen)

    emojis = ["🐱", "😺", "😻", "🐾", "😹", "😽", "🐈", "💖", "✨", "🌟"]
    chosen_emoji = random.choice(emojis)

    await ctx.send(f"{chosen_emoji} Here's a random cat for you!", file=discord.File(file_path))

@bot.command(name="help", help="General help command")
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
