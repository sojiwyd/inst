import hashlib
import hmac
import json
import logging
from typing import Any

from fastapi import FastAPI, Header, HTTPException, Query, Request
from fastapi.responses import JSONResponse, PlainTextResponse

from app.config import get_settings
from app.instagram import InstagramClient
from app.scenario import RESET_WORDS, SCENARIO_STEPS, TRIGGER_WORDS, next_step
from app.state import BotState

settings = get_settings()
logging.basicConfig(level=getattr(logging, settings.log_level.upper(), logging.INFO))
logger = logging.getLogger(__name__)

app = FastAPI(title=settings.app_name)
state = BotState(settings.database_url)
instagram = InstagramClient(settings)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/webhook")
def verify_webhook(
    hub_mode: str = Query(alias="hub.mode"),
    hub_verify_token: str = Query(alias="hub.verify_token"),
    hub_challenge: str = Query(alias="hub.challenge"),
):
    if hub_mode == "subscribe" and hub_verify_token == settings.verify_token:
        return PlainTextResponse(hub_challenge)
    raise HTTPException(status_code=403, detail="Invalid verify token")


@app.post("/webhook")
async def receive_webhook(
    request: Request,
    x_hub_signature_256: str | None = Header(default=None),
):
    raw_body = await request.body()

    if settings.meta_access_token and x_hub_signature_256:
        verify_signature(raw_body, x_hub_signature_256)

    payload = await request.json()
    logger.info("Webhook received: %s", json.dumps(payload, ensure_ascii=False)[:2000])

    for entry in payload.get("entry", []):
        for change in entry.get("changes", []):
            value = change.get("value", {})
            field = change.get("field")
            handle_change(field, value)

        for messaging_event in entry.get("messaging", []):
            handle_messaging_event(messaging_event)

    return JSONResponse({"ok": True})



def verify_signature(raw_body: bytes, signature_header: str) -> None:
    # Optional hardening: if you enable App Secret Proof / webhook signatures,
    # you can extend this to use APP_SECRET from env. Left as template.
    if not signature_header.startswith("sha256="):
        raise HTTPException(status_code=403, detail="Invalid signature header")



def handle_change(field: str | None, value: dict[str, Any]) -> None:
    if field not in {"comments", "feed"}:
        return

    comment_text = (value.get("text") or "").strip().lower()
    if comment_text not in {word.lower() for word in TRIGGER_WORDS}:
        return

    sender_id = value.get("from", {}).get("id") or value.get("user_id") or value.get("from_id")
    comment_id = value.get("id") or value.get("comment_id")
    event_id = f"comment:{comment_id}"

    if not sender_id or not comment_id:
        logger.warning("Comment event missing sender or comment id: %s", value)
        return

    if state.has_processed_event(event_id):
        return

    first = SCENARIO_STEPS[0]
    try:
        instagram.send_text_message(recipient_igid=sender_id, message_text=first.text)
        state.set_user_step(user_id=sender_id, step_index=0, last_comment_id=comment_id)
        state.mark_event_processed(event_id)
        logger.info("Sent first scenario message to %s", sender_id)
    except Exception:
        logger.exception("Failed to send first message")



def handle_messaging_event(event: dict[str, Any]) -> None:
    sender_id = event.get("sender", {}).get("id")
    message = event.get("message", {})
    text = (message.get("text") or "").strip()
    mid = message.get("mid")

    if not sender_id or not text or not mid:
        return

    event_id = f"message:{mid}"
    if state.has_processed_event(event_id):
        return

    lowered = text.lower()
    if lowered in RESET_WORDS:
        state.reset_user(sender_id)
        next_message = SCENARIO_STEPS[0]
        instagram.send_text_message(recipient_igid=sender_id, message_text=next_message.text)
        state.set_user_step(sender_id, 0)
        state.mark_event_processed(event_id)
        return

    current_step = state.get_user_step(sender_id)
    if current_step is None:
        state.mark_event_processed(event_id)
        return

    upcoming = next_step(current_step)
    if upcoming is None:
        closing = "Если хочешь, я потом могу собрать ещё отдельный блок про историю места, архитектуру и лоты 👀"
        instagram.send_text_message(recipient_igid=sender_id, message_text=closing)
        state.reset_user(sender_id)
        state.mark_event_processed(event_id)
        return

    next_index = current_step + 1
    instagram.send_text_message(recipient_igid=sender_id, message_text=upcoming.text)
    state.set_user_step(sender_id, next_index)
    state.mark_event_processed(event_id)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host=settings.app_host, port=settings.app_port, reload=True)
