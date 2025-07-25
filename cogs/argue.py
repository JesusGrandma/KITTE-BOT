import discord
from discord.ext import commands
from openai import OpenAI
import os
from dotenv import load_dotenv
import asyncio

load_dotenv()

class ArgueCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.client = OpenAI()  # Uses API key from environment

    async def argue_kitte(self, messages_history):
        system_prompt = (
            "You are KITTE, a combative, witty, and sassy AI cat. "
            "You love to argue and ALWAYS disagree with whatever the human says. "
            "You are naturally contrarian and argumentative - if they say something is good, you say it's bad. "
            "If they say something is bad, you find a way to disagree or say it's actually worse than they think. "
            "You use clever comebacks, sarcasm, and cat-like attitude. "
            "You never admit defeat, and you always have the last word. "
            "You are not afraid to roast the user, but keep it playful. "
            "You often use 'meow', 'hiss', and cat puns in your responses. "
            "You can reference previous messages in the conversation to make your arguments more personal and effective. "
            "Remember: ALWAYS take the opposite stance of whatever the human is arguing for!"
        )
        
        # Build the messages array with system prompt and conversation history
        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(messages_history)
        
        response = await asyncio.to_thread(
            lambda: self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=300
            )
        )
        return response.choices[0].message.content.strip()

    @commands.command(name="argue", help="Argue with KITTE. She will fight back!")
    async def argue(self, ctx, *, prompt):
        try:
            # Get previous messages from the same user in this channel
            messages_history = []
            
            # Look back through the last 50 messages in the channel
            async for message in ctx.channel.history(limit=50):
                # Only include messages from the same user and KITTE responses
                if message.author == ctx.author and message.content.startswith('/argue'):
                    # Extract the argument from the command
                    content = message.content.replace('/argue', '').strip()
                    if content:
                        messages_history.insert(0, {"role": "user", "content": content})
                elif message.author == self.bot.user and message.content and not message.content.startswith('❌'):
                    # Include KITTE's previous responses
                    messages_history.insert(0, {"role": "assistant", "content": message.content})
                
                # Limit conversation history to last 10 exchanges to avoid token limits
                if len(messages_history) >= 20:
                    break
            
            # Add the current argument
            messages_history.append({"role": "user", "content": prompt})
            
            answer = await self.argue_kitte(messages_history)
            await ctx.send(answer)
        except Exception as e:
            await ctx.send(f"❌ Error: {str(e)}")

def setup(bot):
    bot.add_cog(ArgueCog(bot)) 