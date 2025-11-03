import google.generativeai as genai


def _resolve_model_name(model_name: str) -> str:
    name = (model_name or "").strip()
    key = name.lower().replace("_", "-").replace(" ", "-")
    alias_map = {
        "gemini-2.0-flash": "gemini-2.0-flash",
        "gemini-20-flash": "gemini-2.0-flash",
        "gemini-2-0-flash": "gemini-2.0-flash",
        "gemini-2.0-flash-exp": "gemini-2.0-flash-exp",
        "gemini-2.0-flash-lite": "gemini-2.0-flash-lite",
        "gemini-1.5-flash": "gemini-1.5-flash",
        "gemini-1.5-pro": "gemini-1.5-pro",
        # Common display variants
        "gemini-2.0": "gemini-2.0-flash",
        "gemini-20": "gemini-2.0-flash",
        "gemini-2.0-flash-8b": "gemini-2.0-flash-8b",
    }
    # Direct mapping or return normalized key
    return alias_map.get(key, key)


def get_gemini_response(prompt: str, model_name: str = "gemini-2.0-flash") -> str:
    base = _resolve_model_name(model_name)
    candidate_models = [
        base,
        f"{base}-latest",
        f"{base}-001",
        # Sensible fallbacks
        "gemini-2.0-flash",
        "gemini-2.0-flash-exp",
        "gemini-1.5-flash",
        "gemini-1.5-pro",
    ]
    last_error = None
    for candidate in candidate_models:
        try:
            model = genai.GenerativeModel(candidate)
            response = model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            last_error = e
            continue
    return f"Error: {str(last_error)}"


