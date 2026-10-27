"""Instrumentos sintetizados para las bandas sonoras de OMMA (sin muestras ni licencias).

Uso:
    from sintesis import Mezcla, piano, pad, bass, thump, whoosh
    m = Mezcla(20.0)
    m.add(piano(62, .5), 1.0)
    m.guardar('out/x.wav', fade_out=18.0)
"""
import wave

import numpy as np

SR = 48000
rng = np.random.default_rng(7)


class Mezcla:
    """Dos buses estéreo: uno con reverberación (música) y uno seco (graves)."""

    def __init__(self, duration):
        self.N = int(SR * duration)
        self.music = np.zeros((2, self.N), np.float32)
        self.dry = np.zeros((2, self.N), np.float32)

    def add(self, sig, t, pan=0.0, gain=1.0, dry=False):
        bus = self.dry if dry else self.music
        i = int(t * SR)
        if i >= self.N:
            return
        j = min(self.N, i + len(sig))
        seg = sig[: j - i] * gain
        a = (pan + 1) * np.pi / 4
        bus[0, i:j] += seg * np.cos(a)
        bus[1, i:j] += seg * np.sin(a)

    def guardar(self, out, fade_out):
        mix = reverb(self.music) + self.dry
        mix -= mix.mean(axis=1, keepdims=True)
        fade = np.ones(self.N, np.float32)
        k = int(SR * fade_out)
        fade[k:] = np.linspace(1, 0, self.N - k) ** 1.5
        fade[: int(SR * .05)] = np.linspace(0, 1, int(SR * .05))
        mix *= fade
        mix = np.tanh(1.2 * mix / np.max(np.abs(mix))) / np.tanh(1.2) * 0.89
        with wave.open(out, 'wb') as w:
            w.setnchannels(2)
            w.setsampwidth(2)
            w.setframerate(SR)
            w.writeframes((mix.T * 32767).astype(np.int16).tobytes())
        print('listo:', out)


def mtof(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def piano(m, vel=0.6, dur=5.0):
    f = mtof(m)
    n = int(SR * dur)
    t = np.arange(n, dtype=np.float32) / SR
    out = np.zeros(n, np.float32)
    brightness = 0.35 + 0.65 * vel
    for k in range(1, 11):
        fk = k * f * np.sqrt(1 + 0.00035 * k * k)
        if fk > 9000:
            break
        amp = brightness ** (k - 1) / k ** 1.1
        s = (f / 260) ** 0.5
        env = 0.7 * np.exp(-t * (1.6 + 0.9 * k) * s) + 0.3 * np.exp(-t * 0.35 * s)
        out += amp * env * np.sin(2 * np.pi * fk * t + rng.uniform(0, 6.28))
    out *= np.clip(t / 0.004, 0, 1)
    out[-int(SR * .3):] *= np.linspace(1, 0, int(SR * .3))
    hammer = rng.normal(0, 1, int(SR * .012)).astype(np.float32)
    hammer = np.convolve(hammer, np.ones(8) / 8, 'same') * np.linspace(1, 0, len(hammer))
    out[: len(hammer)] += 0.03 * hammer
    return out * vel * 0.22


def pad(notes, dur, attack=1.8, release=2.5, cutoff=1400):
    n = int(SR * (dur + release))
    t = np.arange(n, dtype=np.float32) / SR
    env = np.clip(t / attack, 0, 1) ** 2 * np.where(t < dur, 1.0, np.exp(-(t - dur) * 3 / release))
    sig = np.zeros(n, np.float32)
    for m in notes:
        f = mtof(m)
        for cents in (-7, 0, 7):
            fd = f * 2 ** (cents / 1200)
            rate = rng.uniform(.2, .4)
            vib = np.sin(2 * np.pi * rate * t) * 0.0015 / rate   # ±0,15 % de afinación, lento
            for k in range(1, 13):
                fk = k * fd
                if fk > 5000:
                    break
                a = (1 / k) / (1 + (fk / cutoff) ** 2)
                sig += a * np.sin(2 * np.pi * fk * t + fk * vib + rng.uniform(0, 6.28))
    return sig * env * 0.018


def bass(m, dur):
    n = int(SR * (dur + 1.0))
    t = np.arange(n, dtype=np.float32) / SR
    f = mtof(m)
    env = np.clip(t / 0.08, 0, 1) * np.where(t < dur, np.exp(-t * 0.15), np.exp(-dur * 0.15) * np.exp(-(t - dur) * 4))
    return (np.sin(2 * np.pi * f * t) + 0.25 * np.sin(4 * np.pi * f * t)) * env * 0.16


def thump(gain=1.0, f0=95, f1=45, decay=5.0):
    n = int(SR * 1.2)
    t = np.arange(n, dtype=np.float32) / SR
    f = f1 + (f0 - f1) * np.exp(-t * 25)
    ph = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(ph) * np.exp(-t * decay) * np.clip(t / 0.003, 0, 1) * 0.5 * gain


def whoosh(dur=1.0, peak=0.6, fmax=5000, gain=1.0):
    """Aire de transición: ruido con filtro paso bajo que sube y baja."""
    n = int(SR * dur)
    x = rng.normal(0, 1, n).astype(np.float32)
    t = np.arange(n) / n
    shape = np.where(t < peak, np.sin(np.pi / 2 * t / peak), np.cos(np.pi / 2 * (t - peak) / (1 - peak)))
    fc = 250 + (fmax - 250) * shape ** 2
    a = 1 - np.exp(-2 * np.pi * fc / SR)
    y = np.zeros(n, np.float32)
    y1 = y2 = 0.0
    for i in range(n):
        y1 += a[i] * (x[i] - y1)
        y2 += a[i] * (y1 - y2)
        y[i] = y2
    env = np.where(t < peak, (t / peak) ** 2, ((1 - t) / (1 - peak)) ** 1.5)
    return y * env * 0.5 * gain


def reverb(sig, seconds=3.2, mix=0.38):
    n = int(SR * seconds)
    t = np.arange(n) / SR
    out = np.empty_like(sig)
    for ch in range(2):
        ir = rng.normal(0, 1, n) * np.exp(-t / 0.55)
        ir = np.convolve(ir, np.ones(6) / 6, 'same')   # cola más oscura
        ir[: int(SR * .02)] = 0                          # pre-retardo
        ir /= np.sqrt(np.sum(ir ** 2))
        size = 1 << int(np.ceil(np.log2(len(sig[ch]) + n)))
        wet = np.fft.irfft(np.fft.rfft(sig[ch], size) * np.fft.rfft(ir, size), size)[: sig.shape[1]]
        out[ch] = sig[ch] + mix * wet
    return out
