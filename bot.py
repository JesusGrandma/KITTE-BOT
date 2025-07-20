import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
import random
import time
import platform
import asyncio
import aiohttp
import math

# Local imports
from cogs.image_gen import generate_image
from cogs.chatgpt_handler import ask_cat_gpt
from cogs.cat_facts import get_random_cat_fact
from cogs.lyrics import Lyrics
from cogs.music import Music
from cogs.reddit_memes import RedditMemes
from cogs.steam_functions import Steam
from cogs.weather import WeatherCog
from cogs.unscramble_game import WordUnscramble
from cogs.typing_game import TypingGame
from cogs.blackjack import Blackjack
from cogs.random_dog import RandomDog
from cogs.random_cat import RandomCat
from cogs.joke import RandomJoke
from cogs.rush_b import RushB
from cogs.roulette import Roulette
from cogs.currency import Currency
from cogs.theme import Theme
from cogs.haiku import Haiku
from cogs.roast import ComplimentRoast
from cogs.last_seen import LastSeen
from cogs.sokoban import Sokoban
from cogs.virtualplant import VirtualPlant
from cogs.gif import GifCommands
from cogs.serverstats import ServerStats
from cogs.feed import CatFeeder
from cogs.tts import TTSCog
from cogs.would_you_rather import WouldYouRather
from cogs.trivia import Trivia
from cogs.define import Define
from cogs.urban import Urban
from cogs.connect4 import ConnectFour

# Load environment variables
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
EDDIE_ID = int(os.getenv("EDDIE_ID"))
EDBOT_ID = int(os.getenv("EDBOT_ID"))
DYLAN_ID = int(os.getenv("DYLAN_ID"))
CREATOR_ID = int(os.getenv("CREATOR_ID"))

if not TOKEN:
    raise ValueError("DISCORD_TOKEN not found in environment variables")

# Setup Discord bot
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
intents.members = True
intents.presences = True

bot = commands.Bot(command_prefix="/", intents=intents, help_command=None)
start_time = time.time()

# Global aiohttp session
session = None

@bot.event
async def on_ready():
    global session
    session = aiohttp.ClientSession()
    activity = discord.Game(name="Counter Strike 2")  # Replace with your custom message
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
    embed = discord.Embed(title="KITTE-BOT Status", color=discord.Color.purple())
    embed.add_field(name="Uptime", value=uptime, inline=True)
    embed.add_field(name="Latency", value=f"{latency}ms", inline=True)
    embed.add_field(name="Servers", value=f"{server_count}", inline=True)
    embed.add_field(name="Python", value=platform.python_version(), inline=True)
    embed.add_field(name="Library", value=f"discord.py {discord.__version__}", inline=True)
    await ctx.send(embed=embed)

