import discord
from discord.ext import commands
import openai
import os
from dotenv import load_dotenv
import traceback

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")
print("OpenAI API Key Loaded:", bool(openai.api_key))

class CatFeeder(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="feed")
    async def feed(self, ctx, *, item: str = None):
        if not item:
            await ctx.send("😾 You have to tell me what you're feeding me!")
            return

        prompt = (
            f"You are a very sassy, witty, and sarcastic cat. A human tries to feed you '{item}'. "
            "If the item is spicy, or not actually food, respond with a clever, mean, or disgusted remark (1-2 sentences). "
            "If the item is any kind of normal, safe food (like chicken, tuna, or cat food), respond with a playful, mischievous, or excited cat-like remark (1-2 sentences), but keep your wit and sass. "
            "Respond with only one short, clever message."
        )

        try:
            client = openai.OpenAI(api_key=openai.api_key)
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=60,
                temperature=0.5,
            )
            ai_response = response.choices[0].message.content.strip()
            await ctx.send(ai_response)
        except Exception as e:
            print("OpenAI API error:", e)
            traceback.print_exc()
            await ctx.send("😾 Something went wrong with the AI. Check the logs.")

async def setup(bot):
    await bot.add_cog(CatFeeder(bot))
