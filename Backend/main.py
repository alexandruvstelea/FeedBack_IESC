from __init__ import init_app
from flask_cors import CORS

app = init_app()

if __name__ == "__main__":
    CORS(app,supports_credentials=True)
    app.run(host="0.0.0.0")
