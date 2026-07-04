from flask import Flask, jsonify
import threading
import os
import logging
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Global flag to track bot status
bot_running = False

@app.route('/')
def home():
    return jsonify({
        "status": "online",
        "bot": "My Word Finder Bot",
        "bot_running": bot_running,
        "message": "Bot is running smoothly! 🚀"
    })

@app.route('/health')
def health():
    return jsonify({
        "status": "healthy",
        "bot_running": bot_running
    }), 200

@app.route('/status')
def status():
    return jsonify({
        "bot_running": bot_running,
        "port": os.environ.get("PORT", 5000)
    })

def run_bot_thread():
    """Run the bot in a separate thread"""
    global bot_running
    try:
        logger.info("Starting bot thread...")
        from bot import run_bot
        bot_running = True
        run_bot()
    except Exception as e:
        bot_running = False
        logger.error(f"❌ Bot thread failed: {e}")

if __name__ == "__main__":
    # Give a small delay to ensure everything is loaded
    time.sleep(1)
    
    # Start bot in a background thread
    logger.info("Initializing bot...")
    bot_thread = threading.Thread(target=run_bot_thread, daemon=True)
    bot_thread.start()
    
    # Give the bot time to start
    time.sleep(2)
    
    # Run Flask app
    port = int(os.environ.get("PORT", 5000))
    logger.info(f"🚀 Starting Flask server on port {port}...")
    app.run(host="0.0.0.0", port=port)
