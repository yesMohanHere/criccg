from __future__ import annotations
import json
import subprocess
import time
from pathlib import Path
from typing import Iterable

import requests
from moviepy import VideoFileClip
import whisper

import config


def extract_audio(video_path: Path = config.VIDEO_PATH, audio_path: Path = config.AUDIO_PATH) -> Path:
    """Extract audio from *video_path* and write to *audio_path*."""
    clip = VideoFileClip(str(video_path))
    clip.audio.write_audiofile(str(audio_path))
    return audio_path


def transcribe_audio(audio_path: Path = config.AUDIO_PATH, output_path: Path = config.CLEAN_TRANSCRIPT) -> Path:
    """Transcribe audio using whisper and save minimal JSON."""
    model = whisper.load_model("base")
    result = model.transcribe(str(audio_path))
    minimal = [
        {
            "start": round(seg["start"], 2),
            "end": round(seg["end"], 2),
            "text": seg["text"].strip(),
        }
        for seg in result["segments"]
    ]
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(minimal, f, indent=4, ensure_ascii=False)
    return output_path


def classify_transcript(
    transcript_path: Path = config.CLEAN_TRANSCRIPT,
    output_path: Path = config.LABELED_TRANSCRIPT,
    model: str = config.OLLAMA_MODEL,
    url: str = config.OLLAMA_URL,
    labels: Iterable[str] | None = None,
) -> Path:
    """Label each transcript entry via Ollama."""
    if labels is None:
        labels = [
            "SIX",
            "FOUR",
            "WICKET",
            "LBW",
            "RUN OUT",
            "WIDE",
            "NO BALL",
            "FREE HIT",
            "EXTRA",
            "DOT BALL",
            "SINGLE",
            "DOUBLE",
            "THREE",
            "BREAK",
            "STRATEGY BREAK",
            "COMMENTARY",
            "SCORE UPDATE",
            "UNKNOWN",
            "APPEAL",
            "MISS",
            "EDGE",
            "REVIEW",
            "FIELDING EFFORT",
            "DROPPED CATCH",
            "BALL CONTACT",
            "MILESTONE",
            "BOWLING CHANGE",
            "CAPTAINCY DECISION",
            "INJURY",
            "PLAYER INTRO",
            "WEATHER INTERRUPTION",
        ]

    with open(transcript_path, "r", encoding="utf-8") as f:
        transcript = json.load(f)

    labeled = []
    for i, item in enumerate(transcript):
        text = item["text"]
        prompt = (
            "You are a cricket commentary classification assistant.\n\n"
            "Label the following cricket commentary into one word from this list:\n"
            f"{labels}.\n"
            "Only reply with one of the labels exactly as it appears in the list.\n\n"
            f"Commentary: \"{text}\""
        )
        try:
            resp = requests.post(
                url,
                json={"model": model, "prompt": prompt, "stream": False},
            )
            raw_label = resp.json()["response"].strip().upper()
            label = next((l for l in labels if l in raw_label.split()), "UNKNOWN")
        except Exception:
            label = "UNKNOWN"
        labeled.append({
            "start": item.get("start"),
            "end": item.get("end"),
            "text": text,
            "label": label,
        })
        time.sleep(1)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(labeled, f, indent=4, ensure_ascii=False)
    return output_path


def clip_segments(
    video_path: Path = config.VIDEO_PATH,
    labels_json: Path = config.LABELED_TRANSCRIPT,
    label: str | None = None,
    output_dir: Path = config.CLIPS_DIR,
    output_merged: Path = config.OUTPUT_VIDEO,
    ffmpeg_path: str = config.FFMPEG_PATH,
) -> Path:
    """Trim and merge segments from *video_path* according to *labels_json*."""
    with open(labels_json, "r", encoding="utf-8") as f:
        transcript = json.load(f)
    if label is None:
        label = input("\ud83d\udd0d Enter label to extract (e.g., SIX): ").strip().upper()
    segments = [t for t in transcript if t["label"] == label]
    print(f"\u2702\ufe0f Found {len(segments)} segments for label: {label}")

    output_dir.mkdir(parents=True, exist_ok=True)
    trimmed_files = []
    for i, seg in enumerate(segments):
        start = float(seg["start"])
        duration = float(seg["end"]) - start
        clip_path = output_dir / f"clip_{i:03d}.mp4"
        trimmed_files.append(clip_path)
        cmd = [
            ffmpeg_path,
            "-y",
            "-i",
            str(video_path),
            "-ss",
            str(start),
            "-t",
            str(duration),
            "-c",
            "copy",
            str(clip_path),
        ]
        try:
            subprocess.run(cmd, check=True)
            print(f"\u2705 Trimmed: {clip_path}")
        except subprocess.CalledProcessError:
            print(f"\u274c Failed: {clip_path}")

    list_path = output_dir / "merge_list.txt"
    with open(list_path, "w", encoding="utf-8") as f:
        for clip in trimmed_files:
            f.write(f"file '{clip}'\n")

    merge_cmd = [
        ffmpeg_path,
        "-y",
        "-f",
        "concat",
        "-safe",
        "0",
        "-i",
        str(list_path),
        "-c",
        "copy",
        str(output_merged),
    ]
    try:
        subprocess.run(merge_cmd, check=True)
        print(f"\n\ud83c\udf9c\ufe0f Merged video saved to: {output_merged}")
    except subprocess.CalledProcessError:
        print("\u274c Failed to merge clips.")
    return output_merged


def tsv_to_csv(tsv_path: Path = config.TSV_PATH, csv_path: Path = config.CSV_PATH) -> Path:
    """Convert TSV file to CSV."""
    import csv

    with open(tsv_path, "r", encoding="utf-8") as tsvfile:
        reader = csv.reader(tsvfile, delimiter="\t")
        rows = list(reader)

    with open(csv_path, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(rows)

    print("Saved as CSV:", csv_path)
    return csv_path


def labels_to_csv(json_path: Path = config.LABELED_TRANSCRIPT, csv_path: Path = config.CSV_PATH) -> Path:
    """Convert a labeled transcript JSON to CSV."""
    import csv

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    with open(csv_path, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=["start", "end", "text", "label"])
        writer.writeheader()
        for item in data:
            writer.writerow(item)

    print("\u2705 CSV saved to:", csv_path)
    return csv_path
