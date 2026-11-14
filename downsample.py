import subprocess
import sys
from pathlib import Path

SRC = Path("Generations")
DST = Path("Generations24k")
RATE = int(sys.argv[1]) if len(sys.argv) > 1 else 24000

for src in sorted(SRC.rglob("*.wav")):
    dst = DST / src.relative_to(SRC)
    dst.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error", "-i", str(src),
         "-ar", str(RATE), "-c:a", "pcm_s16le", str(dst)],
        check=True,
    )
    print(dst)
