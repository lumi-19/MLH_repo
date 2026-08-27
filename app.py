from flask import Flask
from routes import initialize_routes

app = Flask(__name__)
initialize_routes(app)

if __name__ == '__main__':
    # Bind to 0.0.0.0 to make it accessible in the preview environment
    app.run(debug=True, host='0.0.0.0')
