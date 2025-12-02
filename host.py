import os
import sys
from pyngrok import ngrok
from threading import Thread
import time

# Add backend directory to path so we can import app
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))
from app import app

def run_app():
    # Run Flask app without reloader to avoid main thread issues
    app.run(port=5000, use_reloader=False)

def start_host():
    print("Starting Flask server...")
    server_thread = Thread(target=run_app)
    server_thread.daemon = True
    server_thread.start()

    # Give server a moment to start
    time.sleep(2)

    print("Opening Ngrok tunnel...")
    # Open a HTTP tunnel on the default port 5000
    public_url = ngrok.connect(5000).public_url
    
    print("\n" + "="*60)
    print(f" YOUR PUBLIC URL IS: {public_url}")
    print("="*60 + "\n")
    print("Share this link with anyone to access your website.")
    print("Press CTRL+C to stop hosting.")

    try:
        # Keep the main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping hosting...")
        ngrok.kill()
        sys.exit(0)

if __name__ == "__main__":
    start_host()
