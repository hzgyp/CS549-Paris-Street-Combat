"""Generate equal-text stock-voice auditions locally; never alter game audio."""
from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
from pathlib import Path
import subprocess
import sys
from datetime import datetime, timezone


TEXT = (
    "Welcome to Paris Street Combat. Lead an Allied squad across the bridge and "
    "secure the German-held bridgehead. This demonstration shows movement, "
    "collision, navigation, and enemy behavior. Save after clearing the guards, "
    "or restart the mission if the player is killed."
)
VOICES = (
    ("A_Michael_US_male", "am_michael", "en-us"),
    ("B_George_UK_male", "bm_george", "en-gb"),
    ("C_Emma_UK_female", "bf_emma", "en-gb"),
    ("D_Heart_US_female", "af_heart", "en-us"),
)


def identity(path: Path) -> dict:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return {"name": path.name, "bytes": path.stat().st_size, "sha256": h.hexdigest()}


def command(args: list[str], log: Path) -> subprocess.CompletedProcess:
    result = subprocess.run(args, capture_output=True, text=True, encoding="utf-8")
    log.write_text(result.stdout + result.stderr, encoding="utf-8")
    if result.returncode:
        raise RuntimeError(f"Command failed ({result.returncode}); see {log.name}")
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--work", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--ffmpeg", required=True, type=Path)
    parser.add_argument("--reuse-raw", type=Path)
    args = parser.parse_args()
    work = args.work.resolve()
    output = args.output.resolve()
    if output.exists():
        raise RuntimeError("Output identity already exists; do not overwrite auditions")
    output.mkdir(parents=True)
    sys.path.insert(0, str(work / "runtime"))
    import numpy as np
    import onnxruntime as ort
    import soundfile as sf
    from kokoro_onnx import Kokoro

    model = work / "models" / "kokoro-v1.0.onnx"
    voices = work / "models" / "voices-v1.0.bin"
    release = json.loads((work / "models" / "release-assets.json").read_text(encoding="utf-8-sig"))
    inputs = [identity(p) for p in (model, voices)]
    for expected in release:
        actual = next(row for row in inputs if row["name"] == expected["name"])
        if actual["bytes"] != expected["size"]:
            raise RuntimeError("Model release size mismatch")
        if expected.get("digest") and expected["digest"] != "sha256:" + actual["sha256"]:
            raise RuntimeError("Model release digest mismatch")
    options = ort.SessionOptions()
    options.intra_op_num_threads = 4
    options.inter_op_num_threads = 1
    session = ort.InferenceSession(str(model), sess_options=options, providers=["CPUExecutionProvider"])
    kokoro = Kokoro.from_session(session, str(voices))
    if not all(voice in kokoro.voices for _, voice, _ in VOICES):
        raise RuntimeError("Requested stock voice absent")
    output.joinpath("TEXT_EN.txt").write_text(TEXT + "\n", encoding="utf-8")
    if args.reuse_raw and (args.reuse_raw / "TEXT_EN.txt").read_text(encoding="utf-8") != TEXT + "\n":
        raise RuntimeError("Raw reuse has different audition text")
    rows = []
    for label, voice, lang in VOICES:
        retained = args.reuse_raw / f"{label}_RAW.wav" if args.reuse_raw else None
        if retained and retained.exists():
            samples, rate = sf.read(retained, dtype="float32")
        else:
            samples, rate = kokoro.create(TEXT, voice=voice, speed=1.0, lang=lang)
        samples = np.asarray(samples, dtype=np.float32).ravel()
        if rate != 24000 or len(samples) < 24000 or not np.isfinite(samples).all():
            raise RuntimeError(f"Invalid PCM: {label}")
        peak = float(np.max(np.abs(samples)))
        if peak < 0.001:
            raise RuntimeError(f"Silent PCM: {label}")
        raw = output / f"{label}_RAW.wav"
        sf.write(raw, samples, rate, subtype="FLOAT")
        first = command([
            str(args.ffmpeg), "-hide_banner", "-nostdin", "-i", str(raw),
            "-af", "loudnorm=I=-20:TP=-2:LRA=7:print_format=json", "-f", "null", "-",
        ], output / f"{label}_loudness_analysis.log")
        measurement, _ = json.JSONDecoder().raw_decode(first.stderr[first.stderr.rfind("{"):])
        norm = (
            "loudnorm=I=-20:TP=-2:LRA=7:linear=true:"
            f"measured_I={measurement['input_i']}:measured_TP={measurement['input_tp']}:"
            f"measured_LRA={measurement['input_lra']}:measured_thresh={measurement['input_thresh']}:"
            f"offset={measurement['target_offset']}:print_format=json"
        )
        mp3 = output / f"{label}.mp3"
        command([
            str(args.ffmpeg), "-hide_banner", "-nostdin", "-n", "-i", str(raw),
            "-af", norm, "-ar", "24000", "-ac", "1", "-c:a", "libmp3lame", "-b:a", "128k", str(mp3),
        ], output / f"{label}_encode.log")
        decoded = output / f"{label}_DECODED.wav"
        command([
            str(args.ffmpeg), "-hide_banner", "-nostdin", "-n", "-i", str(mp3),
            "-c:a", "pcm_f32le", str(decoded),
        ], output / f"{label}_decode.log")
        actual, actual_rate = sf.read(decoded, dtype="float32")
        if not np.isfinite(actual).all() or np.max(np.abs(actual)) >= 1.0:
            raise RuntimeError(f"Invalid/clipped delivered audio: {label}")
        rows.append({
            "id": label[0], "voice": voice, "language": lang, "speed": 1.0,
            "raw_duration_seconds": len(samples) / rate,
            "delivered_duration_seconds": len(actual) / actual_rate,
            "sample_rate": actual_rate, "raw_peak": peak,
            "delivered_peak": float(np.max(np.abs(actual))),
            "delivered_rms": float(np.sqrt(np.mean(np.square(actual)))),
            "loudness_target_lufs": -20, "full_decode_exit": 0,
            "retained_raw_reused": str(retained) if retained and retained.exists() else None,
            "mp3": identity(mp3), "raw": identity(raw), "decoded": identity(decoded),
        })
        print(json.dumps(rows[-1]), flush=True)
    receipt = {
        "status": "four_auditions_generated_technical_checks_pass_voice_selection_pending",
        "utc": datetime.now(timezone.utc).isoformat(), "text": TEXT,
        "text_sha256": identity(output / "TEXT_EN.txt")["sha256"],
        "generation": "local stock-voice AI narration, not captured game audio or voice cloning",
        "human_listening": "pending; assistant does not claim listening",
        "providers": session.get_providers(), "model_inputs": inputs, "release_assets": release,
        "packages": {name: importlib.metadata.version(name) for name in (
            "kokoro-onnx", "onnxruntime", "numpy", "phonemizer", "espeakng-loader", "soundfile")},
        "voices": rows,
    }
    output.joinpath("AUDITION_RESULT.json").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
