# v0.1.3 – 12/04/2026

from pathlib import Path
import datetime
import textwrap
import re

from grabmymemos.config import ConfigClass

# _____________________________________________________________________________

_CONFIG = None

def config(base_url: str, token: str|Path) -> None:
    global _CONFIG
    _CONFIG = ConfigClass(base_url=base_url, token=token)

# _____________________________________________________________________________

def get_config() -> ConfigClass:
    global _CONFIG
    if _CONFIG is None:
        raise RuntimeError("Please call grabmymemos.config() before using the library")

    assert isinstance(_CONFIG, ConfigClass)  # Così PyCharm non rompe le palle
    return _CONFIG

# _____________________________________________________________________________

def always_force_a_title() -> None:
    _CONFIG.force_a_title = True

# _____________________________________________________________________________

def wrap_titles_at(length: int) -> None:
    _CONFIG.wrap_titles_at = length

# _____________________________________________________________________________

def _extract_title(content) -> str|None:
    first_line = content.split("\n")[0].strip()
    if first_line.startswith("#"):
        return first_line.lstrip("#").strip()
    return None

# _____________________________________________________________________________

def _extract_tags(content: str) -> list[str]:
    tags = re.findall(r'#([\w-]+)', content)
    return tags

# _____________________________________________________________________________

def _convert_date(stringa) -> datetime.datetime:
    return datetime.datetime.strptime(stringa, "%Y-%m-%dT%H:%M:%SZ")

# _____________________________________________________________________________

def _get_attachments(memo) -> tuple[list[dict], str|None]:
    """
    Restituisce una lista di stringhe contenenti gli URL
    agli allegati di una singola nota
    """

    config = get_config()

    attachments_list = []
    cover_image = None
    for attachment in memo["attachments"]:
        url = f"{config.base_url}/file/{attachment['name']}/{attachment['filename']}"
        attachments_list.append(url)
        if attachment["type"].lower() in ["image/jpeg", "image/png", "image/gif",
                                          "image/webp", "image/avif", "image/svg+xml"]:
            if not cover_image:
                # Non c'era un immagine di copertina prima. La assegna
                cover_image = url
            else:
                # Era già stata scelta un'immagine di copertina
                # Se l'utente ci tiene a fare un override della
                # copertina, aggiunge la sottostringa "thumb_"
                # all'inizio del nome file, e il programma lo
                # accontenta.
                if attachment['filename'].startswith("thumb_"):
                    cover_image = url

    return attachments_list, cover_image

# _____________________________________________________________________________

def reset() -> None:
    config = get_config()
    config.last_fetched_page = None

# _____________________________________________________________________________

def fetch(limit: int = 6, tags: list[str] = None) -> list[dict]:
    """
    Elenca tutte le note di un server Memos
    """

    config = get_config()

    output = []
    # Da qui in poi tutte le chiamate includono automaticamente il token
    params = {"pageSize": limit, "filter": "visibility == 'PUBLIC'"}
    # Se sono stati passati dei tag specifici per la ricerca
    if tags:
        temp = " || ".join(f'"{tag}" in tags' for tag in tags)
        params["filter"] += f" && ({temp})"
    if config.last_fetched_page is not None:
        params["pageToken"] = config.last_fetched_page
    response = config.session.get(f"{config.base_url}/api/v1/memos",
                                  params=params)
    if response.status_code == 200:
        dati = response.json()
        for memo in dati["memos"]:
            attachments, image = _get_attachments(memo)
            temp = {}
            temp["name"] = memo["name"].split("/")[-1]
            temp["display_time"] = _convert_date(memo["displayTime"])
            temp["create_time"] = _convert_date(memo["createTime"])
            temp["update_time"] = _convert_date(memo["updateTime"])
            temp["title"] = _extract_title(memo["content"])
            if config.force_a_title and not temp["title"]:
                temp_width = 160 if config.wrap_titles_at < 1 else config.wrap_titles_at
                temp["title"] = textwrap.shorten(memo["content"], width=temp_width, placeholder="..")
            if config.wrap_titles_at > 0 and temp["title"]:
                temp["title"] = textwrap.shorten(temp["title"], width=config.wrap_titles_at, placeholder="..")
            temp["content"] = memo["content"]
            temp["attachments"] = attachments
            temp["image"] = image
            temp["tags"] = _extract_tags(memo["content"])
            temp["url"] = f"{config.base_url}/{memo['name']}"
            output.append(temp)

        # Riordina i memo in ordine cronologico inverso
        output.sort(key=lambda x: x["display_time"], reverse=True)

        config.last_fetched_page = dati["nextPageToken"]

        return output
    else:
        raise RuntimeError(f"Error from server: {response.status_code}")

# _____________________________________________________________________________

def fetch_all(tags: list[str] = None) -> list[dict]:
    reset()
    output = []
    while True:
        chunk = fetch(limit=20, tags=tags)
        output += chunk
        if not get_config().last_fetched_page:
            break
    return output