import discord
from discord.ext import commands
import asyncpraw
import random
import os
from dotenv import load_dotenv

load_dotenv()

class RedditMemes(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.reddit = asyncpraw.Reddit(
            client_id=os.getenv("REDDIT_CLIENT_ID"),
            client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
            user_agent=os.getenv("REDDIT_USER_AGENT")
        )

    @commands.command(name="caseoh", help="Pull a funny meme from r/caseoh_")
    async def caseoh(self, ctx):
        subreddit = await self.reddit.subreddit("caseoh_")
        
        # Get top posts of the week
        posts = [
            post async for post in subreddit.top(time_filter="week", limit=100)
            if not post.stickied 
            and post.score > 100  # Only popular posts
            and post.url.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.gifv', '.mp4'))
        ]
        
        if not posts:
            await ctx.send("No funny memes found this week. 😿")
            return

        random.shuffle(posts)
        post = posts[0]

        # Optional: embed for nicer formatting
        embed = discord.Embed(title=post.title, url=post.url, color=discord.Color.orange())
        embed.set_image(url=post.url)
        embed.set_footer(text=f"👍 {post.score} | 💬 {post.num_comments} | From r/caseoh_")

        await ctx.send(embed=embed)

# **Add the setup function here**
async def setup(bot):
    await bot.add_cog(reddit_memes(bot))
