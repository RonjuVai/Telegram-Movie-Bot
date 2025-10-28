import os
import logging
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from urllib.parse import quote

# Enhanced logging configuration
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('bot.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

# Bot token from environment
BOT_TOKEN = os.getenv('8420353064:AAHMWwrXujws6I-nsFdtnU-UcMALnoOLygA')

if not BOT_TOKEN:
    logger.error("❌ BOT_TOKEN environment variable is not set!")
    raise ValueError("BOT_TOKEN environment variable is required")

class MovieDownloadBot:
    def __init__(self):
        self.search_results = {}
        logger.info("MovieDownloadBot initialized successfully")
        
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
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
                [InlineKeyboardButton("📖 Help", callback_data="help"),
                 InlineKeyboardButton("ℹ️ About", callback_data="about")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(welcome_text, reply_markup=reply_markup)
            logger.info(f"Start command executed for user {update.effective_user.id}")
            
        except Exception as e:
            logger.error(f"Error in start command: {e}")
            await update.message.reply_text("❌ Bot startup failed. Please try again.")

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            help_text = """
📖 **Help Guide**

**Commands:**
/start - Start the bot
/help - Show this help message

**How to download:**
1. Send movie name directly
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
            
        except Exception as e:
            logger.error(f"Error in help command: {e}")
            await update.message.reply_text("❌ Help command failed.")

    async def handle_search(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            query = ' '.join(context.args)
            if not query:
                await update.message.reply_text(
                    "Please provide a movie name. Example: `/search Avengers`", 
                    parse_mode='Markdown'
                )
                return
            
            await self.search_movies(update, query, context)
            
        except Exception as e:
            logger.error(f"Error in handle_search: {e}")
            await update.message.reply_text("❌ Search command failed.")

    async def search_movies(self, update: Update, query: str, context: ContextTypes.DEFAULT_TYPE):
        try:
            logger.info(f"Searching for: {query}")
            
            # For demo, using mock data - safer implementation
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
            
            # Store results safely in context
            if 'search_data' not in context.user_data:
                context.user_data['search_data'] = {}
                
            context.user_data['search_data']['results'] = mock_results
            context.user_data['search_data']['query'] = query
            
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
        try:
            if update.message.text and not update.message.text.startswith('/'):
                query = update.message.text.strip()
                if len(query) < 2:
                    await update.message.reply_text("❌ Please enter a longer movie name.")
                    return
                    
                await self.search_movies(update, query, context)
                
        except Exception as e:
            logger.error(f"Error handling message: {e}")
            await update.message.reply_text("❌ Error processing your message.")

    async def button_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            query = update.callback_query
            await query.answer()
            
            data = query.data
            
            if data == "help":
                await self.show_help(query)
            elif data == "about":
                await self.show_about(query)
            elif data == "back_to_search":
                await self.back_to_search(query, context)
            elif data.startswith("select_"):
                await self.handle_movie_selection(query, context)
            elif data.startswith("quality_"):
                await self.handle_quality_selection(query)
            else:
                await query.edit_message_text("❌ Unknown command received.")
                
        except Exception as e:
            logger.error(f"Button handler error: {e}")
            try:
                await query.edit_message_text("❌ Error processing your request.")
            except Exception:
                # If we can't edit the message, send a new one
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text="❌ An error occurred. Please try again."
                )

    async def show_help(self, query):
        try:
            help_text = """
📖 **Help Guide**

Send me any movie name to search and download.
Example: `Avengers`, `Spider-Man`, `Inception`

I'll show you search results and download options.
            """
            await query.edit_message_text(help_text, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"Error showing help: {e}")

    async def show_about(self, query):
        try:
            about_text = """
ℹ️ **About This Bot**

🤖 **Movie Download Bot**
Version: 2.0

🔧 **Technology:**
• Python Telegram Bot
• Secure downloads

📜 **Disclaimer:**
This bot is for educational purposes only. 
Respect copyright laws in your country.
            """
            await query.edit_message_text(about_text)
            
        except Exception as e:
            logger.error(f"Error showing about: {e}")

    async def back_to_search(self, query, context):
        try:
            search_data = context.user_data.get('search_data', {})
            original_query = search_data.get('query', 'movies')
            
            # Recreate search results
            mock_results = [
                {"title": f"{original_query} (2023)", "year": "2023", "imdb": "tt1234567", "type": "movie"},
                {"title": f"{original_query} Part 2", "year": "2022", "imdb": "tt1234568", "type": "movie"},
            ]
            
            keyboard = []
            for i, movie in enumerate(mock_results):
                keyboard.append([
                    InlineKeyboardButton(
                        f"🎬 {movie['title']} ({movie['year']})", 
                        callback_data=f"select_{i}"
                    )
                ])
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                f"🔍 Search results for: **{original_query}**\n\nSelect a movie:",
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            
        except Exception as e:
            logger.error(f"Error in back_to_search: {e}")
            await query.edit_message_text("❌ Error returning to search.")

    async def handle_movie_selection(self, query, context):
        try:
            data = query.data
            index = int(data.split("_")[1])
            
            search_data = context.user_data.get('search_data', {})
            results = search_data.get('results', [])
            
            if 0 <= index < len(results):
                movie = results[index]
                await self.show_quality_options(query, movie)
            else:
                await query.edit_message_text("❌ Movie not found. Please search again.")
                
        except (ValueError, IndexError) as e:
            logger.error(f"Movie selection error: {e}")
            await query.edit_message_text("❌ Invalid selection. Please try again.")

    async def show_quality_options(self, query, movie):
        try:
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
            
        except Exception as e:
            logger.error(f"Error showing quality options: {e}")
            await query.edit_message_text("❌ Error showing quality options.")

    async def handle_quality_selection(self, query):
        try:
            data = query.data
            parts = data.split("_")
            if len(parts) != 3:
                raise ValueError("Invalid quality data format")
                
            movie_id = parts[1]
            quality = parts[2]
            
            await self.process_download(query, movie_id, quality)
            
        except Exception as e:
            logger.error(f"Quality selection error: {e}")
            await query.edit_message_text("❌ Error processing quality selection.")

    async def process_download(self, query, movie_id, quality):
        try:
            # Show downloading message
            await query.edit_message_text(f"⏬ Downloading in {quality}p...\n\nPlease wait, this may take a few minutes.")
            
            # Simulate download process
            await asyncio.sleep(3)
            
            # Mock download links
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
            logger.error(f"Download process error: {e}")
            await query.edit_message_text("❌ Download failed. Please try again later.")

    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            logger.error(f"Exception occurred: {context.error}", exc_info=True)
            
            # Send error message to user
            if update and update.effective_chat:
                error_message = "❌ An unexpected error occurred. Our developers have been notified."
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=error_message
                )
        except Exception as e:
            logger.error(f"Error in error handler: {e}")

def main():
    try:
        logger.info("🚀 Starting Movie Download Bot...")
        
        # Validate token
        if not BOT_TOKEN:
            logger.error("❌ BOT_TOKEN not found in environment variables!")
            return
        
        # Create bot instance
        bot = MovieDownloadBot()
        
        # Create application with better configuration
        application = Application.builder().token(BOT_TOKEN).build()
        
        # Add handlers with specific order
        application.add_handler(CommandHandler("start", bot.start))
        application.add_handler(CommandHandler("help", bot.help_command))
        application.add_handler(CommandHandler("search", bot.handle_search))
        application.add_handler(CallbackQueryHandler(bot.button_handler))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, bot.handle_message))
        
        # Add error handler
        application.add_error_handler(bot.error_handler)
        
        # Start bot with better configuration
        logger.info("🤖 Bot started successfully - Waiting for messages...")
        application.run_polling(
            drop_pending_updates=True,
            allowed_updates=Update.ALL_TYPES,
            close_loop=False
        )
        
    except Exception as e:
        logger.critical(f"❌ Critical error in main: {e}", exc_info=True)

if __name__ == '__main__':
    # Create downloads directory if needed
    os.makedirs('downloads', exist_ok=True)
    
    # Set event loop policy for Windows compatibility (if needed)
    if os.name == 'nt':
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    
    main()
