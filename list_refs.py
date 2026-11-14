import html
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).parent
REFS = ROOT / "References"
OUT = ROOT / "references.html"


def embed(source: str) -> str:
    kind, _, vid = source.partition("-")
    if kind not in ("yt", "ytshorts") or not vid:
        return f"<p>(不明なsource: {html.escape(source)})</p>"
    url = f"https://www.youtube.com/embed/{vid}"
    if kind == "ytshorts":
        w, h = 315, 560
    else:
        w, h = 560, 315
    return (
        f'<iframe width="{w}" height="{h}" src="{url}" loading="lazy" '
        f"allowfullscreen></iframe>"
    )


def main() -> None:
    chars = defaultdict(list)
    for wav in sorted(REFS.glob("*.wav")):
        name, _, source = wav.stem.partition(".")
        chars[name].append(source)

    parts = [
        '<!DOCTYPE html><html lang="ja"><head><meta charset="utf-8">'
        "<title>References</title></head><body>"
    ]
    for name in sorted(chars):
        parts.append(f"<h2>{html.escape(name)}</h2>")
        for source in chars[name]:
            parts.append(f"<h3>{html.escape(source)}</h3>{embed(source)}")
    parts.append("</body></html>")
    OUT.write_text("\n".join(parts), encoding="utf-8")
    print(
        f"saved: {OUT} ({sum(map(len, chars.values()))} refs, {len(chars)} characters)"
    )


if __name__ == "__main__":
    main()
