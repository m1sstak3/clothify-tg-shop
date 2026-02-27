from locales.ru import TEXTS as RU_TEXTS
from locales.en import TEXTS as EN_TEXTS

LOCALES = {
    "ru": RU_TEXTS,
    "en": EN_TEXTS
}

def get_text(key: str, lang: str = "ru", **kwargs) -> str:
    """Получить текст по ключу для указанного языка."""
    texts = LOCALES.get(lang, RU_TEXTS)
    text = texts.get(key, key)
    if kwargs:
        return text.format(**kwargs)
    return text
