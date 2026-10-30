"""Validators — shared allowed-value constants used by app.py and Jinja templates."""

ALLOWED_DIRECTIONS = frozenset({
    "en-ig",  # English → Igede
    "ig-en",  # Igede → English
})

ALLOWED_CATEGORIES = frozenset({
    "greeting",
    "family",
    "food",
    "proverb",
    "culture",
    "everyday",
})

ALLOWED_SOURCE_TYPES = frozenset({
    "native_speaker",
    "elder",
    "book",
    "personal_knowledge",
})

CATEGORY_DISPLAY = {
    "greeting": "Greetings",
    "family": "Family & people",
    "food": "Food & farming",
    "proverb": "Proverbs & sayings",
    "culture": "Culture & ceremony",
    "everyday": "Everyday phrases",
}

SOURCE_TYPE_DISPLAY = {
    "native_speaker": "Native speaker",
    "elder": "Elder / community member",
    "book": "Book or document",
    "personal_knowledge": "Personal knowledge",
}

DIRECTION_DISPLAY = {
    "en-ig": "English → Igede",
    "ig-en": "Igede → English",
}
