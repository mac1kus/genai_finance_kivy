import os
from app_creator import app

# Import routes so they get attached to the app
import routes

if __name__ == "__main__":
    # Render provides a 'PORT' variable; we default to 5001 for local testing
    port = int(os.environ.get("PORT", 5001))
    
    # We use '0.0.0.0' to ensure it's accessible externally on the network
    app.run(host='0.0.0.0', port=port, debug=True)