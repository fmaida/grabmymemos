from pathlib import Path
import textwrap
import grabmymemos as gmm


if __name__ == "__main__":

    # ––– Parametri globali –––
    gmm.config(base_url="https://memos.cesco.it",
               token=Path.home() / ".config" / "grabmymemos" / "memos.token")
    gmm.always_force_a_title()
    gmm.wrap_titles_at(length=30)
    
    list_of_memos = gmm.fetch_all()

    for memo in list_of_memos:
        date = memo["display_time"].strftime("%d/%m/%Y %H:%M")
        truncated = textwrap.shorten(memo["content"], width=60, placeholder="...")
        title = memo["title"] if memo["title"] else truncated
        print(f"ID: \"{memo['name']}\"")
        print(f"[{date}]  {title}")
        if memo["attachments"]:
            print("  contains:")
            for attachment in memo["attachments"]:
                print(f"    – {attachment}")
        else:
            print("  (no attachments)")
        if memo["image"]:
            print(f"  image:")
            print(f"    – {memo['image']}")
