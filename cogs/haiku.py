from openai import OpenAI
import os
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
client = OpenAI()  # Will auto-pick up from env

class Haiku(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="haiku", help="Generate a haiku about a topic. Usage: /haiku [topic]")
    async def haiku(self, ctx, *, topic: str = None):
        """Generates a haiku using OpenAI. Optionally takes a topic."""
        try:
            user_prompt = f"Write a haiku about {topic}." if topic else "Write a haiku."
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a poet who only writes in traditional 5-7-5 haiku format."},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=50,
                temperature=0.8
            )
            haiku = response.choices[0].message.content.strip()
            await ctx.send(haiku)
        except Exception as e:
            await ctx.send(f"Failed to generate haiku: {e}")
            print(f"Error generating haiku: {e}")

async def setup(bot):
    await bot.add_cog(Haiku(bot))
