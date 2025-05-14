from discord.ext import commands
import discord
import random
import asyncpraw
import os


class RedditMemes(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.reddit = asyncpraw.Reddit(
            client_id=os.getenv("REDDIT_CLIENT_ID"),
            client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
            user_agent=os.getenv("REDDIT_USER_AGENT")
        )

    @commands.command(name="reddit", help="Get a random post from any subreddit (e.g. /reddit memes)")
    async def reddit(self, ctx, subreddit_name: str):
        try:
            subreddit = await self.reddit.subreddit(subreddit_name, fetch=True)
            # Check if the subreddit is NSFW
            if subreddit.over18:  # This is the correct attribute for asyncpraw
                await ctx.send("❌ Sorry, I can't fetch posts from NSFW subreddits.")
                return

            # Fetch up to 50 hot posts (excluding stickied)
            posts = [
                post async for post in subreddit.hot(limit=50)
                if not post.stickied
            ]
            if not posts:
                await ctx.send("No posts found in that subreddit.")
                return
            post = random.choice(posts)
            embed = discord.Embed(title=post.title, url=post.url, color=discord.Color.orange())
            if post.url.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.gifv', '.mp4')):
                embed.set_image(url=post.url)
            embed.set_footer(text=f"👍 {post.score} | 💬 {post.num_comments} | From r/{subreddit_name}")
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"❌ Error: {str(e)}")
async def setup(bot):
    await bot.add_cog(RedditMemes(bot))

