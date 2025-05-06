import discord
from discord.ext import commands
import asyncpraw
import random
import os
from dotenv import load_dotenv  # Corrected import

load_dotenv()  # Load environment variables from .env

class RedditMemes(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.reddit = asyncpraw.Reddit(
            client_id=os.getenv("REDDIT_CLIENT_ID"),
            client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
            user_agent=os.getenv("REDDIT_USER_AGENT")
        )

    @commands.command(name="caseoh", help="Pull a random meme from r/caseoh_")
    async def caseoh(self, ctx):
        subreddit = await self.reddit.subreddit("caseoh_")
        posts = [post async for post in subreddit.hot(limit=50)
                 if not post.stickied and post.url.lower().endswith(('.jpg', '.jpeg', '.png', '.gif'))]
        
        if not posts:
            await ctx.send("No suitable memes found.")
            return

        post = random.choice(posts)
        await ctx.send(post.url)

def setup(bot):
    bot.add_cog(RedditMemes(bot))
