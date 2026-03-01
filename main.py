
import asyncio
import os
import time
import webrtcvad
from dotenv import load_dotenv
from livekit import rtc
from livekit.api import AccessToken, VideoGrants
from openai import OpenAI

load_dotenv()

LIVEKIT_URL = os.getenv("LIVEKIT_URL")
API_KEY = os.getenv("LIVEKIT_API_KEY")
API_SECRET = os.getenv("LIVEKIT_API_SECRET")
ROOM_NAME = os.getenv("ROOM_NAME")
OPENAI_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_KEY:
    raise Exception("OPENAI_API_KEY missing in .env")

client = OpenAI(api_key=OPENAI_KEY)

SAMPLE_RATE = 16000
CHANNELS = 1
FRAME_DURATION = 20  # ms
FRAME_SIZE = int(SAMPLE_RATE * FRAME_DURATION / 1000) * 2

vad = webrtcvad.Vad(2)

is_speaking = False
user_speaking = False
last_user_audio = time.time()
audio_buffer = bytearray()


# ================= TOKEN =================

def generate_token(identity):
    return (
        AccessToken(API_KEY, API_SECRET)
        .with_identity(identity)
        .with_name(identity)
        .with_grants(VideoGrants(room_join=True, room=ROOM_NAME))
        .to_jwt()
    )


# ================= STT =================

async def speech_to_text(pcm_data):
    with open("temp.wav", "wb") as f:
        f.write(pcm_data)

    transcript = client.audio.transcriptions.create(
        file=open("temp.wav", "rb"),
        model="whisper-1"
    )

    return transcript.text


# ================= TTS =================

async def text_to_speech(text):
    response = client.audio.speech.create(
        model="gpt-4o-mini-tts",
        voice="alloy",
        input=text
    )

    return response.content


# ================= STREAM AUDIO =================

async def stream_audio(source, audio_bytes):
    global is_speaking, user_speaking

    is_speaking = True

    for i in range(0, len(audio_bytes), FRAME_SIZE):

        # INTERRUPT CHECK
        if user_speaking:
            print("🔴 Interrupted by user")
            break

        chunk = audio_bytes[i:i + FRAME_SIZE]

        frame = rtc.AudioFrame(
            chunk,
            SAMPLE_RATE,
            CHANNELS,
            len(chunk) // 2
        )

        await source.capture_frame(frame)
        await asyncio.sleep(FRAME_DURATION / 1000)

    is_speaking = False


async def play_audio(source, text):
    if user_speaking:
        return

    audio_bytes = await text_to_speech(text)
    await stream_audio(source, audio_bytes)


# ================= SILENCE MONITOR =================

async def silence_monitor(source):
    global last_user_audio

    while True:
        await asyncio.sleep(5)

        if not is_speaking and time.time() - last_user_audio > 20:
            print("⏳ Silence detected")
            await play_audio(source, "Are you still there?")
            last_user_audio = time.time()


# ================= MAIN =================

async def main():
    global user_speaking, last_user_audio, audio_buffer

    room = rtc.Room()
    token = generate_token("voice-agent")

    await room.connect(LIVEKIT_URL, token)
    print("✅ Connected")

    source = rtc.AudioSource(SAMPLE_RATE, CHANNELS)
    track = rtc.LocalAudioTrack.create_audio_track("agent-audio", source)
    await room.local_participant.publish_track(track)

    @room.on("track_subscribed")
    def on_track(track, publication, participant):
        print("🎤 Subscribed to user audio")

        async def read_audio():
            global user_speaking, last_user_audio, audio_buffer

            async for frame in track:
                pcm = frame.data
                last_user_audio = time.time()

                if vad.is_speech(pcm, SAMPLE_RATE):
                    user_speaking = True
                    audio_buffer.extend(pcm)
                else:
                    if user_speaking:
                        user_speaking = False

                        if len(audio_buffer) > 0:
                            text = await speech_to_text(bytes(audio_buffer))
                            audio_buffer = bytearray()

                            if text.strip():
                                response = f"You said: {text}"
                                await play_audio(source, response)

        asyncio.create_task(read_audio())

    asyncio.create_task(silence_monitor(source))

    while True:
        await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(main())