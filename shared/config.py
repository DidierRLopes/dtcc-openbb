from pathlib import Path

ROOT_PATH = Path(__file__).parent.parent.resolve()

CORS_SETTINGS = {
    "allow_origins": [
        "https://pro.openbb.co",
        "https://pro.openbb.dev",
        "http://localhost:3000",
        "http://localhost:1420",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:1420"
    ],
    "allow_credentials": True,
    "allow_methods": ["*"],
    "allow_headers": ["*"],
}