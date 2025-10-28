import os
import logging
import requests
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from urllib.parse import quote
import yt_dlp

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Bot token from environment
BOT_TOKEN = os.getenv('BOT_TOKEN')

# YouTube DL options
ydl_opts = {
    'format': 'best[height<=720]',
    'outtmpl': 'downloads/%(title)s.%(ext)s',
    'quiet': True,
}

class MovieDownloadBot:
    def __init__(self):
        self.search_results = {}
        
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        welcome_text = """
🎬 **Welcome to Movie Download Bot** 🎬

I can help you search and download movies/series.

**Features:**
• Search movies by name
• Multiple quality options
• Fast download links
• TV series support

**How to use:**
1. Send me a movie/series name
2. Choose from search results
3. Select quality
4. Download your file

⚠️ *Only for educational purposes*
        """
        
        keyboard = [
            [InlineKeyboardButton("🔍 Search Movies", switch_inline_query_current_chat="")],
            [InlineKeyboardButton("📖 Help", callback_data="help"),
             InlineKeyboardButton("ℹ️ About", callback_data="about")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(welcome_text, reply_markup=reply_markup)

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        help_text = """
📖 **Help Guide**

**Commands:**
/start - Start the bot
/search <movie name> - Search for movies
/help - Show this help message

**How to download:**
1. Send movie name directly or use /search command
2. Bot will show search results
3. Click on desired movie
4. Choose quality (480p, 720p, 1080p)
5. Wait for download link

**Supported:**
• Movies 🎬
• TV Series 📺
• Multiple languages 🌍
• Various qualities 📹

**Note:** Download speed depends on file size and server load.
        """
        await update.message.reply_text(help_text)

    async def handle_search(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = ' '.join(context.args)
        if not query:
            await update.message.reply_text("Please provide a movie name. Example: `/search Avengers`", parse_mode='Markdown')
            return
        
        await self.search_movies(update, query)

    async def search_movies(self, update: Update, query: str):
        try:
            # Simulate search (replace with actual movie API)
            search_url = f"http://www.omdbapi.com/?i=tt3896198&apikey=227a86bc={quote(query)}"
            
            # For demo, using mock data
            mock_results = [
                {"title": f"{query} (2023)", "year": "2023", "imdb": "tt1234567", "type": "movie"},
                {"title": f"{query} Part 2", "year": "2022", "imdb": "tt1234568", "type": "movie"},
                {"title": f"{query} TV Series", "year": "2021-2023", "imdb": "tt1234569", "type": "series"},
            ]
            
            keyboard = []
            for i, movie in enumerate(mock_results):
                keyboard.append([
                    InlineKeyboardButton(
                        f"🎬 {movie['title']} ({movie['year']})", 
                        callback_data=f"select_{i}"
                    )
                ])
            
            # Store results in context for callback
            context.user_data['search_results'] = mock_results
            context.user_data['search_query'] = query
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(
                f"🔍 Search results for: **{query}**\n\nSelect a movie:",
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            
        except Exception as e:
            logger.error(f"Search error: {e}")
            await update.message.reply_text("❌ Search failed. Please try again.")

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.message.text and not update.message.text.startswith('/'):
            await self.search_movies(update, update.message.text)

    async def button_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        
        data = query.data
        user_data = context.user_data
        
        if data == "help":
            await self.help_command(update, context)
            return
        elif data == "about":
            about_text = """
ℹ️ **About This Bot**

🤖 **Movie Download Bot**
Version: 2.0
Developer: Your Name

🔧 **Technology:**
• Python Telegram Bot
• yt-dlp for downloads
• Multiple sources

📜 **Disclaimer:**
This bot is for educational purposes only. 
Respect copyright laws in your country.
            """
            await query.edit_message_text(about_text)
            return
        
        if data.startswith("select_"):
            index = int(data.split("_")[1])
            movie = user_data['search_results'][index]
            await self.show_quality_options(query, movie)
        
        elif data.startswith("quality_"):
            # data format: quality_movieId_quality
            parts = data.split("_")
            movie_id = parts[1]
            quality = parts[2]
            await self.process_download(query, movie_id, quality)

    async def show_quality_options(self, query, movie):
        keyboard = [
            [
                InlineKeyboardButton("📹 480p", callback_data=f"quality_{movie['imdb']}_480"),
                InlineKeyboardButton("🎥 720p", callback_data=f"quality_{movie['imdb']}_720")
            ],
            [
                InlineKeyboardButton("🎬 1080p", callback_data=f"quality_{movie['imdb']}_1080"),
                InlineKeyboardButton("🔙 Back", callback_data="back_to_search")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        text = f"""
🎬 **{movie['title']}**

📅 Year: {movie['year']}
🎭 Type: {movie['type'].title()}

Select download quality:
        """
        
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')

    async def process_download(self, query, movie_id, quality):
        try:
            # Show downloading message
            await query.edit_message_text(f"⏬ Downloading in {quality}p...\n\nPlease wait, this may take a few minutes.")
            
            # Simulate download process
            await asyncio.sleep(2)
            
            # Mock download links (replace with actual download logic)
            download_links = {
                "480p": "https://example.com/movie_480p.mp4",
                "720p": "https://example.com/movie_720p.mp4", 
                "1080p": "https://example.com/movie_1080p.mp4"
            }
            
            download_url = download_links.get(quality, download_links["720p"])
            
            # Send download link
            keyboard = [
                [InlineKeyboardButton("📥 Download Now", url=download_url)],
                [InlineKeyboardButton("🔍 Search Again", callback_data="back_to_search")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                f"✅ **Download Ready!**\n\n"
                f"🎬 Quality: {quality}p\n"
                f"📦 File Size: ~1.5GB\n"
                f"⏱️ Duration: 2h 15m\n\n"
                f"Click the button below to download:",
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            
        except Exception as e:
            logger.error(f"Download error: {e}")
            await query.edit_message_text("❌ Download failed. Please try again later.")

    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        logger.error(f"Exception: {context.error}")

def main():
    # Create bot instance
    bot = MovieDownloadBot()
    
    # Create application
    application = Application.builder().token(BOT_TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler("start", bot.start))
    application.add_handler(CommandHandler("help", bot.help_command))
    application.add_handler(CommandHandler("search", bot.handle_search))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, bot.handle_message))
    application.add_handler(CallbackQueryHandler(bot.button_handler))
    
    # Error handler
    application.add_error_handler(bot.error_handler)

    # Start bot
    print("🎬 Movie Download Bot is running...")
    application.run_polling()

if __name__ == '__main__':
    # Create downloads directory
    os.makedirs('downloads', exist_ok=True)
    main()