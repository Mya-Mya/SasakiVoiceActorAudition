# SasakiVoiceActorAudition

A project ot find the voice quality of "Sasaki" from the "Haruhi Suzumiya" series using Irodori TTS.

## Setup

```
git clone --recurse-submodules <this-repo>
cd vendor/Irodori-TTS-v4-light
uv sync --extra cu134
```

Model weights of Irodori TTS are not included in the repository. Prepare the following:
- `model.safetensors` for Irodori-TTS-v4.1-Small (HF: Aratako/Irodori-TTS-v4.1-Small)
- Codec Semantic-DACVAE-Japanese-32dim (HF: Aratako/Semantic-DACVAE-Japanese-32dim)

## Usage

1. Place reference videos in `ReferencesRaw/{character}.{source}.mp4` (source is `yt-{id}` for the YouTube video or `ytshorts-{id}` for the YouTube Shorts.)。
2. Extract reference audio (ffmpeg required): `uv run python extract_refs.py`
3. Generate:
    ```
    uv run --no-sync --project vendor/Irodori-TTS-v4-light python generate.py \
      --checkpoint <model.safetensors> --codec-repo <codec> [--seed 0] [--character character]
    ```
    Reads each line from `Transcripts.txt` (excluding `(Source)` at the end of the line) and saves the output to `Generations/{character}/{transcript-short}.{source}.{seed}.wav`, where transcript-short is the first 8 characters of the transcript. Skips existing files.
