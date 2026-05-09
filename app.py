import os
from functools import wraps

from anthropic import Anthropic
from dotenv import load_dotenv
from flask import Flask, abort, request
from twilio.request_validator import RequestValidator
from twilio.rest import Client
from werkzeug.middleware.proxy_fix import ProxyFix

load_dotenv()

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

twilio_client = Client(os.environ["TWILIO_ACCOUNT_SID"], os.environ["TWILIO_AUTH_TOKEN"])
anthropic_client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

TWILIO_WHATSAPP_NUMBER = os.environ["TWILIO_WHATSAPP_NUMBER"]

SYSTEM_PROMPT = (
    "You are a helpful, friendly assistant accessible via WhatsApp. "
    "Be concise since this is a messaging app."
)

# Per-sender conversation history: { "whatsapp:+1234567890": [{"role": ..., "content": ...}] }
conversation_history: dict[str, list[dict]] = {}


def require_twilio_signature(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        validator = RequestValidator(os.environ["TWILIO_AUTH_TOKEN"])
        signature = request.headers.get("X-Twilio-Signature", "")
        if not validator.validate(request.url, request.form, signature):
            abort(403)
        return f(*args, **kwargs)
    return decorated


@app.route("/webhook", methods=["POST"])
@require_twilio_signature
def webhook():
    sender = request.form.get("From", "").strip()
    body = request.form.get("Body", "").strip()

    if not sender or not body:
        return "", 400

    if body.lower() == "reset":
        conversation_history.pop(sender, None)
        _send(sender, "Conversation history cleared. Starting fresh!")
        return "", 200

    history = conversation_history.setdefault(sender, [])
    history.append({"role": "user", "content": body})

    try:
        response = anthropic_client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            messages=history,
        )
        reply = response.content[0].text
        history.append({"role": "assistant", "content": reply})
    except Exception:
        history.pop()  # don't record a turn we couldn't complete
        reply = "Sorry, I'm having trouble right now. Please try again in a moment."

    _send(sender, reply)
    return "", 200


def _send(to: str, body: str) -> None:
    twilio_client.messages.create(
        from_=TWILIO_WHATSAPP_NUMBER,
        to=to,
        body=body,
    )


if __name__ == "__main__":
    app.run(debug=True, port=5000)
