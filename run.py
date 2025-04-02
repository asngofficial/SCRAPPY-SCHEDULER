import sys
from pathlib import Path
from app import create_app
import os
from werkzeug.serving import run_simple
from werkzeug.middleware.proxy_fix import ProxyFix

# Add project root to Python path
sys.path.append(str(Path(__file__).parent))

app = create_app()

# Configure for reverse proxy if running behind one
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

def run_server():
    """Run the application with enhanced configuration"""
    host = os.environ.get('FLASK_HOST', '0.0.0.0')
    port = int(os.environ.get('FLASK_PORT', 5000))
    
    if os.environ.get('FLASK_ENV') == 'production':
        # Production configuration
        run_simple(
            hostname=host,
            port=port,
            application=app,
            use_reloader=False,
            use_debugger=False,
            threaded=True
        )
    else:
        # Development configuration
        app.run(
            host=host,
            port=port,
            debug=True,
            use_reloader=True,
            threaded=True
        )

if __name__ == '__main__':
    run_server()