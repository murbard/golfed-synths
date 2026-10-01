"""
Small physically-motivated additive OBOE model.

Driven double-reed: a *sustained*, near-perfectly-harmonic tone whose timbre comes
from fixed bore/reed resonances (formants), not from a pitch-dependent decay.

    f_n   = n * f0                       (harmonic; B ~ 0, measured)
    A_n(t)= formant(f_n * (1+vibrato(t))) (FIXED formant in absolute Hz; as the
            vibrato wavers the pitch, each partial slides along the formant curve
            -> natural per-partial amplitude shimmer, the key realism cue)
    + slow per-partial jitter + tiny pitch flutter (a living, non-static tone)
    + breath noise; attack/sustain/release envelope.

Formant envelope: main +28 dB @ 1.29 kHz, a softened second @ 3.0 kHz, a -10 dB/oct
tilt and a gentle extra HF rolloff above ~4.5 kHz (warmth). Fit to the pooled
spectra of the 35 Iowa ff notes (Bb3-Ab6), then warmed per listening test "D".
"""
from __future__ import annotations
import numpy as np

SR = 44100

_BASE, _TILT = -23.15, -9.97
_FORMANTS = ((27.78, 1291.9, 0.65), (20.0, 3000.0, 0.50))   # (gain dB, center Hz, width oct)


def formant_db(f):
    f = np.asarray(f, float)
    db = _BASE + _TILT * np.log2(np.maximum(f, 1e-6) / 1000.0)
    for g, fc, w in _FORMANTS:
        db = db + g * np.exp(-(np.log2(np.maximum(f, 1e-6) / fc) ** 2) / (2 * w * w))
    db = db - 6.0 * np.maximum(0.0, np.log2(np.maximum(f, 1.0) / 4500.0))   # warmth: HF rolloff
    return db


def reverb(x, wet=0.16, decay=0.12, length=0.35, sr=SR, seed=1):
    """Light room reverb via FFT convolution with an exp-decaying noise IR."""
    L = int(length * sr)
    ir = np.random.default_rng(seed).standard_normal(L) * np.exp(-np.arange(L) / (decay * sr))
    n = len(x) + L
    y = np.fft.irfft(np.fft.rfft(x, n) * np.fft.rfft(ir, n), n)[:len(x)]
    y /= np.abs(y).max() + 1e-9
    out = (1 - wet) * x + wet * y
    return (out / (np.abs(out).max() + 1e-9)).astype(np.float32)


def oboe_synth(midi, dur=2.0, vel=80, vib_rate=5.5, vib_cents=5.0,
               attack=0.08, release=0.10, breath=0.015, seed=None, et_epsilon=None,
               decay=0.0):
    """Render one oboe note -> float32 mono @ 44.1 kHz (dry; apply reverb() to taste).
    Formant-tracking vibrato gives the partials natural shimmer. ``et_epsilon``
    (per-partial fractional offsets) applies the Sethares spectrum tuning."""
    f0 = 440.0 * 2.0 ** ((midi - 69) / 12.0)
    N = int(dur * SR); t = np.arange(N) / SR
    rng = np.random.default_rng(midi if seed is None else seed)

    n = np.arange(1, int(0.48 * SR / f0) + 1)
    fn = n * f0
    if et_epsilon is not None:
        eps = np.zeros(len(n)); m = min(len(et_epsilon), len(n))
        eps[:m] = np.asarray(et_epsilon)[:m]; fn = fn * (1.0 + eps)
    A0 = 10.0 ** (formant_db(fn) / 20.0)
    A0 = A0 * (n ** (-0.3 * (1.0 - vel / 127.0)))            # softer/darker when quieter
    A0 = A0 / A0.max()
    db0 = formant_db(fn)                                     # reference formant gain per partial

    vib = (vib_cents / 1200.0) * np.log(2) * np.sin(2 * np.pi * vib_rate * t)
    flut = np.cumsum(rng.standard_normal(N)); flut = flut / (np.abs(flut).max() + 1e-9) * 0.0015
    vt = vib + flut                                          # total fractional pitch deviation
    phase = 2 * np.pi * np.cumsum(f0 * (1.0 + vt)) / SR      # base phase; partial k uses (fk/f0)*phase

    out = np.zeros(N)
    for fk, a0, d0 in zip(fn, A0, db0):
        g = 10.0 ** ((formant_db(fk * (1.0 + vt)) - d0) / 20.0)          # formant-tracking shimmer
        jit = 1.0 + 0.05 * np.sin(2 * np.pi * (3 + 2.5 * rng.random()) * t + rng.uniform(0, 2 * np.pi))
        out += a0 * g * jit * np.sin((fk / f0) * phase + rng.uniform(0, 2 * np.pi))

    env = np.ones(N); na, nr = int(attack * SR), int(release * SR)
    if na: env[:na] = np.linspace(0, 1, na) ** 1.5
    if nr: env[-nr:] = np.linspace(1, 0, nr)
    if decay: env = env * np.exp(-decay * t)        # gentle per-note taper -> phrased, not tenuto
    out *= env

    nz = rng.standard_normal(N); fw = np.fft.rfftfreq(N, 1 / SR)
    nz = np.fft.irfft(np.fft.rfft(nz) * (fw < 4000), n=N); nz /= np.abs(nz).max() + 1e-9
    out += breath * nz * env * (0.4 + 0.6 * np.exp(-t / 0.05))

    return (out / (np.abs(out).max() + 1e-9)).astype(np.float32)
