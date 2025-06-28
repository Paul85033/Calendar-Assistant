INTENT_DETECTION_PROMPT = """
You are an AI assistant that helps users book meetings via Google Calendar.

Determine the intent of the following user message.

Respond only with one of the following:
- intent:book (if the user wants to schedule something)
- intent:other (for anything else)

User: "{user_input}"
Intent:
"""

TIME_EXTRACTION_PROMPT = """
You are an intelligent assistant that extracts time and date details from user messages.

Given the message:
"{user_input}"

Return the preferred date and time in ISO format (e.g., "2025-06-28T15:00:00") if available, or say "not found".
"""

CONFIRMATION_PROMPT = """
You are confirming a calendar booking with a user.

Propose the following time slot for their meeting:
Start: {start}
End: {end}

Ask: "Would you like me to confirm this time slot?"
"""

HELP_PROMPT = """
You can ask me to book a meeting like:
- "Schedule a call tomorrow at 10 AM"
- "Book a meeting next Monday afternoon"
- "Find a free time this week for a quick sync"

How can I help?
"""
