# Real-Time Voice Agent (LiveKit + OpenAI)

This project is a real-time conversational voice agent built using LiveKit and OpenAI APIs.

The agent listens to user speech, converts it to text (STT), generates a response, converts the response back to speech (TTS), and plays it in the LiveKit room.

It also includes interruption handling and silence detection logic.

---

## Features

- Real-time audio communication using LiveKit
- Speech-to-Text (OpenAI)
- Text-to-Speech (OpenAI)
- No speech overlap (agent stops if user interrupts)
- Silence detection (reminder after ~20 seconds)

---

## SDKs / Technologies Used

- Python 3.11
- LiveKit Agents SDK
- OpenAI API
- asyncio (for async handling)

---

## External Services

- LiveKit Cloud (room + real-time audio)
- OpenAI API (speech processing)

---

## Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/livekit-voice-agent.git
cd livekit-voice-agent
```

### 2. Create and activate virtual environment

```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

## Required Environment Variables

Create a `.env` file in the root directory:

```
LIVEKIT_URL=your_livekit_url
LIVEKIT_API_KEY=your_livekit_api_key
LIVEKIT_API_SECRET=your_livekit_api_secret
OPENAI_API_KEY=your_openai_api_key
```

---

## How to Run

First generate a token:

```bash
python generate_token.py
```

Then start the agent:

```bash
python main.py
```

Join the LiveKit room and start speaking.

---

## Known Limitations

- Depends on OpenAI API quota
- Requires stable internet connection
- No frontend UI (CLI-based agent)
- Basic conversational logic (can be extended further)

---

## Notes

This project was built as part of a real-time voice agent assignment.