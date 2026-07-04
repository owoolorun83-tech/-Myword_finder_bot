# 📖 My Word Finder Bot

A powerful Telegram bot that helps you find definitions, synonyms, and antonyms.

## ✨ Features
- 📖 Get word definitions with examples
- 🔀 Find synonyms
- ❌ Find antonyms
- 📝 Interactive buttons for quick access
- 🎯 Multiple dictionary sources for accuracy
- ⚡ Fast and reliable

## 🚀 Commands
- `/start` - Welcome message
- `/help` - Show help menu
- `/define <word>` - Get full definition
- `/synonym <word>` - Get synonyms
- `/antonym <word>` - Get antonyms

## 🛠️ Deployment

### Prerequisites
- Python 3.11+
- Railway account
- GitHub account

### Steps

1. **Create bot on Telegram**
   - Message @BotFather
   - Send `/newbot`
   - Name: `My Word Finder Bot`
   - Username: `@Myword_finder_bot`
   - Save the API token

2. **Deploy on Railway**
   - Push code to GitHub
   - Connect GitHub to Railway
   - Set environment variable:
     - `TELEGRAM_BOT_TOKEN` = your bot token

3. **Test your bot**
   - Open Telegram
   - Search `@Myword_finder_bot`
   - Send a word!

## 📝 License
MIT
