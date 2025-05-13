import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
import random
import time
import platform
import asyncio
import aiohttp

# Local imports
from image_gen import generate_image
from chatgpt_handler import ask_cat_gpt
from cat_facts import get_random_cat_fact
from lyrics import Lyrics
from music import Music
from reddit_memes import RedditMemes
from steam_functions import Steam
from weather import get_weather

# Load environment variables
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
EDDIE_ID = int(os.getenv("EDDIE_ID"))
EDBOT_ID = int(os.getenv("EDBOT_ID"))

if not TOKEN:
    raise ValueError("DISCORD_TOKEN not found in environment variables")
if not WEATHER_API_KEY:
    raise ValueError("WEATHER_API_KEY not found in environment variables")

# Setup Discord bot
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
intents.members = True

bot = commands.Bot(command_prefix="/", intents=intents, help_command=None)
start_time = time.time()

# Global aiohttp session
session = None

@bot.event
async def on_ready():
    global session
    session = aiohttp.ClientSession()
    activity = discord.Game(name="Final Fantasy XIV")  # Replace with your custom message
    await bot.change_presence(status=discord.Status.online, activity=activity)
    print(f"Bot is online as {bot.user}")

@bot.event
async def on_shutdown():
    global session
    if session:
        await session.close()
    print("Closed aiohttp session.")

@bot.event
async def on_disconnect():
    global session
    if session:
        await session.close()
    print("Closed aiohttp session.")

# General Commands

@bot.command(help="Replies with Pong!")
async def ping(ctx):
    await ctx.send("Pong!")

@bot.command(name="status", help="Shows KITTE Bot status and info")
async def status(ctx):
    current_time = time.time()
    uptime_seconds = int(current_time - start_time)
    uptime = time.strftime("%H:%M:%S", time.gmtime(uptime_seconds))
    latency = round(bot.latency * 1000)
    server_count = len(bot.guilds)
    embed = discord.Embed(title="KITTIE-BOT Status", color=discord.Color.purple())
    embed.add_field(name="Uptime", value=uptime, inline=True)
    embed.add_field(name="Latency", value=f"{latency}ms", inline=True)
    embed.add_field(name="Servers", value=f"{server_count}", inline=True)
    embed.add_field(name="Python", value=platform.python_version(), inline=True)
    embed.add_field(name="Library", value=f"discord.py {discord.__version__}", inline=True)
    await ctx.send(embed=embed)

@bot.command(name="info", help="Shows bot creator and helpful links")
async def info(ctx):
    embed = discord.Embed(
        title="About KITTIE",
        description="Cat bot meow",
        color=discord.Color.purple()
    )
    embed.add_field(name="Creator", value="JesusGrandma", inline=True)
    embed.add_field(name="Support / GitHub", value="[Click Here](https://github.com/JesusGrandma/KITTE-BOT)", inline=False)
    try:
        await ctx.author.send(embed=embed)
        if ctx.guild:
            await ctx.send("I've sent you a DM with the info")
    except discord.Forbidden:
        await ctx.send("❌ I couldn't send you a DM. Please check your privacy settings.")

# Fun Commands

@bot.command(name="catfact", help="Sends a random cat fact")
async def catfact(ctx):
    fact = get_random_cat_fact()
    await ctx.send(f"**Cat Fact:** {fact}")

@bot.command(name="kittyuh", help="Sends a random cat picture")
async def cat(ctx):
    folder = "cat-pics"
    if not os.path.exists(folder):
        await ctx.send("❌ No cat pics folder found!")
        return
    files = [f for f in os.listdir(folder) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]
    if not files:
        await ctx.send("😿 No cat pics found.")
        return
    chosen = random.choice(files)
    file_path = os.path.join(folder, chosen)
    emojis = ["🐱", "😺", "😻", "🐾", "😹", "😽", "🐈", "💖", "✨", "🌟"]
    chosen_emoji = random.choice(emojis)
    await ctx.send(f"{chosen_emoji} Here's a random cat for you!", file=discord.File(file_path))

# AI Commands

@bot.command(name="ask", help="Ask GPT-3.5 a question")
async def ask(ctx, *, prompt):
    try:
        answer = await asyncio.to_thread(ask_cat_gpt, prompt)
        await ctx.send(answer)
    except Exception as e:
        await ctx.send(f"❌ Error: {str(e)}")

@bot.command(name="image", help="Generate an AI image from a prompt")
async def imagine(ctx, *, prompt):
    await ctx.send(f"Generating image for: {prompt}. Please wait as this could take a few seconds.")
    image_url = generate_image(prompt)
    if image_url:
        await ctx.send(image_url)
    else:
        await ctx.send("❌ Failed to generate image.")

# Utility Commands

