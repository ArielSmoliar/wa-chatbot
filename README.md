# WhatsApp Chatbot

A WhatsApp bot built with Python, Flask, Twilio, and Claude (claude-sonnet-4-6).

## How it works

Twilio receives WhatsApp messages and forwards them to your Flask webhook. The bot maintains per-conversation history in memory, sends it to Claude, and replies via Twilio.

---

## Setup

### 1. Clone and install dependencies

```bash
git clone https://github.com/ArielSmoliar/wa-chatbot.git
cd wa-chatbot
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure environment variables

```bash
cp .env.example .env
```

Fill in `.env`:

| Variable | Where to find it |
|---|---|
| `TWILIO_ACCOUNT_SID` | [Twilio Console](https://console.twilio.com) → Account Info |
| `TWILIO_AUTH_TOKEN` | [Twilio Console](https://console.twilio.com) → Account Info |
| `TWILIO_WHATSAPP_NUMBER` | `whatsapp:+14155238886` (sandbox default) |
| `ANTHROPIC_API_KEY` | [console.anthropic.com](https://console.anthropic.com) |

### 3. Join the Twilio WhatsApp Sandbox

From your WhatsApp, send the following message to **+1 415 523 8886**:

```
join whistle-frame
```

You'll receive a confirmation that you've joined the sandbox.

### 4. Run the Flask app

```bash
python app.py
```

The server starts on `http://localhost:5000`.

### 5. Expose it with ngrok

In a separate terminal:

```bash
ngrok http 5000
```

Copy the **Forwarding** HTTPS URL, e.g. `https://abc123.ngrok.io`.

### 6. Configure the Twilio Sandbox webhook

1. Go to [Twilio Console → Messaging → Try it out → Send a WhatsApp message](https://console.twilio.com/us1/develop/sms/try-it-out/whatsapp-learn)
2. Under **Sandbox settings**, paste your ngrok URL into the **"When a message comes in"** field:
   ```
   https://abc123.ngrok.io/webhook
   ```
3. Set the method to **HTTP POST** and save.

---

## Usage

| Send | Bot does |
|---|---|
| Any message | Replies using Claude with full conversation context |
| `reset` | Clears your conversation history and starts fresh |

---

## Notes

- Conversation history is stored **in memory** and resets when the server restarts.
- The Twilio sandbox requires each user to join before they can exchange messages.
- For production use, replace in-memory history with a persistent store (Redis, Postgres, etc.) and deploy to a public server instead of ngrok.

---

## License

MIT License. See [LICENSE](LICENSE) for details.