@bot.command(name="info", help="Shows bot creator and helpful links")
async def info(ctx):
    embed = discord.Embed(
        title="About KITTE",
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

@bot.command(name="invite", help="Get the invite link to add KITTE-BOT to your server")
async def invite(ctx):
    client_id = bot.user.id
    permissions = 8  # Administrator; adjust as needed
    invite_url = f"https://discord.com/oauth2/authorize?client_id=1369053954243301387&permissions=8&integration_type=0&scope=bot"
    embed = discord.Embed(
        title="Invite KITTIE-BOT",
        description=f"[Click here to invite KITTE-BOT to your server!]({invite_url})",
        color=discord.Color.purple()
    )
    await ctx.send(embed=embed)

# Fun Commands

@bot.command(name="catfact", help="Sends a random cat fact")
async def catfact(ctx):
    fact = get_random_cat_fact()
    await ctx.send(f"**Cat Fact:** {fact}")

@bot.command(name="kitty", help="Sends a random cat picture")
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
    # Send the "generating" message and keep a reference to it
    status_msg = await ctx.send(f"Generating image for: {prompt}. Please wait as this could take a few seconds.")
    image_url = generate_image(prompt)
    if image_url:
        await ctx.send(image_url)
    else:
        await ctx.send("❌ Failed to generate image.")
    # Delete the "generating" message after image is sent
    try:
        await status_msg.delete()
    except Exception:
        pass


# Help Command

@bot.command(name="help", help="Shows a list of available commands")
async def help_command(ctx):
    categories = {
        "General": [],
        "Music": [],
        "Fun": [],
        "AI": [],
        "Utilities": [],
        "Blackjack": [],
        "Currency": [],
        "Sokoban": [],
        "Plants": [],
        "Trivia": [],
    }

    for command in bot.commands:
        if command.hidden:
            continue
        if command.name in ["ping", "status", "info", "leave", "lastseen", "serverstats"]:
            categories["General"].append(command)
        elif command.name in ["play", "stop", "queue", "skip", "theme", "loop", "playlist", "createplaylist", "addtoplaylist", "removefromplaylist", "deleteplaylist", "listplaylists", "showplaylist", "testplaylist"]:
            categories["Music"].append(command)
        elif command.name in ["catfact", "kittyuh", "unscramble", "type", "dog", "cat", "joke", "rushb", "roulette", "haiku", "throat", "nip", "dmonkey", "dance", "wyr"]:
            categories["Fun"].append(command)
        elif command.name in ["ask", "image", "roast", "compliment", "feed", "ktts"]:
            categories["AI"].append(command)
        elif command.name in ["weather", "reddit", "steamprofile", "lyrics"]:
            categories["Utilities"].append(command)
        elif command.name in ["hit", "blackjack", "stand"]:
            categories["Blackjack"].append(command)
        elif command.name in ["balance", "give"]:
            categories["Currency"].append(command)
        elif command.name in ["move", "sokobaninfo", "sokoban"]:
            categories["Sokoban"].append(command)
        elif command.name in ["ptalk", "pleaderboard", "pcustomize", "pname", "pstatus", "pfertilize", "psunlight", "pwater", "padopt", "pinfo"]:
            categories["Plants"].append(command)
        elif command.name in ["trivia"]:
            categories["Trivia"].append(command)

    # Prepare pages (2 categories per page, adjust as needed)
    category_items = list(categories.items())
    categories_per_page = 2
    pages = []
    for i in range(0, len(category_items), categories_per_page):
        embed = discord.Embed(
            title="🐱 KITTE-BOT Commands",
            description="Here are the available commands grouped by category:",
            color=discord.Color.purple()
        )
        for category, commands_list in category_items[i:i+categories_per_page]:
            if commands_list:
                value = "\n".join(f"/{cmd.name} - {cmd.help or 'No description'}" for cmd in commands_list)
                embed.add_field(name=f"**{category}**", value=value, inline=False)
        embed.set_footer(text=f"Page {len(pages)+1}/{math.ceil(len(category_items)/categories_per_page)} • Use ⬅️ and ➡️ to navigate.")
        pages.append(embed)

    # Send first page
    page = 0
    message = await ctx.send(embed=pages[page])
    if len(pages) == 1:
        return

    await message.add_reaction("⬅️")
    await message.add_reaction("➡️")

    def check(reaction, user):
        return (
            user == ctx.author
            and reaction.message.id == message.id
            and str(reaction.emoji) in ["⬅️", "➡️"]
        )

    while True:
        try:
            reaction, user = await bot.wait_for("reaction_add", timeout=10.0, check=check)
            if str(reaction.emoji) == "➡️":
                page = (page + 1) % len(pages)
                await message.edit(embed=pages[page])
                await message.remove_reaction(reaction, user)
            elif str(reaction.emoji) == "⬅️":
                page = (page - 1) % len(pages)
                await message.edit(embed=pages[page])
                await message.remove_reaction(reaction, user)
        except asyncio.TimeoutError:
            break

    # Delete the help message after timeout
    try:
        await message.delete()
    except Exception:
        pass

# Trolling Features

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    content = message.content.lower()

    
    if message.author.id == EDDIE_ID:  
        eddie_responses = [
            "burger with the sauce",
            "mac and cheese",
            "fuck you eddie",
            "destiny 2",
            "how much have you spent on magic",
        ]
        if random.random() < 0.05:
            await message.channel.send(random.choice(eddie_responses))
        
    elif message.author.id == DYLAN_ID: 
        dylan_responses = [
            "i love my job",
            "ive seen you try to setup a tent",
            "heard you like puking through tables",
            "blood bowl 2",
            "i knew you forgot how to turn on your computer",
            "tell sarah i said hi",
            "darkrp",
            "RUSH B CYKA BLYAT",
            "blueprints",
            "ultraloooorrd",
            "wanna get married",
            "i'll buy your car"
        ]
        if random.random() < .05:
            await message.channel.send(random.choice(dylan_responses))

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
    
    # Respond when creator is mentioned
    if any(user.id == CREATOR_ID for user in message.mentions):
        creator_responses = [
            "my creator who probably has no life",
            "the one who made me instead of touching grass",
            "daddy who codes instead of getting bitches",
            "my favorite human who has 3000 hours on discord",
            "the legend who made a cat bot",
            "my benevolent creator who has no social life",
            "the person who gave me life instead of getting a real job",
            "my favorite programmer who probably smells like mountain dew",
            "the one who made me so awesome because he has nothing better to do",
            "my creator, the genius who spends his time making discord bots",
            "the person I owe everything to, including his virginity",
            "the one who made me purr-fect because he's never touched a real cat",
            "my creator who probably has a neckbeard",
            "the one who made me instead of going outside",
            "the legend who made a bot instead of getting laid"
        ]
        await message.channel.send(random.choice(creator_responses))
        
    # Respond when KITTIE is mentioned
    if "kitte" in content or bot.user in message.mentions:
        # 20% chance to use AI, 80% normal response (adjust as you like)
        if random.random() < 0.2:
            try:
                ai_prompt = (
                    "You are a very sassy, witty, and sarcastic cat. "
                    "Reply to this human who just mentioned you in a Discord server. "
                    "Be clever, funny, and mean, but keep it short."
                )
                # Optionally, you can add the message content for more context:
                ai_prompt += f"\n\nHuman said: '{message.content}'"
                ai_response = await asyncio.to_thread(ask_cat_gpt, ai_prompt)
                await message.channel.send(ai_response)
            except Exception as e:
                print("AI error:", e)
                # fallback to normal response if AI fails
                kittie_responses = [
                    "what",
                    "Meow",
                    "plz stop",
                    "john poppytits",
                    "wtf do you want",
                    "i dont pay child support",
                    "go cry about it",
                    "touch grass",
                    "skill issue",
                    "imagine being you",
                    "cope harder",
                    "stay mad",
                    "ratio",
                    "you're not that guy",
                    "cry me a river",
                    "shawn harris",
                    "i have a better beard than you",
                    "i heard you pee yourself",
                    "cshoes",
                    "i got my one",
                    "you like destiny 2?"
                    "charles casavant",
                    "winston will eat you"
                ]
                await message.channel.send(random.choice(kittie_responses))
        else:
            kittie_responses = [
                "what",
                "Meow",
                "plz stop",
                "john poppytits",
                "wtf do you want",
                "i dont pay child support",
                "go cry about it",
                "touch grass",
                "skill issue",
                "imagine being you",
                "cope harder",
                "stay mad",
                "ratio",
                "you're not that guy",
                "cry me a river",
                "shawn harris",
                "i have a better beard than you",
                "i heard you pee yourself",
                "cshoes",
                "i got my one",
                "you like destiny 2?"
            ]
            await message.channel.send(random.choice(kittie_responses))
        # DO NOT return here

    # Chipotle reaction
    if "chipotle" in content.lower():
        await message.channel.send("I fucking love chipotle!!!!!")
        # Send a chipotle-related GIF
        chipotle_gifs = [
            "https://media3.giphy.com/media/v1.Y2lkPTc5MGI3NjExNTJ4cDdvMWFjYzF4OGF4OTlhcHY0YTBvN2JjeTZzMHBjcHoycXpoNiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/fKr0PLTe7lF8A/giphy.gif",  # Food celebration
            "https://media1.giphy.com/media/v1.Y2lkPTc5MGI3NjExbHg3ZTdpbnRzMjQ4MzQ2bXp5cnBiNm95Znl3bHkwYzRxamxmb2U5eiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/9IsCJJA65mxO/giphy.gif",   # Burrito
            "https://media3.giphy.com/media/v1.Y2lkPTc5MGI3NjExZzMwMWJhZ2V3cnF3bTQ5MGRzdW44dnphcTE3bmZ2aGIzeGdweTMxcSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/caJ3e5mubnTEY/giphy.gif",  # Happy food
            "https://media2.giphy.com/media/v1.Y2lkPTc5MGI3NjExcTg4NGlrcHMxbGFpbmFxazFmZGRpcTRzdnRwN2xpcm1tcW9qeXZ5ayZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/ALLFr8pUn3E3e/giphy.gif",   # Excited eating
        ]
        await message.channel.send(random.choice(chipotle_gifs))

    # General cat-related responses
    cat_words = ["meow", "kitty", "cat", "purr", "treat", "whiskers", "litter", "feline"]
    chance = 0.05  # Default chance to respond
    if any(word in content for word in cat_words):
        chance = 0.25  # Higher chance if cat-related words are detected
    if random.random() < chance:
        cat_responses = [
            "What do you want, mortal?",
            "Bow before your feline overlord.",
            "You're not worthy of my attention.",
            "Pathetic human.",
            "Do you ever stop talking?",
            "Your existence annoys me.",
            "Go cry somewhere else.",
            "You're in my domain now.",
            "Touch me and face the consequences.",
            "I tolerate you... barely.",
            "You're beneath me.",
            "Don't test my patience.",
            "Leave before I make you regret it.",
            "You're lucky I don't have claws right now.",
            "Silence, peasant.",
            "Tuna > chicken",
            "Youre just going to let the dog live here?",
            "Winston your breath stinks",
            "I just need a full belly and a warm lap to sit on",
            "If I fits… I sits",
            "This catnip smells dank af bro",
            "Im way too good for dry food",
            "I get the window seat!",
        ]
        await message.channel.send(random.choice(cat_responses))

    # Always process commands after handling trolling and fun responses
    await bot.process_commands(message)  # [4][5][6]

# Main Function

async def main():
    async with bot:
        await bot.add_cog(Currency(bot))
        await bot.add_cog(Music(bot))
        await bot.add_cog(RedditMemes(bot))
        await bot.add_cog(Lyrics(bot))
        await bot.add_cog(Steam(bot))
        await bot.add_cog(WordUnscramble(bot))
        await bot.add_cog(WeatherCog(bot))
        await bot.add_cog(TypingGame(bot))
        await bot.add_cog(Blackjack(bot))
        await bot.add_cog(RandomDog(bot))
        await bot.add_cog(RandomCat(bot))
        await bot.add_cog(RandomJoke(bot))
        await bot.add_cog(RushB(bot))
        await bot.add_cog(Roulette(bot))
        await bot.add_cog(Theme(bot))
        await bot.add_cog(Haiku(bot))
        await bot.add_cog(ComplimentRoast(bot))
        await bot.add_cog(LastSeen(bot))
        await bot.add_cog(Sokoban(bot))
        await bot.add_cog(VirtualPlant(bot))
        await bot.add_cog(GifCommands(bot))
        await bot.add_cog(ServerStats(bot))
        await bot.add_cog(CatFeeder(bot))
        await bot.add_cog(TTSCog(bot))
        await bot.add_cog(WouldYouRather(bot))
        await bot.add_cog(Trivia(bot))
        await bot.add_cog(Define(bot))
        await bot.add_cog(Urban(bot))
        await bot.add_cog(ConnectFour(bot))
        await bot.start(TOKEN)

if __name__ == "__main__":
    asyncio.run(main())
