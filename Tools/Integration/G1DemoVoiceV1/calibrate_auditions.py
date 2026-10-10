"""Apply measured attenuation only, retaining original synthesis and prior files."""
import argparse
import json
from pathlib import Path
import subprocess
import hashlib


def stats(text):
    return json.JSONDecoder().raw_decode(text[text.rfind("{"):])[0]


def run(command, log):
    result = subprocess.run(command, capture_output=True, text=True, encoding="utf-8")
    log.write_text(result.stdout + result.stderr, encoding="utf-8")
    if result.returncode:
        raise RuntimeError(f"Export/analysis failed: {log.name}")
    return result


parser = argparse.ArgumentParser()
parser.add_argument("--source", type=Path, required=True)
parser.add_argument("--output", type=Path, required=True)
parser.add_argument("--ffmpeg", required=True)
args = parser.parse_args()
if args.output.exists():
    raise RuntimeError("Do not overwrite an output identity")
args.output.mkdir(parents=True)
original = json.loads((args.source / "AUDITION_RESULT.json").read_text(encoding="utf-8"))
rows = []
for row in original["voices"]:
    name = Path(row["mp3"]["name"]).stem
    initial = stats((args.source / f"{name}_loudness_analysis.log").read_text(encoding="utf-8"))
    delivered = stats((args.source / f"{row['id']}_delivered_loudness.log").read_text(encoding="utf-8"))
    gain = -21 - float(delivered["input_i"])
    if gain > 0:
        raise RuntimeError("Calibration may only attenuate, never boost a peak")
    norm = (
        "loudnorm=I=-20:TP=-2:LRA=7:linear=true:"
        f"measured_I={initial['input_i']}:measured_TP={initial['input_tp']}:"
        f"measured_LRA={initial['input_lra']}:measured_thresh={initial['input_thresh']}:"
        f"offset={initial['target_offset']},volume={gain:.4f}dB"
    )
    output = args.output / row["mp3"]["name"]
    run([args.ffmpeg, "-hide_banner", "-nostdin", "-n", "-i", str(args.source / row["raw"]["name"]),
         "-af", norm, "-ar", "24000", "-ac", "1", "-c:a", "libmp3lame", "-b:a", "128k", str(output)],
        args.output / f"{name}_export.log")
    analysis = run([args.ffmpeg, "-hide_banner", "-nostdin", "-i", str(output),
                    "-af", "loudnorm=I=-21:TP=-2:LRA=7:print_format=json", "-f", "null", "-"],
                   args.output / f"{name}_verify.log")
    actual = stats(analysis.stderr)
    if abs(float(actual["input_i"]) + 21) > .2 or float(actual["input_tp"]) >= 0:
        raise RuntimeError(f"Delivered loudness/peak failed: {name}")
    rows.append({"id": row["id"], "voice": row["voice"], "language": row["language"],
                 "duration_seconds": row["delivered_duration_seconds"], "file": output.name,
                 "sha256": hashlib.sha256(output.read_bytes()).hexdigest(), "bytes": output.stat().st_size,
                 "additional_gain_db": gain, "measured_lufs": float(actual["input_i"]),
                 "true_peak_db": float(actual["input_tp"]), "full_decode_exit": 0,
                 "original_raw": row["raw"], "original_voice_speed": row["speed"]})
result = {"status": "four_final_auditions_technical_pass_human_selection_pending", "text": original["text"],
          "loudness_target_lufs": -21, "loudness_tolerance_db": .2,
          "source_receipt": str(args.source / "AUDITION_RESULT.json"),
          "scope": "measured attenuation only, original raw synthesis reused without lossy input re-encoding",
          "voices": rows}
(args.output / "AUDITION_RESULT.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
(args.output / "TEXT_EN.txt").write_text(original["text"] + "\n", encoding="utf-8")
print(json.dumps(result, indent=2))
