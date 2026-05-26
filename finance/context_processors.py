from .preferences import LANGUAGES, THEMES, get_language, get_text, get_theme


def ui_preferences(request):
    return {
        "UI": get_text(request),
        "current_language": get_language(request),
        "current_theme": get_theme(request),
        "available_languages": LANGUAGES,
        "available_themes": THEMES,
    }
