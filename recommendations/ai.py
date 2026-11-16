"""AI job recommendations through OpenRouter (https://openrouter.ai).

Only the server calls the AI; the browser never sees the API key.

How it works:
1. We describe the user's profile and the current jobs (each with its id) to the model.
2. We ask for *structured output*: JSON shaped like {"recommendations": [{"job_id": 3, "reason": "..."}]}.
3. We check every answer against our own database: unknown job ids are dropped, duplicates are
   dropped, at most 5 are kept. So the AI can only ever point at jobs that really exist.

Any problem (no API key, network error, timeout, bad JSON) raises AIError, and the page shows a
friendly message instead of crashing. Tests replace `call_openrouter` with a fake: they never call the real AI.
"""

import json
import logging
import urllib.error
import urllib.request

from django.conf import settings

logger = logging.getLogger(__name__)

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
MAX_RECOMMENDATIONS = 5
MAX_JOBS_SENT = 100  # keeps the prompt (and the cost) small
MAX_REASON_LENGTH = 300

# JSON Schema the model's answer must follow (OpenRouter "structured outputs").
RESPONSE_SCHEMA = {
    "name": "job_recommendations",
    "strict": True,
    "schema": {
        "type": "object",
        "properties": {
            "recommendations": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "job_id": {"type": "integer", "description": "The id of a job from the list."},
                        "reason": {"type": "string", "description": "One sentence on why it fits this person."},
                    },
                    "required": ["job_id", "reason"],
                    "additionalProperties": False,
                },
            }
        },
        "required": ["recommendations"],
        "additionalProperties": False,
    },
}

SYSTEM_PROMPT = (
    "You help MBA students find startup and VC jobs. Given a job seeker's profile and a list of open jobs, "
    f"pick up to {MAX_RECOMMENDATIONS} jobs that fit the profile best, best fit first. For each, write one short "
    "sentence, addressed to the job seeker as 'you', explaining why it fits. Only use job ids from the list. "
    "If nothing fits, return an empty list."
)


class AIError(Exception):
    """The AI could not give us usable recommendations (not configured, unreachable, slow or nonsense)."""


def describe_profile(profile):
    return "\n".join(
        [
            f"Background: {profile.background or '(not given)'}",
            f"Skills: {profile.skills or '(not given)'}",
            f"Preferred role types: {', '.join(profile.role_type_labels()) or '(any)'}",
            f"Preferred locations: {profile.preferred_locations or '(any)'}",
            f"Preferred company stages: {', '.join(profile.stage_labels()) or '(any)'}",
        ]
    )


def describe_jobs(jobs):
    lines = []
    for job in jobs:
        stage = job.company.get_stage_display() or "unknown stage"
        lines.append(
            f"- id {job.id}: {job.title} at {job.company.name} ({stage}), {job.location}, "
            f"{job.get_role_type_display()}"
        )
    return "\n".join(lines)


def build_messages(profile, jobs):
    user_prompt = f"Job seeker profile:\n{describe_profile(profile)}\n\nOpen jobs:\n{describe_jobs(jobs)}"
    return [{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": user_prompt}]


def call_openrouter(messages):
    """Send the messages to OpenRouter and return the model's reply text. Raises AIError on any failure."""
    if not settings.OPENROUTER_API_KEY:
        raise AIError("OPENROUTER_API_KEY is not set")

    payload = {
        "model": settings.OPENROUTER_MODEL,
        "messages": messages,
        "response_format": {"type": "json_schema", "json_schema": RESPONSE_SCHEMA},
        "temperature": 0.2,
    }
    request = urllib.request.Request(
        OPENROUTER_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "X-Title": "Funky Lobsters job tracker",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=settings.OPENROUTER_TIMEOUT_SECONDS) as response:
            body = json.loads(response.read().decode("utf-8"))
        return body["choices"][0]["message"]["content"]
    except (urllib.error.URLError, TimeoutError, OSError, ValueError, KeyError, IndexError, TypeError) as error:
        # Log the kind of error, never the API key.
        logger.warning("OpenRouter call failed: %s", type(error).__name__)
        raise AIError("OpenRouter call failed") from error


def parse_recommendations(reply_text, jobs):
    """Turn the model's JSON reply into [(job, reason), ...], keeping only real, distinct jobs (max 5)."""
    try:
        data = json.loads(reply_text)
        items = data["recommendations"]
        if not isinstance(items, list):
            raise TypeError("recommendations is not a list")
    except (ValueError, KeyError, TypeError) as error:
        raise AIError("The AI reply was not in the expected format") from error

    jobs_by_id = {job.id: job for job in jobs}
    results, seen = [], set()
    for item in items:
        if not isinstance(item, dict):
            continue
        job = jobs_by_id.get(item.get("job_id"))
        reason = str(item.get("reason") or "").strip()[:MAX_REASON_LENGTH]
        if job is None or job.id in seen or not reason:
            continue  # the AI named a job we don't have, repeated one, or gave no reason
        seen.add(job.id)
        results.append((job, reason))
        if len(results) == MAX_RECOMMENDATIONS:
            break
    return results


def recommend_jobs(profile, jobs):
    """Ask the AI for up to 5 jobs that fit this profile. Returns [(job, reason), ...]; raises AIError."""
    jobs = list(jobs[:MAX_JOBS_SENT])
    if not jobs:
        return []
    reply_text = call_openrouter(build_messages(profile, jobs))
    return parse_recommendations(reply_text, jobs)
