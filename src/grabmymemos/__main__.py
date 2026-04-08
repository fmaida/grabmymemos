from pathlib import Path
import textwrap
from grabmymemos import config, fetch_all


if __name__ == "__main__":

    # ––– Parametri globali –––
    config(base_url="https://memos.cesco.it",
           token=Path.home() / ".config" / "grabmymemos" / "memos.token")
    dati = fetch_all()

    for memo in dati:
        data = memo["display_time"].strftime("%d/%m/%Y %H:%M")
        troncato = textwrap.shorten(memo["content"], width=60, placeholder="...")
        titolo = memo["title"] if memo["title"] else troncato
        print(f"ID: \"{memo['name']}\"")
        print(f"[{data}]  {titolo}")
        if memo["attachments"]:
            print("  contiene:")
            for allegato in memo["attachments"]:
                print(f"    – {allegato}")
        else:
            print("  (senza allegati)")
        if memo["image"]:
            print(f"  image:")
            print(f"    – {memo['image']}")
