# PianoSynth v14 — complete physically-based additive piano voice in one function.
# Bit-identical to the full fitted synth it was distilled from (max|Δ|~1e-13). numpy only.
#
#   synth(m, v=64, d=3) -> np.ndarray
#
#     m : MIDI note number, 21..108 (A0..C8). 60 = middle C.
#     v : MIDI velocity 0..127. Continuously interpolates timbre across the
#         measured pp/mf/ff dynamics (brightness slope, unison detune, hammer
#         knock). Louder => brighter + more attack. Default 64.
#     d : duration in seconds (sustain tail included). Default 3.
#
#   returns: 1-D float32 array of d*44100 mono samples @ 44.1 kHz, UN-normalized
#            (peak ~0.3..0.8). Multiply/clip as needed before writing to audio.
#
#   Model: inharmonic partials f_n = n*f0*sqrt(1+B n^2); pitch+velocity excitation
#   slope (bass rich, treble pure); note/partial-dependent two-stage decay; unison
#   string beating (1/2/3 strings by register); soft attack; low-passed hammer
#   knock; procedural log-frequency soundboard "body" EQ.   (~880 chars of code)
from numpy import*
def synth(m,v=64,d=3):
 e=m-60
 a,s,D,k=[interp(v,[36,75,101],y)for y in([2.43,2.19,1.84],[.04,.088,.094],[3,3,2],[.02,.035,.06])]
 F=440*2**((m-69)/12)
 n=arange(1,65)
 f=n*F*(1+exp(-7.79+.0653*e)*n*n)**.5
 j=f<=12e3
 n,f=n[j],f[j]
 A=n**-clip(a+s*e,1.5,3.6)/(1+(f/6e3)**4)**.5
 A/=A.max()
 T=maximum(.835*exp(-.0277*e)*(F/f)**.4,.05)
 N=int(d*44100)
 t=arange(N)/44100
 g=random.default_rng(m)
 w=fft.rfftfreq(N,1/44100)
 E=A[:,None]*(.85*exp(-t/T[:,None])+.15*exp(-8*t/T[:,None]))
 S=1 if m<=28 else 2 if m<=40 else 3
 o=zeros(N)
 for c in[0]if S<2 else[(2*i/(S-1)-1)*D for i in range(S)]:
  o+=(E*sin(2*pi*(f*2**(c/1200))[:,None]*t+g.uniform(0,2*pi,len(f))[:,None])).sum(0)
 o=o/S*(1-exp(-t/.004))
 z=fft.irfft(fft.rfft(g.normal(0,1,N))/(1+(w/1500)**2)**.5,N)
 o+=k*z/(abs(z).max()+1e-9)*exp(-t/.006)
 o=fft.irfft(fft.rfft(o)*10**(polyval([-.564,-.814,1.385],log2(w/1e3+.02))/20),N)
 return float32(o)
