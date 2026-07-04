from flask import Flask, jsonify
import threading
import os
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({
        "status": "online",
        "bot": "My Word Finder Bot",
        "message": "Bot is running smoothly! 🚀"
    })

@app.route('/health')
def health():
    return jsonify({"status": "healthy"}), 200

def run_bot():
    """Run the bot in a separate thread"""
    try:
        from bot import main
        main()
    except Exception as e:
        logger.error(f"Bot failed: {e}")

if __name__ == "__main__":
    # Start bot in background thread
    logger.info("Starting bot thread...")
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()
    
    # Run Flask app
    port = int(os.environ.get("PORT", 5000))
    logger.info(f"Starting Flask app on port {port}...")
    app.run(host="0.0.0.0", port=port)
