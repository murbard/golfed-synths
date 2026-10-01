# golfed-synths

A whole piano in about 900 characters of numpy, plus a small oboe.

Neither voice uses samples. Each note is a sum of sine partials, and every parameter (inharmonicity,
decay, brightness, unison detune, body EQ, formants) was measured from the
[University of Iowa MIS](https://theremin.music.uiowa.edu/MIS.html) recordings and then reduced to a few
closed-form laws of pitch and velocity.

```python
from piano import synth          # synth(midi, velocity=64, seconds=3) -> float32 @ 44.1 kHz
from oboe import oboe_synth      # oboe_synth(midi, dur=2.0, vel=80, ...) -> float32 @ 44.1 kHz
```

`python demo.py` writes a piano scale, a piano chord progression and an oboe scale to WAV. Needs numpy only.

## Piano (`piano.py`)

The function body is golfed, but it is not a toy: it is bit-identical (max |Δ| ≈ 1e-13) to the full fitted model it
was distilled from. What it models:

- **Stiff-string inharmonicity.** f_n = n·f₀·√(1 + B·n²), with log B linear in pitch.
- **Excitation.** Partial amplitudes fall as n^(−slope). The slope depends on pitch and velocity, so the bass is rich,
  the treble is pure and loud notes are brighter. A soft low-pass at 6 kHz on top.
- **Decay.** Each partial has its own time constant, shorter for higher notes and for higher partials. The decay
  has two stages: a fast "prompt" drop and a slow aftersound.
- **Unison strings.** 1, 2 or 3 strings depending on register, detuned by a few cents, which gives the beating.
- **Hammer.** A 4 ms attack ramp, plus a short burst of low-passed noise for the knock.
- **Soundboard.** A fixed EQ, quadratic in log-frequency.

Velocity is continuous. It interpolates between the parameters measured separately at pp, mf and ff.

The way it was fit matters more than the formula. Fitting these parameters by gradient descent through an STFT
loss failed: B went negative, the decays collapsed and brightness came out inverted. A magnitude-spectrogram
loss barely constrains any of those quantities. The approach that worked was to run a lock-in (heterodyne)
analysis on every recorded note, which yields each partial's frequency and envelope directly. B, the decay laws and
the detune were read off those measurements and pinned. Only the excitation shape was left to the audio loss.

The upper range is the weakest part.

## Oboe (`oboe.py`)

The oboe is a different architecture. A driven double reed sustains, its partials are almost perfectly harmonic, and
its character comes from fixed resonances rather than from how it decays. The model is harmonic partials under a
fixed formant envelope fit to 35 Iowa ff notes (Bb3–Ab6): +28 dB at 1.29 kHz and a second peak near 3 kHz, on a
−10 dB/octave tilt. On top of that sit 5.5 Hz vibrato and breath noise. The formant is fixed in absolute Hz, so as
the vibrato moves the pitch, each partial slides along the formant curve and its amplitude shimmers. That shimmer
is most of what makes it sound alive. Against the recordings, the harmonic spectra correlate at 0.93–0.96 (in dB).

`et_epsilon` takes per-partial frequency offsets for Sethares-style spectrum tuning, which retunes the timbre so
that equal-tempered intervals land on dissonance minima. With the oboe's brighter spectrum, 9 of the 12 intervals
can be made into minima. With the piano's, it's about 3.

## Ports (`ports/`)

`piano.c` (about 1500 chars, `math.h` only, no FFT) and `piano.jl` (about 1070 chars) port a slightly
earlier revision of the piano. That revision had a table-based body EQ folded into the partial amplitudes, and its
decay law was a little different. Neither port is bit-identical to `piano.py`, because the random number generators
differ. Julia came out larger than numpy, mostly because numpy has `interp` built in.

## License

MIT
