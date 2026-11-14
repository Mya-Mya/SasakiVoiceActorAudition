import subprocess
from pathlib import Path

ROOT = Path(__file__).parent
RAW = ROOT / "ReferencesRaw"
OUT = ROOT / "References"


def main() -> None:
    OUT.mkdir(exist_ok=True)
    for mp4 in sorted(RAW.glob("*.mp4")):
        wav = OUT / f"{mp4.stem}.wav"
        if wav.exists():
            print(f"skip: {wav.name}")
            continue
        subprocess.run(
            ["ffmpeg", "-y", "-i", str(mp4), "-vn", "-ac", "1", "-ar", "48000", str(wav)],
            check=True,
        )
        print(f"saved: {wav.name}")


if __name__ == "__main__":
    main()
