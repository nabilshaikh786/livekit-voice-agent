import os
from dotenv import load_dotenv
from livekit.api import AccessToken, VideoGrants

load_dotenv()

API_KEY = os.getenv("LIVEKIT_API_KEY")
API_SECRET = os.getenv("LIVEKIT_API_SECRET")
ROOM_NAME = os.getenv("ROOM_NAME", "ai-room")

def generate_user_token():
    token = (
        AccessToken(API_KEY, API_SECRET)
        .with_identity("browser-user")
        .with_name("Browser User")
        .with_grants(
            VideoGrants(
                room_join=True,
                room=ROOM_NAME,
            )
        )
        .to_jwt()
    )
    return token

print(generate_user_token())