import re
from collections import defaultdict
from pathlib import Path
from urllib.parse import quote

from jinja2 import Environment, select_autoescape

ROOT = Path(__file__).parent
GENS = ROOT / "Generations24k"
OUT_DIR = ROOT / "local"
OUT_DIR.mkdir(exist_ok=True)

OUT_REF = OUT_DIR / "by_reference.html"
OUT_TEXT = OUT_DIR / "by_text.html"

env = Environment(autoescape=select_autoescape(default=True))

BASE = """<!DOCTYPE html><html lang="ja"><head><meta charset="utf-8">
<title>{{ title }}</title>
<style>audio{vertical-align:middle;height:32px} li{margin:.3em 0}</style></head><body>
<h1>{{ title }}</h1>
<p><a href="by_reference.html">参照音声別</a> | <a href="by_text.html">読み上げテキスト別</a></p>
{% block body %}{% endblock %}
</body></html>"""

T_REF = env.from_string(BASE.replace("{% block body %}{% endblock %}", """
{% for name, sources in data.items() %}
<h2>{{ name }}</h2>
{% for src, items in sources.items() %}
<h3><a href="{{ src_url(src) }}" target="_blank">{{ src }}</a></h3>
<ul>{% for it in items %}
<li><audio controls preload="none" src="{{ it.path }}"></audio> {{ it.text }} {% if it.seed != "0" %} (seed {{ it.seed }}){% endif %}</li>
{% endfor %}</ul>
{% endfor %}
{% endfor %}"""))

T_TEXT = env.from_string(BASE.replace("{% block body %}{% endblock %}", """
{% for text, items in data.items() %}
<h2>{{ text }}</h2>
<ul>{% for it in items %}
<li><audio controls preload="none" src="{{ it.path }}"></audio> {{ it.name }} (<a href="{{ src_url(it.source) }}" target="_blank">{{ it.source }}</a>)
{% if it.seed != "0" %} (seed {{ it.seed }}){% endif %}</li>
{% endfor %}</ul>
{% endfor %}"""))


def src_url(source: str) -> str:
    kind, _, vid = source.partition("-")
    if kind == "yt":
        return f"https://www.youtube.com/watch?v={vid}"
    if kind == "ytshorts":
        return f"https://www.youtube.com/shorts/{vid}"
    return "#"


def load_transcripts() -> dict[str, str]:
    """transcript-part(先頭8文字) -> 全文"""
    lines = (ROOT / "Transcripts.txt").read_text(encoding="utf-8").splitlines()
    texts = [re.sub(r"\s*（.*）\s*$", "", ln).strip() for ln in lines]
    return {re.sub(r'[\/:*?"<>|]', "_", t[:8]): t for t in texts if t}


def main() -> None:
    full = load_transcripts()
    order = {p: i for i, p in enumerate(full)}
    recs = []
    for wav in GENS.glob("*/*.wav"):
        part, source, seed = wav.stem.rsplit(".", 2)
        recs.append(
            dict(
                name=wav.parent.name,
                source=source,
                seed=seed,
                part=part,
                text=full.get(part, part)[:20],
                path=quote(wav.relative_to(ROOT).as_posix()),
            )
        )
    recs.sort(key=lambda r: (r["name"], r["source"], order.get(r["part"], 999), r["seed"]))

    by_ref = defaultdict(lambda: defaultdict(list))
    by_text = defaultdict(list)
    for r in recs:
        by_ref[r["name"]][r["source"]].append(r)
    for r in sorted(recs, key=lambda r: (order.get(r["part"], 999), r["name"], r["source"], r["seed"])):
        by_text[r["text"]].append(r)

    OUT_REF.write_text(
        T_REF.render(title="参照音声別", data=by_ref, src_url=src_url), encoding="utf-8"
    )
    OUT_TEXT.write_text(
        T_TEXT.render(title="読み上げテキスト別", data=by_text, src_url=src_url),
        encoding="utf-8",
    )
    print(f"saved: {OUT_REF}, {OUT_TEXT} ({len(recs)} wavs)")


if __name__ == "__main__":
    main()
