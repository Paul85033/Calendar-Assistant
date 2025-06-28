import openai
from datetime import datetime, timedelta, timezone
from app.calendar.api import get_free_busy, create_event
from app.agent.template import INTENT_DETECTION_PROMPT, TIME_EXTRACTION_PROMPT
from app.func.config import OPENAI_API_KEY

openai.api_key = OPENAI_API_KEY

def detect_intent(state: dict) -> dict:
    user_input = state.get("user_input", "")
    prompt = INTENT_DETECTION_PROMPT.format(user_input=user_input)

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0,
        )
        intent = response.choices[0].message.content.strip()
        state["intent"] = intent
    except Exception as e:
        state["intent"] = "intent:other"
        state["bot_reply"] = f"Failed to determine intent: {e}"

    return state

def extract_datetime(state: dict) -> dict:
    user_input = state.get("user_input", "")
    prompt = TIME_EXTRACTION_PROMPT.format(user_input=user_input)

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "AI that extracts datetime info in ISO format."},
                {"role": "user", "content": prompt}
            ],
            temperature=0,
        )
        result = response.choices[0].message.content.strip()

        if result.lower() != "not found" and "T" in result:
            state["requested_datetime"] = result
        else:
            state["requested_datetime"] = None
            state["bot_reply"] = "Please specify when you would like the meeting!"

    except Exception as e:
        state["requested_datetime"] = None
        state["bot_reply"] = f"Failed to extract datetime: {e}"

    return state

def check_availability(state: dict) -> dict:
    access_token = state.get("access_token")
    requested = state.get("requested_datetime")

    if requested:
        start = datetime.fromisoformat(requested.replace("Z", ""))
        end = start + timedelta(hours=1)
    else:
        start = datetime.now(timezone.utc)
        end = start + timedelta(days=3)

    now = start.isoformat() + 'Z'
    later = end.isoformat() + 'Z'

    try:
        busy_slots = get_free_busy(access_token, now, later)
        state["busy_slots"] = busy_slots
    except Exception as e:
        state["bot_reply"] = f"Failed to fetch calendar !: {e}"

    return state

def suggest_slots(state: dict) -> dict:
    busy = state.get("busy_slots", [])
    suggestions = []

    base_time = datetime.now(timezone.utc).replace(hour=10, minute=0, second=0, microsecond=0)

    for i in range(6):
        start = base_time + timedelta(hours=i)
        end = start + timedelta(minutes=30)

        conflict = False
        for b in busy:
            busy_start = datetime.fromisoformat(b["start"].replace("Z", "+00:00"))
            busy_end = datetime.fromisoformat(b["end"].replace("Z", "+00:00"))
            if start < busy_end and end > busy_start:
                conflict = True
                break

        if not conflict:
            suggestions.append({
                "start": start.isoformat().replace("+00:00", "Z"),
                "end": end.isoformat().replace("+00:00", "Z")
            })

        if len(suggestions) == 3:
            break

    if not suggestions:
        state["bot_reply"] = "No available time slots found. Please try another time."
    else:
        state["suggested_slots"] = suggestions
        slots_str = "\n".join([f"{s['start']} to {s['end']}" for s in suggestions])
        state["bot_reply"] = f"Available slots:\n{slots_str}"

    print("Suggested free slots:", suggestions)
    return state

def confirm_booking(state: dict) -> dict:
    access_token = state.get("access_token")
    suggested_slots = state.get("suggested_slots", [])

    if not suggested_slots:
        state["bot_reply"] = "No available time slots to book.Provide a specific time."
        return state

    slot = suggested_slots[0]

    if not slot.get("start") or not slot.get("end"):
        state["bot_reply"] = "Incomplete slot information. Cannot proceed with booking."
        return state

    user_input = state.get("user_input", "")

    event = {
        "summary": "Meeting with user",
        "start": {"dateTime": slot["start"], "timeZone": "UTC"},
        "end": {"dateTime": slot["end"], "timeZone": "UTC"},
        "description": f"Booked via AI: {user_input}",
    }

    try:
        created = create_event(access_token, event)
        link = created.get("htmlLink", "")
        if link:
            state["bot_reply"] = f"Your meeting has been booked.)"
        else:
            state["bot_reply"] = "Meeting booked, but no calendar link returned."
    except Exception as e:
        state["bot_reply"] = f"Failed to book meeting: {e}"

    return state


nodes = {
    "intent": detect_intent,
    "extract_datetime": extract_datetime,
    "check_calendar": check_availability,
    "suggest_slots": suggest_slots,
    "confirm_booking": confirm_booking
}

