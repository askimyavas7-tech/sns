import os
from typing import Dict

import yaml

DEFAULT_LANG = os.getenv("DEFAULT_LANG", "tr").lower()

languages: Dict[str, dict] = {}
languages_present: Dict[str, str] = {}

# İstemediğin dilleri burada kapat (my = Myanmar)
DISABLED_LANGS = {"my", "mm"}


def get_string(lang: str):
    """
    - my/mm gibi istemediğin dil gelirse TR'ye düş
    - lang yoksa TR
    - TR yoksa EN
    """
    code = (lang or "").strip().lower()

    if code in DISABLED_LANGS:
        code = "tr"

    if code not in languages:
        # Önce DEFAULT_LANG (tr), yoksa en
        code = DEFAULT_LANG if DEFAULT_LANG in languages else "en"

    return languages[code]


LANG_DIR = "./strings/langs/"

# EN mutlaka yüklensin
en_path = os.path.join(LANG_DIR, "en.yml")
if os.path.exists(en_path):
    languages["en"] = yaml.safe_load(open(en_path, encoding="utf8"))
    languages_present["en"] = languages["en"].get("name", "English")
else:
    raise FileNotFoundError("strings/langs/en.yml bulunamadı!")

# Diğer dilleri yükle (disabled olanları yükleme)
for filename in os.listdir(LANG_DIR):
    if not filename.endswith(".yml"):
        continue

    language_code = filename[:-4].lower()  # tr.yml -> tr
    if language_code == "en":
        continue
    if language_code in DISABLED_LANGS:
        continue  # my.yml vs tamamen devre dışı

    data = yaml.safe_load(open(os.path.join(LANG_DIR, filename), encoding="utf8"))

    # EN'deki eksik key'leri doldur
    for k in languages["en"]:
        if k not in data:
            data[k] = languages["en"][k]

    # name yoksa hata basıp çıkma; sadece dosyayı yine de ekle
    languages[language_code] = data
    languages_present[language_code] = data.get("name", language_code)


LOGGERS = "Nhoe_Kyaite_Kaung_Layy_Robot"
