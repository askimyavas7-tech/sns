import os
from typing import Dict
import yaml

# Varsayılan dili zorla TR yap
DEFAULT_LANG = "tr"

languages: Dict[str, dict] = {}
languages_present: Dict[str, str] = {}

# Myanmar dili tamamen kapalı
DISABLED_LANGS = {"my", "mm"}


def load_yaml(path: str):
    with open(path, encoding="utf8") as f:
        return yaml.safe_load(f) or {}


def get_string(lang: str):
    """
    Dil alma sistemi:
    - my/mm gelirse tr
    - geçersiz dil gelirse tr
    - tr yoksa en
    """
    code = (lang or "").strip().lower()

    if code in DISABLED_LANGS:
        code = "tr"

    if code not in languages:
        code = "tr"

    if code not in languages:
        code = "en"

    return languages.get(code, languages.get("en", {}))


LANG_DIR = "./strings/langs/"

# EN zorunlu
en_path = os.path.join(LANG_DIR, "en.yml")
if not os.path.exists(en_path):
    raise FileNotFoundError("strings/langs/en.yml bulunamadı!")

languages["en"] = load_yaml(en_path)
languages_present["en"] = languages["en"].get("name", "English")

# Diğer dilleri yükle
for filename in os.listdir(LANG_DIR):
    if not filename.endswith(".yml"):
        continue

    language_code = filename[:-4].lower()

    if language_code in {"en"}:
        continue

    if language_code in DISABLED_LANGS:
        continue

    file_path = os.path.join(LANG_DIR, filename)
    data = load_yaml(file_path)

    # EN'deki eksik key'leri doldur
    for k, v in languages["en"].items():
        if k not in data:
            data[k] = v

    languages[language_code] = data
    languages_present[language_code] = data.get("name", language_code)


# LOGGERS Myanmar linkini tamamen kaldır
LOGGERS = None
