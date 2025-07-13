import discord
from discord.ext import commands
import requests
import aiohttp
import os
import asyncio
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env

class TTSCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")  # Load from .env
        self.ELEVENLABS_VOICE_ID = 'zcAOhNBS3c14rBihAFp1'  # Example voice ID (Rachel); replace if needed
        self.ELEVENLABS_API_URL = f'https://api.elevenlabs.io/v1/text-to-speech/{self.ELEVENLABS_VOICE_ID}'

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'{self.bot.user} - TTS Cog loaded and ready.')

    @commands.command(name="ktts", help="Generate and play AI text-to-speech in your voice channel")
    async def tts(self, ctx, *, text: str):
        # Ensure the user is in a voice channel
        if not ctx.author.voice or not ctx.author.voice.channel:
            await ctx.send("You must be in a voice channel to use this command!", ephemeral=True)
            return

        voice_channel = ctx.author.voice.channel
        await ctx.send("Generating audio, please wait...", ephemeral=True)

        try:
            # Generate audio from ElevenLabs
            headers = {
                'Accept': 'audio/mpeg',
                'Content-Type': 'application/json',
                'xi-api-key': self.ELEVENLABS_API_KEY
            }
            data = {
                'text': text,
                'model_id': 'eleven_monolingual_v1',
                'voice_settings': {
                    'stability': 0.5,
                    'similarity_boost': 0.5
                }
            }

            # Make request to ElevenLabs API
            async with aiohttp.ClientSession() as session:
                async with session.post(self.ELEVENLABS_API_URL, json=data, headers=headers) as response:
                    if response.status != 200:
                        await ctx.send("Failed to generate audio from ElevenLabs.", ephemeral=True)
                        return
                    audio_data = await response.read()

            # Save audio to a temporary file
            audio_file = 'output.mp3'
            with open(audio_file, 'wb') as f:
                f.write(audio_data)

            # Connect to voice channel and play audio
            voice_client = await voice_channel.connect()
            # Lower pitch by 10% (change 1.1 to a higher value for lower pitch, or lower for higher pitch)
            audio_source = discord.FFmpegPCMAudio(
                audio_file,
                executable='ffmpeg',
                before_options='-loglevel panic',
                options='-af "asetrate=44100*0.50,aresample=44100"'
            )
            voice_client.play(audio_source)

            # Wait until playback is finished
            while voice_client.is_playing():
                await asyncio.sleep(1)

            # Disconnect and clean up
            await voice_client.disconnect()
            os.remove(audio_file)
            await ctx.send("Audio played successfully!", ephemeral=True)

        except Exception as e:
            await ctx.send(f"An error occurred: {str(e)}", ephemeral=True)
            if voice_client and voice_client.is_connected():
                await voice_client.disconnect()
            if os.path.exists(audio_file):
                os.remove(audio_file)

def setup(bot):
    bot.add_cog(TTSCog(bot))