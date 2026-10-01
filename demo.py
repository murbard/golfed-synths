"""Render a few short demos to WAV. numpy + stdlib only.

    python demo.py            # writes piano_scale.wav, piano_chords.wav, oboe_scale.wav
"""
import wave
import numpy as np
from piano import synth
from oboe import oboe_synth, reverb

SR = 44100


def write(path, x):
    x = np.asarray(x, float)
    x = 0.9 * x / (np.abs(x).max() + 1e-9)
    with wave.open(path, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((x * 32767).astype("<i2").tobytes())
    print("wrote", path)


def place(events, total):
    """events: list of (start_sec, mono array) -> mixed buffer."""
    out = np.zeros(int(total * SR))
    for t0, x in events:
        i = int(t0 * SR); n = min(len(x), len(out) - i)
        out[i:i + n] += x[:n]
    return out


C_MAJOR = [60, 62, 64, 65, 67, 69, 71, 72]

# Piano: C major scale at mf, then a quiet-to-loud chord progression.
write("piano_scale.wav",
      place([(0.45 * i, synth(m, 70, 2)) for i, m in enumerate(C_MAJOR)], 0.45 * 8 + 2))

chords = [([48, 60, 64, 67], 45), ([45, 60, 64, 69], 60), ([41, 57, 60, 65], 80), ([43, 55, 62, 71], 100),
          ([36, 55, 64, 72], 110)]
write("piano_chords.wav",
      place([(1.2 * i, sum(synth(m, v, 3) for m in ns)) for i, (ns, v) in enumerate(chords)], 1.2 * 5 + 3))

# Oboe: same scale, legato-ish, light room.
write("oboe_scale.wav",
      reverb(place([(0.5 * i, oboe_synth(m, dur=0.55, attack=0.03, release=0.06)) for i, m in enumerate(C_MAJOR)],
                   0.5 * 8 + 0.6)))
