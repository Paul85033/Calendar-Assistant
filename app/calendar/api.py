import requests
from app.func.config import(
    GCA,
    PCI
)

def get_free_busy(access_token: str, time_min: str, time_max: str) -> list:
    url = f"{GCA}/freeBusy"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    body = {
        "timeMin": time_min,
        "timeMax": time_max,
        "items": [{"id": PCI}]
    }

    response = requests.post(url, headers=headers, json=body)
    response.raise_for_status()

    busy = response.json()["calendars"][PCI]["busy"]
    return busy

def create_event(access_token: str, event_data: dict) -> dict:
    url = f"{GCA}/calendars/{PCI}/events"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    response = requests.post(url, headers=headers, json=event_data)
    response.raise_for_status()

    return response.json()