@bot.command(name="weather", help="Get current weather for a city")
async def weather(ctx, *, city: str):
    await ctx.trigger_typing()
    data = await get_weather(city, session)
    if not data or "error" in data:
        await ctx.send("❌ Couldn't fetch weather data. Please check the city name.")
        return
    location = data['location']['name']
    country = data['location']['country']
    condition = data['current']['condition']['text']
    temp_c = data['current']['temp_c']
    feelslike_c = data['current']['feelslike_c']
    humidity = data['current']['humidity']
    wind_kph = data['current']['wind_kph']
    icon_url = "http:" + data['current']['condition']['icon']
    embed = discord.Embed(
        title=f"Weather in {location}, {country}",
        description=f"{condition}",
        color=discord.Color.blue()
    )
    embed.set_thumbnail(url=icon_url)
    embed.add_field(name="Temperature", value=f"{temp_c}°C (feels like {feelslike_c}°C)", inline=False)
    embed.add_field(name="Humidity", value=f"{humidity}%", inline=True)
    embed.add_field(name="Wind", value=f"{wind_kph} kph", inline=True)
    await ctx.send(embed=embed)

# Help Command

@bot.command(name="help", help="Shows a list of available commands")
async def help_command(ctx):
    embed = discord.Embed(
        title="🐱 KITTIE-BOT Commands",
        description="Here are the available commands grouped by category:",
        color=discord.Color.purple()
    )
    # Group commands by category
    categories = {
        "General": [],
        "Music": [],
        "Fun": [],
        "AI": [],
        "Utilities": []
    }
    for command in bot.commands:
        if command.hidden:
            continue
        # Categorize commands based on their name or purpose
        if command.name in ["ping", "status", "info"]:
            categories["General"].append(command)
        elif command.name in ["join", "leave", "play", "pause", "resume", "stop"]:
            categories["Music"].append(command)
        elif command.name in ["catfact", "kittyuh", "duck", "insult"]:
            categories["Fun"].append(command)
        elif command.name in ["ask", "image"]:
            categories["AI"].append(command)
        elif command.name in ["weather", "reddit"]:
            categories["Utilities"].append(command)
    # Add commands to the embed
    for category, commands_list in categories.items():
        if commands_list:
            value = "\n".join(f"/{cmd.name} - {cmd.help or 'No description'}" for cmd in commands_list)
            embed.add_field(name=f"**{category}**", value=value, inline=False)
    embed.set_footer(text="Use / to execute a command.")
    await ctx.send(embed=embed)

# Trolling Features

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    content = message.content.lower()

    # Respond to Eddie (creator)
    if message.author.id == EDDIE_ID:  # Replace with Eddie's Discord user ID
        eddie_responses = [
            "burger with the sauce",
            "mac and cheese",
            "fuck you eddie",
            "destiny 2",
            "how much have you spent on magic",
        ]
        if random.random() < 0.05:
            await message.channel.send(random.choice(eddie_responses))
        # DO NOT return here

    # Respond to Edbot
    elif message.author.id == EDBOT_ID:
        edbot_responses = [
            "im better",
            "edbot smells like fish",
            "meow",
            "winston eats edbot",
            "edbot is jeramey derkas's son",
            "no bitches",
            "you smell like dylan",
            "charles casavant",
            "i am supreme",
            "i have 3000 hours on dbd",
            "overwatch 2 more like... i hate myself",
        ]
        if random.random() < 0.05:
            await message.channel.send(random.choice(edbot_responses))
        # DO NOT return here

    # Respond when KITTIE is mentioned
    if "kittie" in content:
        kittie_responses = [
            "what",
            "Meow",
            "plz stop",
            "john poppytits",
            "wtf do you want",
            "i dont pay child support",
        ]
        await message.channel.send(random.choice(kittie_responses))
        # DO NOT return here

    # General cat-related responses
    cat_words = ["meow", "kitty", "cat", "purr", "treat", "whiskers", "litter", "feline"]
    chance = 0.05  # Default chance to respond
    if any(word in content for word in cat_words):
        chance = 0.25  # Higher chance if cat-related words are detected
    if random.random() < chance:
        cat_responses = [
            "Meow? 🐾",
            "*licks paw*",
            "*purrs loudly* 😺",
            "Did you say... tuna? 🐟",
            "*knocks cup off table* 😼",
            "*stares at you silently from the corner*",
        ]
        await message.channel.send(random.choice(cat_responses))

    # Always process commands after handling trolling and fun responses
    await bot.process_commands(message)  # [4][5][6]

# Main Function

async def main():
    async with bot:
        await bot.add_cog(Music(bot))
        await bot.add_cog(RedditMemes(bot))
        await bot.add_cog(Lyrics(bot))
        await bot.add_cog(Steam(bot))
        await bot.start(TOKEN)

if __name__ == "__main__":
    asyncio.run(main())
