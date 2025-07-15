import discord
from discord.ext import commands
import aiohttp
import html

TRIVIA_CATEGORIES = {
    "general": 9,
    "books": 10,
    "film": 11,
    "music": 12,
    "musicals": 13,
    "tv": 14,
    "video games": 15,
    "board games": 16,
    "science": 17,
    "computers": 18,
    "math": 19,
    "mythology": 20,
    "sports": 21,
    "geography": 22,
    "history": 23,
    "politics": 24,
    "art": 25,
    "celebrities": 26,
    "animals": 27,
    "vehicles": 28,
    "comics": 29,
    "gadgets": 30,
    "anime": 31,
    "cartoon": 32
}
TRIVIA_DIFFICULTIES = ["easy", "medium", "hard"]

class Trivia(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="trivia", help="Ask a random trivia question. Usage: /trivia [category] [difficulty]. Use /triviacategories or /triviadifficulties to list options.")
    async def trivia(self, ctx, category: str = None, difficulty: str = None):
        if category and category.lower() == "categories":
            cats = ', '.join(TRIVIA_CATEGORIES.keys())
            await ctx.send(f"Available categories: {cats}")
            return
        if difficulty and difficulty.lower() == "difficulties":
            diffs = ', '.join(TRIVIA_DIFFICULTIES)
            await ctx.send(f"Available difficulties: {diffs}")
            return
        params = {"amount": 1, "type": "multiple"}
        if category and category.lower() in TRIVIA_CATEGORIES:
            params["category"] = TRIVIA_CATEGORIES[category.lower()]
        if difficulty and difficulty.lower() in TRIVIA_DIFFICULTIES:
            params["difficulty"] = difficulty.lower()
        url = "https://opentdb.com/api.php"
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as resp:
                if resp.status != 200:
                    await ctx.send("❌ Could not fetch a trivia question. Try again later.")
                    return
                data = await resp.json()
                if not data["results"]:
                    await ctx.send("❌ No questions found for that category/difficulty. Try different options.")
                    return
                question_data = data["results"][0]
                question = html.unescape(question_data["question"])
                correct = html.unescape(question_data["correct_answer"])
                incorrect = [html.unescape(ans) for ans in question_data["incorrect_answers"]]
                options = incorrect + [correct]
                import random
                random.shuffle(options)
                option_letters = ["A", "B", "C", "D"]
                option_map = dict(zip(option_letters, options))
                options_text = "\n".join(f"{letter}: {option}" for letter, option in option_map.items())
                embed = discord.Embed(title="Trivia Time!", description=f"{question}\n\n{options_text}", color=discord.Color.blue())
                embed.set_footer(text="Reply with the letter of your answer (A, B, C, or D)")
                await ctx.send(embed=embed)

                def check(m):
                    return m.author == ctx.author and m.channel == ctx.channel and m.content.upper() in option_letters
                try:
                    answer_msg = await self.bot.wait_for("message", timeout=20.0, check=check)
                except Exception:
                    await ctx.send(f"⏰ Time's up! The correct answer was: **{correct}**")
                    return
                user_answer = answer_msg.content.upper()
                if option_map[user_answer] == correct:
                    await ctx.send(f"✅ Correct! 🎉 The answer was: **{correct}**")
                else:
                    await ctx.send(f"❌ Incorrect. The correct answer was: **{correct}**")

    @commands.command(name="triviacat", help="List all available trivia categories.")
    async def triviacategories(self, ctx):
        cats = ', '.join(TRIVIA_CATEGORIES.keys())
        await ctx.send(f"Available categories: {cats}")

    @commands.command(name="triviadif", help="List all available trivia difficulties.")
    async def triviadifficulties(self, ctx):
        diffs = ', '.join(TRIVIA_DIFFICULTIES)
        await ctx.send(f"Available difficulties: {diffs}")

def setup(bot):
    bot.add_cog(Trivia(bot)) 