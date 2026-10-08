"""Banda sonora original para el video de lanzamiento de OMMA.

Piano + colchón de cuerdas en re mayor, sintetizados aquí mismo (sin
muestras ni licencias de terceros). Pulso de 1,1 s (54,5 BPM), alineado con
los cortes del video; los acentos de diseño sonoro caen en los tiempos
exactos de las transiciones.

    python3 tools/musica.py out/musica.wav
"""
import sys
import wave

import numpy as np

SR = 48000
DURATION = 40.0
N = int(SR * DURATION)
BEAT = 1.1           # un corte de palabra = un tiempo
EIGHTH = BEAT / 2
rng = np.random.default_rng(7)

music = np.zeros((2, N), np.float32)   # bus con reverberación
dry = np.zeros((2, N), np.float32)     # graves sin reverberación


def mtof(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def add(sig, t, pan=0.0, gain=1.0, bus=None):
    bus = music if bus is None else bus
    i = int(t * SR)
    if i >= N:
        return
    j = min(N, i + len(sig))
    seg = sig[: j - i] * gain
    a = (pan + 1) * np.pi / 4
    bus[0, i:j] += seg * np.cos(a)
    bus[1, i:j] += seg * np.sin(a)


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


# ---- Armonía: un acorde por capítulo -------------------------------------------
DMAJ9 = [50, 57, 61, 64, 66, 69, 73, 76]
BM11 = [47, 54, 57, 62, 64, 66, 69, 74]
GMAJ7 = [43, 50, 54, 59, 61, 66, 71, 74]
ASUS = [45, 52, 59, 62, 64, 66, 71, 76]
EM9 = [40, 47, 50, 54, 55, 59, 62, 66]
A6 = [45, 52, 57, 61, 64, 66, 69, 73]
BM9 = [47, 54, 57, 61, 62, 66, 69, 73]
ARP = [0, 3, 5, 6, 4, 7, 5, 3]          # orden del arpegio en corcheas

# 0–4,6 s · el hilo: colchón que se abre y notas sueltas
add(pad([50, 57, 64, 66, 73], 4.6, attack=3.0), 0.0, gain=0.9)
for t, m, v, p in [(0.35, 69, .45, .2), (1.45, 78, .35, -.2), (2.55, 76, .38, .25), (3.65, 73, .42, -.1)]:
    add(piano(m, v), t, pan=p)

# 4,6–22,2 s · bocetos, oficio, diseño: cuatro acordes de 4,4 s
for c, chord in enumerate([DMAJ9, BM11, GMAJ7, ASUS]):
    t0 = 4.6 + c * 4.4
    add(pad(chord[1:6], 4.4, attack=1.2), t0, gain=0.8)
    add(bass(chord[0] - 12, 4.4), t0, bus=dry)
    for i in range(8):
        idx = ARP[i]
        v = 0.55 if i == 0 else 0.38 + 0.08 * rng.random()
        add(piano(chord[idx], v), t0 + i * EIGHTH, pan=(idx - 3.5) / 7)
    add(piano(chord[-1] + 12, 0.3), t0 + 0.02, pan=0.3)   # campanita aguda al cambiar de acorde

# 22,2–26,6 s · proceso: pulso en cada corte, tensión que sube
for c, chord in enumerate([EM9, EM9, A6, A6]):
    t0 = 22.2 + c * BEAT
    add(thump(0.9), t0, bus=dry)
    add(piano(chord[0] + 12, .6) + piano(chord[3], .5) + piano(chord[5], .5), t0)
    for i in range(1, 2):
        add(piano(chord[ARP[(c * 2 + i) % 8]], .4), t0 + i * EIGHTH, pan=.2)
    add(bass(chord[0] - 12, BEAT), t0, bus=dry)
add(pad(EM9[2:7], 2.2, attack=.6), 22.2, gain=0.8)
add(pad(A6[2:7], 2.3, attack=.6, cutoff=2200), 24.4, gain=0.95)
add(whoosh(2.4, peak=.92, fmax=7000, gain=.8), 24.3)

# 26,6–32,2 s · «Hecho para ti»: respiro, solo colchón y notas largas
add(pad(BM9[1:7], 5.6, attack=1.0), 26.6, gain=0.75)
add(bass(BM9[0] - 12, 5.6), 26.6, bus=dry, gain=0.7)
for t, m, v in [(27.7, 78, .4), (28.8, 76, .35), (29.9, 73, .38), (31.0, 74, .33)]:
    add(piano(m, v), t, pan=.15)

# 32,2–40 s · firma: resolución en re mayor
add(whoosh(1.4, peak=.85, fmax=6000, gain=.9), 31.0)
add(thump(1.3, f0=70, f1=32, decay=1.4), 32.25, bus=dry)
for m, v in [(38, .7), (50, .6), (57, .5), (61, .45), (64, .45), (69, .4)]:
    add(piano(m, v, dur=7.0), 32.25, pan=(m - 55) / 40)
add(pad([50, 57, 61, 64, 69, 73], 5.0, attack=1.4, release=2.5), 32.2, gain=1.0)
add(bass(38, 6.0), 32.2, bus=dry)
for t, m in [(34.9, 81), (35.2, 85), (35.5, 88)]:          # destello al asentarse el logotipo
    add(piano(m, .32), t, pan=.35)

# Transiciones: aire suave en cada cambio de escena
for t in (4.4, 11.2, 16.1, 26.5):
    add(whoosh(1.0, peak=.55, gain=.55), t)

# ---- Mezcla ---------------------------------------------------------------------
mix = reverb(music) + dry
mix -= mix.mean(axis=1, keepdims=True)
fade = np.ones(N, np.float32)
fade[int(SR * 37.5):] = np.linspace(1, 0, N - int(SR * 37.5)) ** 1.5
fade[: int(SR * .05)] = np.linspace(0, 1, int(SR * .05))
mix *= fade
mix = np.tanh(1.2 * mix / np.max(np.abs(mix))) / np.tanh(1.2) * 0.89

out = sys.argv[1] if len(sys.argv) > 1 else 'out/musica.wav'
with wave.open(out, 'wb') as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes((mix.T * 32767).astype(np.int16).tobytes())
print('listo:', out)
