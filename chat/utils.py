import requests
from django.conf import settings


SUPPORTED_LANGUAGES = {
    "en": "English",
    "lg": "Luganda",
    "xog": "Lusoga",
    "nyn": "Runyankole",
    "sw": "Swahili",
}


class TranslationUnavailable(RuntimeError):
    """Raised when translation cannot be attempted or the provider fails."""


def translate_message(text, target_language):
    """Translate text through Google Cloud Translation v2."""
    target = str(target_language or "").strip().lower()
    if target not in SUPPORTED_LANGUAGES:
        raise ValueError(f"Unsupported target language: {target_language}")

    api_key = getattr(settings, "GOOGLE_TRANSLATE_API_KEY", "")
    if not api_key:
        raise TranslationUnavailable("Google Translation is not configured.")

    response = requests.post(
        "https://translation.googleapis.com/language/translate/v2",
        headers={"X-goog-api-key": api_key},
        json={"q": str(text), "target": target, "format": "text"},
        timeout=10,
    )
    try:
        response.raise_for_status()
        return response.json()["data"]["translations"][0]["translatedText"]
    except (requests.RequestException, KeyError, IndexError, TypeError, ValueError) as exc:
        raise TranslationUnavailable("Translation provider request failed.") from exc
