import discord
from discord.ext import commands, tasks
import asyncio
import yt_dlp as youtube_dl
import time
import logging
import sqlite3
import os

logger = logging.getLogger(__name__)

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.voice_client = None
        self.music_playing = False
        self.last_activity_time = time.time()
        self.song_queue = []
        self.loop_enabled = False  
        self.current_song = None
        self.db_file = "playlists.db"
        try:
            self.init_database()
            print(f"Music cog initialized. Database ready.")
        except Exception as e:
            print(f"Error initializing Music cog: {e}")

    def init_database(self):
        """Initialize the SQLite database"""
        try:
            import os
            current_dir = os.getcwd()
            db_path = os.path.join(current_dir, self.db_file)
            print(f"Attempting to create database at: {db_path}")
            
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Create playlists table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS playlists (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    playlist_name TEXT NOT NULL,
                    UNIQUE(user_id, playlist_name)
                )
            ''')
            
            # Create songs table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS songs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    playlist_id INTEGER NOT NULL,
                    audio_url TEXT NOT NULL,
                    page_url TEXT NOT NULL,
                    title TEXT NOT NULL,
                    position INTEGER NOT NULL,
                    FOREIGN KEY (playlist_id) REFERENCES playlists (id) ON DELETE CASCADE
                )
            ''')
            
            conn.commit()
            conn.close()
            print(f"Database successfully created at: {db_path}")
            
            # Verify file exists
            if os.path.exists(db_path):
                print(f"Database file confirmed to exist: {db_path}")
                print(f"File size: {os.path.getsize(db_path)} bytes")
            else:
                print(f"ERROR: Database file was not created at {db_path}")
                
        except Exception as e:
            print(f"Error initializing database: {e}")
            import traceback
            traceback.print_exc()

    def get_user_playlists(self, user_id):
        """Get all playlists for a specific user"""
        import os
        db_path = os.path.join(os.getcwd(), self.db_file)
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT playlist_name FROM playlists 
            WHERE user_id = ? 
            ORDER BY playlist_name
        ''', (str(user_id),))
        
        playlists = [row[0] for row in cursor.fetchall()]
        conn.close()
        return playlists

    def get_playlist_songs(self, user_id, playlist_name):
        """Get all songs in a specific playlist"""
        import os
        db_path = os.path.join(os.getcwd(), self.db_file)
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT s.audio_url, s.page_url, s.title, s.position
            FROM songs s
            JOIN playlists p ON s.playlist_id = p.id
            WHERE p.user_id = ? AND p.playlist_name = ?
            ORDER BY s.position
        ''', (str(user_id), playlist_name))
        
        songs = [(row[0], row[1], row[2]) for row in cursor.fetchall()]
        conn.close()
        return songs

    def create_playlist_db(self, user_id, playlist_name):
        """Create a new playlist in the database"""
        import os
        db_path = os.path.join(os.getcwd(), self.db_file)
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO playlists (user_id, playlist_name)
                VALUES (?, ?)
            ''', (str(user_id), playlist_name))
            conn.commit()
            success = True
        except sqlite3.IntegrityError:
            success = False  # Playlist already exists
        finally:
            conn.close()
        
        return success

    def add_song_to_playlist_db(self, user_id, playlist_name, audio_url, page_url, title):
        """Add a song to a playlist in the database"""
        import os
        db_path = os.path.join(os.getcwd(), self.db_file)
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        try:
            # Get playlist ID
            cursor.execute('''
                SELECT id FROM playlists 
                WHERE user_id = ? AND playlist_name = ?
            ''', (str(user_id), playlist_name))
            
            playlist_row = cursor.fetchone()
            if not playlist_row:
                conn.close()
                return False
            
            playlist_id = playlist_row[0]
            
            # Get the next position
            cursor.execute('''
                SELECT MAX(position) FROM songs 
                WHERE playlist_id = ?
            ''', (playlist_id,))
            
            max_pos = cursor.fetchone()[0]
            next_position = 1 if max_pos is None else max_pos + 1
            
            # Add the song
            cursor.execute('''
                INSERT INTO songs (playlist_id, audio_url, page_url, title, position)
                VALUES (?, ?, ?, ?, ?)
            ''', (playlist_id, audio_url, page_url, title, next_position))
            
            conn.commit()
            success = True
        except Exception as e:
            print(f"Error adding song to playlist: {e}")
            success = False
        finally:
            conn.close()
        
        return success

    def remove_song_from_playlist_db(self, user_id, playlist_name, song_number):
        """Remove a song from a playlist by number"""
        import os
        db_path = os.path.join(os.getcwd(), self.db_file)
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        try:
            # Get playlist ID
            cursor.execute('''
                SELECT id FROM playlists 
                WHERE user_id = ? AND playlist_name = ?
            ''', (str(user_id), playlist_name))
            
            playlist_row = cursor.fetchone()
            if not playlist_row:
                conn.close()
                return False, None
            
            playlist_id = playlist_row[0]
            
            # Get the song to remove
            cursor.execute('''
                SELECT id, title, page_url FROM songs 
                WHERE playlist_id = ? 
                ORDER BY position
                LIMIT 1 OFFSET ?
            ''', (playlist_id, song_number - 1))
            
            song_row = cursor.fetchone()
            if not song_row:
                conn.close()
                return False, None
            
            song_id, title, page_url = song_row
            
            # Delete the song
            cursor.execute('DELETE FROM songs WHERE id = ?', (song_id,))
            
            # Reorder remaining songs
            cursor.execute('''
                UPDATE songs 
                SET position = position - 1 
                WHERE playlist_id = ? AND position > ?
            ''', (playlist_id, song_number))
            
            conn.commit()
            success = True
            song_info = (title, page_url)
        except Exception as e:
            print(f"Error removing song from playlist: {e}")
            success = False
            song_info = None
        finally:
            conn.close()
        
        return success, song_info

    def delete_playlist_db(self, user_id, playlist_name):
        """Delete a playlist from the database"""
        import os
        db_path = os.path.join(os.getcwd(), self.db_file)
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                DELETE FROM playlists 
                WHERE user_id = ? AND playlist_name = ?
            ''', (str(user_id), playlist_name))
            
            conn.commit()
            success = cursor.rowcount > 0
        except Exception as e:
            print(f"Error deleting playlist: {e}")
            success = False
        finally:
            conn.close()
        
        return success

    async def join_vc(self, ctx):
        if ctx.author.voice:
            channel = ctx.author.voice.channel
            if not self.voice_client or not self.voice_client.is_connected():
                self.voice_client = await channel.connect()
                logger.info(f"Joined voice channel: {channel.name}")
            elif self.voice_client.channel != channel:
                await self.voice_client.move_to(channel)
                logger.info(f"Moved to voice channel: {channel.name}")
            return True
        await ctx.send("❌ You must be in a voice channel first!")
        return False

    async def leave_vc(self, ctx=None):
        if self.voice_client:
            await self.voice_client.disconnect()
            self.voice_client = None
            logger.info("Left voice channel")
        elif ctx:
            await ctx.send("❌ Not in a voice channel")

    async def get_youtube_audio(self, query):
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._sync_ytdl_extract, query)

    def _sync_ytdl_extract(self, query):
        ydl_opts = {
            'format': 'bestaudio/best',
            'default_search': 'ytsearch1',
            'noplaylist': True,
            'quiet': True,
            'socket_timeout': 30,
            'nocheckcertificate': True
        }
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            try:
                info = ydl.extract_info(query, download=False)
                if 'entries' in info:
                    video = info['entries'][0]
                else:
                    video = info
                return (
                    video['url'],
                    video.get('webpage_url', query),
                    video.get('title', 'Unknown Title')
                )
            except Exception as e:
                logger.error(f"YTDL Error: {str(e)}")
                raise

    @commands.command(name="play", help="Play a song from YouTube. Usage: /play <song name or URL>")
    async def play(self, ctx, *, query: str):
        """Play audio from YouTube"""
        if not await self.join_vc(ctx):
            return

        # Ensure voice_client is connected before proceeding
        if not self.voice_client or not self.voice_client.is_connected():
            await ctx.send("Not connected to voice. Please try again.")
            return

        try:
            audio_url, page_url, title = await self.get_youtube_audio(query)
            logger.info(f"Playing: {title} ({audio_url})")

            if self.voice_client.is_playing() or self.voice_client.is_paused():
                self.song_queue.append((audio_url, page_url, title))
                await ctx.send(f"🎶 Added to queue: [{title}]({page_url})")
                return

            self._play_audio(ctx, audio_url, page_url, title)
            await ctx.send(f"🎵 Now playing: [{title}]({page_url})")

        except Exception as e:
            logger.error(f"Play error: {str(e)}")
            await ctx.send(f" Error: {str(e)}")

    @commands.command(name="playlist", help="Play a playlist. Usage: /playlist <playlist name>")
    async def play_playlist(self, ctx, *, playlist_name: str):
        """Play a user's playlist"""
        if not await self.join_vc(ctx):
            return

        # Get songs from database
        songs = self.get_playlist_songs(ctx.author.id, playlist_name)
        
        if not songs:
            await ctx.send(f"❌ Playlist '{playlist_name}' not found or is empty!")
            return

        # Clear current queue and add all playlist songs
        self.song_queue.clear()
        self.song_queue.extend(songs)
        
        # Start playing the first song
        if self.song_queue:
            audio_url, page_url, title = self.song_queue.pop(0)
            self._play_audio(ctx, audio_url, page_url, title)
            await ctx.send(f"🎵 Playing playlist '{playlist_name}': [{title}]({page_url})")
        else:
            await ctx.send("❌ No songs in playlist!")

    @commands.command(name="createplaylist", help="Create a new playlist. Usage: /createplaylist <playlist name>")
    async def create_playlist(self, ctx, *, playlist_name: str):
        """Create a new playlist"""
        print(f"Creating playlist '{playlist_name}' for user {ctx.author.id}")  # Debug print
        
        success = self.create_playlist_db(ctx.author.id, playlist_name)
        
        if success:
            await ctx.send(f"✅ Created playlist '{playlist_name}'")
        else:
            await ctx.send(f"❌ Playlist '{playlist_name}' already exists!")

    @commands.command(name="addtoplaylist", help="Add a song to a playlist. Usage: /addtoplaylist <playlist name> <song name or URL>")
    async def add_to_playlist(self, ctx, playlist_name: str, *, song_query: str):
        """Add a song to a playlist"""
        try:
            audio_url, page_url, title = await self.get_youtube_audio(song_query)
            success = self.add_song_to_playlist_db(ctx.author.id, playlist_name, audio_url, page_url, title)
            
            if success:
                await ctx.send(f"✅ Added [{title}]({page_url}) to playlist '{playlist_name}'")
            else:
                await ctx.send(f"❌ Playlist '{playlist_name}' not found!")
        except Exception as e:
            await ctx.send(f"❌ Error adding song: {str(e)}")

    @commands.command(name="removefromplaylist", help="Remove a song from a playlist. Usage: /removefromplaylist <playlist name> <song number>")
    async def remove_from_playlist(self, ctx, playlist_name: str, song_number: int):
        """Remove a song from a playlist by number"""
        success, song_info = self.remove_song_from_playlist_db(ctx.author.id, playlist_name, song_number)
        
        if success and song_info:
            title, page_url = song_info
            await ctx.send(f"✅ Removed [{title}]({page_url}) from playlist '{playlist_name}'")
        elif not success and song_info is None:
            await ctx.send(f"❌ Playlist '{playlist_name}' not found!")
        else:
            await ctx.send(f"❌ Invalid song number!")

    @commands.command(name="deleteplaylist", help="Delete a playlist. Usage: /deleteplaylist <playlist name>")
    async def delete_playlist(self, ctx, *, playlist_name: str):
        """Delete a playlist"""
        success = self.delete_playlist_db(ctx.author.id, playlist_name)
        
        if success:
            await ctx.send(f"✅ Deleted playlist '{playlist_name}'")
        else:
            await ctx.send(f"❌ Playlist '{playlist_name}' not found!")

    @commands.command(name="listplaylists", help="List all your playlists")
    async def list_playlists(self, ctx):
        """List all playlists for the user"""
        playlists = self.get_user_playlists(ctx.author.id)
        
        if not playlists:
            await ctx.send("❌ You don't have any playlists!")
            return

        # Get song count for each playlist
        playlist_info = []
        for playlist_name in playlists:
            songs = self.get_playlist_songs(ctx.author.id, playlist_name)
            playlist_info.append(f"• {playlist_name} ({len(songs)} songs)")
        
        playlist_list = "\n".join(playlist_info)
        await ctx.send(f"📋 Your playlists:\n{playlist_list}")

    @commands.command(name="showplaylist", help="Show songs in a playlist. Usage: /showplaylist <playlist name>")
    async def show_playlist(self, ctx, *, playlist_name: str):
        """Show songs in a specific playlist"""
        songs = self.get_playlist_songs(ctx.author.id, playlist_name)
        
        if not songs:
            await ctx.send(f"❌ Playlist '{playlist_name}' not found or is empty!")
            return

        song_list = "\n".join([f"{i+1}. [{song[2]}]({song[1]})" for i, song in enumerate(songs)])
        await ctx.send(f"📋 Playlist '{playlist_name}':\n{song_list}")

    @commands.command(name="testplaylist", help="Test playlist functionality")
    async def test_playlist(self, ctx):
        """Test playlist functionality"""
        try:
            # Test creating a playlist
            success = self.create_playlist_db(ctx.author.id, "test_playlist")
            print(f"Create playlist result: {success}")
            
            # Test adding a song
            song_success = self.add_song_to_playlist_db(ctx.author.id, "test_playlist", "test_url", "test_page", "Test Song")
            print(f"Add song result: {song_success}")
            
            # Test getting playlists
            playlists = self.get_user_playlists(ctx.author.id)
            print(f"User playlists: {playlists}")
            
            # Test getting songs
            songs = self.get_playlist_songs(ctx.author.id, "test_playlist")
            print(f"Playlist songs: {songs}")
            
            await ctx.send("✅ Playlist test completed! Check console for output.")
        except Exception as e:
            await ctx.send(f"❌ Playlist test failed: {str(e)}")
            print(f"Test failed: {e}")

    @commands.command(name="loop", help="Toggle looping the current song")
    async def loop(self, ctx):
        """Toggle loop for the current song."""
        self.loop_enabled = not self.loop_enabled
        if self.loop_enabled:
            await ctx.send("Loop enabled for the current song.")
        else:
            await ctx.send("Loop disabled.")

    def _play_audio(self, ctx, audio_url, page_url, title):
        self.music_playing = True
        self.last_activity_time = time.time()
        self.current_song = (audio_url, page_url, title)  # Track the current song

        ffmpeg_options = {
            'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
            'options': '-vn -b:a 128k -ac 2'
        }

        self.voice_client.play(
            discord.FFmpegOpusAudio(
                executable="ffmpeg",
                source=audio_url,
                **ffmpeg_options
            ),
            after=lambda e: self.bot.loop.create_task(self._after_play(e, ctx))
        )

    async def _after_play(self, error, ctx):
        self.music_playing = False
        if error:
            logger.error(f"Playback error: {error}")
            await ctx.send(f"❌ Playback error: {error}")

        if self.loop_enabled and self.current_song:
            # Replay the current song
            audio_url, page_url, title = self.current_song
            self._play_audio(ctx, audio_url, page_url, title)
            await ctx.send(f"Replaying: [{title}]({page_url})")
            return

        if self.song_queue:
            next_url, next_page, next_title = self.song_queue.pop(0)
            self._play_audio(ctx, next_url, next_page, next_title)
            await ctx.send(f"Now playing: [{next_title}]({next_page})")
        else:
            await self.leave_vc()

    @commands.command(name="stop", help="Stops the song and removes the bot from VC")
    async def stop(self, ctx):
        """Stop playback and clear queue"""
        if self.voice_client:
            self.song_queue.clear()
            self.voice_client.stop()
            await self.leave_vc()
        else:
            await ctx.send("Not playing anything")

    @commands.command(name="skip", help="Skips to next song in the queue")
    async def skip(self, ctx):
        """Skip current track"""
        if self.voice_client and self.voice_client.is_playing():
            self.voice_client.stop()
            await ctx.send("Skipped current track")
        else:
            await ctx.send("Nothing to skip")

    @commands.command(name="queue", help="Shows songs in queue")
    async def queue(self, ctx):
        """Show current queue"""
        if not self.song_queue:
            await ctx.send("Queue is empty")
            return

        queue_list = "\n".join(
            [f"{i+1}. [{song[2]}]({song[1]})" for i, song in enumerate(self.song_queue)]
        )
        await ctx.send(f"🎶 Current queue:\n{queue_list}")

    @tasks.loop(seconds=60)
    async def _check_inactivity(self):
        if (self.voice_client and
            not self.voice_client.is_playing() and
            (time.time() - self.last_activity_time) > 300):
            logger.info("Inactivity timeout - leaving voice channel")
            await self.leave_vc()

    @commands.Cog.listener()
    async def on_ready(self):
        self._check_inactivity.start()

async def setup(bot):
    await bot.add_cog(Music(bot))
