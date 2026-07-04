import os
import logging
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from PyDictionary import PyDictionary

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Get token from environment variable
TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')

# Initialize dictionary
dictionary = PyDictionary()

# Free Dictionary API (more reliable)
FREE_DICT_API = "https://api.dictionaryapi.dev/api/v2/entries/en/"

def get_meaning_from_api(word):
    """Fetch word meaning from Free Dictionary API"""
    try:
        response = requests.get(f"{FREE_DICT_API}{word}", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data and len(data) > 0:
                result = f"📖 *{word.capitalize()}*\n\n"
                
                entry = data[0]
                if 'meanings' in entry:
                    for meaning in entry['meanings']:
                        part_of_speech = meaning.get('partOfSpeech', 'Unknown')
                        result += f"*{part_of_speech.upper()}:*\n"
                        
                        definitions = meaning.get('definitions', [])
                        for i, definition in enumerate(definitions[:3], 1):
                            result += f"  {i}. {definition.get('definition', 'No definition')}\n"
                            if 'example' in definition and definition['example']:
                                result += f"     📝 *Example:* {definition['example']}\n"
                        result += "\n"
                
                # Add synonyms and antonyms
                if 'meanings' in entry:
                    all_synonyms = []
                    all_antonyms = []
                    for meaning in entry['meanings']:
                        synonyms = meaning.get('synonyms', [])
                        antonyms = meaning.get('antonyms', [])
                        all_synonyms.extend(synonyms)
                        all_antonyms.extend(antonyms)
                    
                    if all_synonyms:
                        result += f"*Synonyms:* {', '.join(all_synonyms[:5])}\n"
                    if all_antonyms:
                        result += f"*Antonyms:* {', '.join(all_antonyms[:5])}\n"
                
                return result
        return None
    except Exception as e:
        logger.error(f"API Error: {e}")
        return None

def get_meaning_pydictionary(word):
    """Get meaning using PyDictionary"""
    try:
        meanings = dictionary.meaning(word)
        if meanings:
            result = f"📖 *{word.capitalize()}*\n\n"
            for pos, definitions in meanings.items():
                result += f"*{pos.upper()}:*\n"
                for i, definition in enumerate(definitions, 1):
                    result += f"  {i}. {definition}\n"
                result += "\n"
            return result
        return None
    except Exception as e:
        logger.error(f"PyDictionary Error: {e}")
        return None

def get_word_definition(word):
    """Get word definition with fallback mechanism"""
    word = word.strip().lower()
    if not word or len(word) > 50:
        return "❌ Please provide a valid word (max 50 characters)."
    
    # Try Free Dictionary API first
    result = get_meaning_from_api(word)
    if result:
        return result
    
    # Fallback to PyDictionary
    result = get_meaning_pydictionary(word)
    if result:
        return result
    
    return f"❌ Sorry, I couldn't find the definition for '*{word}*'.\n\nPlease check the spelling or try another word."

def get_synonyms(word):
    """Get synonyms for a word"""
    try:
        word = word.strip().lower()
        # Try API first
        response = requests.get(f"{FREE_DICT_API}{word}", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data:
                synonyms = []
                for entry in data:
                    if 'meanings' in entry:
                        for meaning in entry['meanings']:
                            if 'synonyms' in meaning:
                                synonyms.extend(meaning['synonyms'])
                if synonyms:
                    unique_synonyms = list(set(synonyms))
                    return unique_synonyms[:10]
        
        # Fallback to PyDictionary
        synonyms = dictionary.synonym(word)
        if synonyms:
            return synonyms[:10]
        return []
    except Exception as e:
        logger.error(f"Synonym Error: {e}")
        return []

def get_antonyms(word):
    """Get antonyms for a word"""
    try:
        word = word.strip().lower()
        # Try API first
        response = requests.get(f"{FREE_DICT_API}{word}", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data:
                antonyms = []
                for entry in data:
                    if 'meanings' in entry:
                        for meaning in entry['meanings']:
                            if 'antonyms' in meaning:
                                antonyms.extend(meaning['antonyms'])
                if antonyms:
                    unique_antonyms = list(set(antonyms))
                    return unique_antonyms[:10]
        
        # Fallback to PyDictionary
        antonyms = dictionary.antonym(word)
        if antonyms:
            return antonyms[:10]
        return []
    except Exception as e:
        logger.error(f"Antonym Error: {e}")
        return []

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send welcome message"""
    welcome_text = (
        "👋 *Welcome to My Word Finder Bot!*\n\n"
        "I can help you explore the English language by providing:\n"
        "📖 *Definitions*\n"
        "🔀 *Synonyms*\n"
        "❌ *Antonyms*\n"
        "📝 *Example Sentences*\n\n"
        "📌 *How to use:*\n"
        "• Simply send me any word\n"
        "• Or use these commands:\n\n"
        "/define <word> - Get definition\n"
        "/synonym <word> - Get synonyms\n"
        "/antonym <word> - Get antonyms\n"
        "/help - Show this help\n\n"
        "🤖 *Try it now!* Send me a word like 'happiness'"
    )
    await update.message.reply_text(welcome_text, parse_mode='Markdown')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send help message"""
    help_text = (
        "📚 *Available Commands*\n\n"
        "/start - Welcome message\n"
        "/help - Show this help\n"
        "/define <word> - Get full definition\n"
        "/synonym <word> - Get synonyms\n"
        "/antonym <word> - Get antonyms\n\n"
        "💡 *Quick Tip:*\n"
        "Just send any word directly and I'll find its meaning!\n\n"
        "📊 *Features:*\n"
        "✅ Multiple dictionary sources\n"
        "✅ Examples & usage\n"
        "✅ Synonyms & antonyms\n"
        "✅ Interactive buttons"
    )
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def define_word(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /define command"""
    if not context.args:
        await update.message.reply_text(
            "📝 Please provide a word.\n\nExample: `/define happiness`",
            parse_mode='Markdown'
        )
        return
    
    word = ' '.join(context.args)
    await update.message.chat.send_action(action="typing")
    result = get_word_definition(word)
    
    # Add helpful keyboard
    keyboard = [
        [
            InlineKeyboardButton("🔄 Synonyms", callback_data=f"syn_{word}"),
            InlineKeyboardButton("❌ Antonyms", callback_data=f"ant_{word}")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        result, 
        parse_mode='Markdown',
        reply_markup=reply_markup
    )

async def synonym_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /synonym command"""
    if not context.args:
        await update.message.reply_text(
            "📝 Please provide a word.\n\nExample: `/synonym happy`",
            parse_mode='Markdown'
        )
        return
    
    word = ' '.join(context.args)
    await update.message.chat.send_action(action="typing")
    synonyms = get_synonyms(word)
    
    if synonyms and len(synonyms) > 0:
        result = f"🔀 *Synonyms for '{word}':*\n\n{', '.join(synonyms)}"
    else:
        result = f"❌ No synonyms found for '*{word}*'."
    
    await update.message.reply_text(result, parse_mode='Markdown')

async def antonym_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /antonym command"""
    if not context.args:
        await update.message.reply_text(
            "📝 Please provide a word.\n\nExample: `/antonym sad`",
            parse_mode='Markdown'
        )
        return
    
    word = ' '.join(context.args)
    await update.message.chat.send_action(action="typing")
    antonyms = get_antonyms(word)
    
    if antonyms and len(antonyms) > 0:
        result = f"❌ *Antonyms for '{word}':*\n\n{', '.join(antonyms)}"
    else:
        result = f"❌ No antonyms found for '*{word}*'."
    
    await update.message.reply_text(result, parse_mode='Markdown')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle regular text messages"""
    word = update.message.text.strip()
    
    if len(word) < 2:
        await update.message.reply_text("📝 Please send a valid word (at least 2 characters).")
        return
    if len(word) > 50:
        await update.message.reply_text("📝 Please send a shorter word (max 50 characters).")
        return
    
    await update.message.chat.send_action(action="typing")
    result = get_word_definition(word)
    
    # Add helpful keyboard
    keyboard = [
        [
            InlineKeyboardButton("🔄 Synonyms", callback_data=f"syn_{word}"),
            InlineKeyboardButton("❌ Antonyms", callback_data=f"ant_{word}")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        result, 
        parse_mode='Markdown',
        reply_markup=reply_markup
    )

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle inline keyboard button presses"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    if data.startswith("syn_"):
        word = data[4:]
        await query.message.chat.send_action(action="typing")
        synonyms = get_synonyms(word)
        if synonyms and len(synonyms) > 0:
            result = f"🔀 *Synonyms for '{word}':*\n\n{', '.join(synonyms)}"
        else:
            result = f"❌ No synonyms found for '*{word}*'."
        await query.edit_message_text(result, parse_mode='Markdown')
    
    elif data.startswith("ant_"):
        word = data[4:]
        await query.message.chat.send_action(action="typing")
        antonyms = get_antonyms(word)
        if antonyms and len(antonyms) > 0:
            result = f"❌ *Antonyms for '{word}':*\n\n{', '.join(antonyms)}"
        else:
            result = f"❌ No antonyms found for '*{word}*'."
        await query.edit_message_text(result, parse_mode='Markdown')

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle errors"""
    logger.error(f"Update {update} caused error {context.error}")
    if update and update.effective_message:
        await update.effective_message.reply_text(
            "⚠️ An error occurred. Please try again later or use a different word."
        )

def main():
    """Start the bot"""
    if not TOKEN:
        logger.error("❌ No token provided! Set TELEGRAM_BOT_TOKEN environment variable.")
        return
    
    # Create application
    application = Application.builder().token(TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("define", define_word))
    application.add_handler(CommandHandler("synonym", synonym_command))
    application.add_handler(CommandHandler("antonym", antonym_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(CallbackQueryHandler(button_callback))
    
    # Add error handler
    application.add_error_handler(error_handler)
    
    # Start polling
    logger.info("🚀 Bot is starting...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
