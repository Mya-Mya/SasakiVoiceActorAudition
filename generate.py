import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).parent
IRODORI = ROOT / "vendor" / "Irodori-TTS-v4-light"
sys.path.insert(0, str(IRODORI))

from irodori_tts.inference_runtime import (  # noqa: E402
    InferenceRuntime,
    RuntimeKey,
    SamplingRequest,
    default_runtime_device,
    resolve_cfg_scales,
    save_wav,
)


def load_transcripts() -> list[str]:
    lines = (ROOT / "Transcripts.txt").read_text(encoding="utf-8").splitlines()
    texts = [re.sub(r"\s*（.*）\s*$", "", ln).strip() for ln in lines]
    return [t for t in texts if t]


def safe(name: str) -> str:
    return re.sub(r'[\\/:*?"<>|]', "_", name)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--checkpoint",
        required=True,
        help="Irodori TTS v4 light checkpoint safetensors",
    )
    ap.add_argument(
        "--codec-repo", required=True, help="Irodori TTS v4 light codec repository"
    )
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--character", default=None, help="Process only that character")
    args = ap.parse_args()

    refs = sorted((ROOT / "References").glob("*.wav"))
    if args.character:
        refs = [r for r in refs if r.stem.split(".", 1)[0] == args.character]
    texts = load_transcripts()

    dev = default_runtime_device()
    runtime = InferenceRuntime.from_key(
        RuntimeKey(
            checkpoint=args.checkpoint,
            model_device=dev,
            codec_repo=args.codec_repo,
            model_precision="fp32",
            codec_device=dev,
            codec_precision="fp32",
            codec_deterministic_encode=True,
            codec_deterministic_decode=True,
            compile_model=False,
            compile_dynamic=False,
            split_rare_tokens=True,
        )
    )
    cfg_t, cfg_c, cfg_s, _ = resolve_cfg_scales(
        cfg_guidance_mode="independent",
        cfg_scale_text=3.0,
        cfg_scale_caption=3.0,
        cfg_scale_speaker=5.0,
        cfg_scale=None,
        use_caption_condition=False,
        use_speaker_condition=bool(runtime.model_cfg.use_speaker_condition_resolved),
    )

    for ref in refs:
        character, source = ref.stem.split(".", 1)
        out_dir = ROOT / "Generations" / character
        out_dir.mkdir(parents=True, exist_ok=True)
        for text in texts:
            out = out_dir / f"{safe(text[:8])}.{source}.{args.seed}.wav"
            if out.exists():
                continue
            result = runtime.synthesize(
                SamplingRequest(
                    text=text,
                    ref_wav=str(ref),
                    ref_normalize_db=-16.0,
                    ref_ensure_max=True,
                    cfg_scale_text=cfg_t,
                    cfg_scale_caption=cfg_c,
                    cfg_scale_speaker=cfg_s,
                    cfg_guidance_mode="independent",
                    seed=args.seed,
                ),
                log_fn=None,
            )
            save_wav(out, result.audio, result.sample_rate)
            print(f"saved: {out}", flush=True)


if __name__ == "__main__":
    main()
