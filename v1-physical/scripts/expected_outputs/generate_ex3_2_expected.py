"""
Expected Output Generator: Exercise 3.2 — FFT, SNR & THD Analysis
===================================================================
Generates reference 4-panel analysis plot (no hardware needed).

Run: python generate_ex3_2_expected.py
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

np.random.seed(55)

# Simulate oscilloscope capture of 1 kHz sine with harmonics + noise
fs = 125e3           # Sample rate
N = 2048             # Samples
SIGNAL_FREQ = 1e3    # 1 kHz fundamental
AMPLITUDE = 0.25     # ±0.25V

t = np.arange(N) / fs
signal = (AMPLITUDE * np.sin(2 * np.pi * SIGNAL_FREQ * t)
          + 0.003 * np.sin(2 * np.pi * 2e3 * t)     # 2nd harmonic
          + 0.001 * np.sin(2 * np.pi * 3e3 * t)     # 3rd harmonic
          + 0.0005 * np.sin(2 * np.pi * 4e3 * t)    # 4th harmonic
          + 0.0003 * np.sin(2 * np.pi * 5e3 * t)    # 5th harmonic
          + 0.002 * np.random.randn(N))               # noise

# --- FFT ---
window = np.hanning(N)
fft_vals = np.fft.rfft(signal * window)
fft_mag = 2.0 / N * np.abs(fft_vals)
freqs = np.fft.rfftfreq(N, 1 / fs)

# Dominant frequency
peak_idx = np.argmax(fft_mag[1:]) + 1
f_dominant = freqs[peak_idx]
peak_amp = fft_mag[peak_idx]

# SNR
signal_power = peak_amp ** 2
noise_indices = [i for i in range(1, len(fft_mag)) if abs(i - peak_idx) > 2]
noise_power = np.mean([fft_mag[i] ** 2 for i in noise_indices])
snr_db = 10 * np.log10(signal_power / max(noise_power, 1e-20))

# THD
NUM_HARMONICS = 5
harmonics = []
for h in range(2, NUM_HARMONICS + 1):
    h_idx = int(peak_idx * h)
    if h_idx < len(fft_mag):
        harmonics.append(fft_mag[h_idx])

thd = np.sqrt(sum(h ** 2 for h in harmonics)) / peak_amp
thd_pct = thd * 100

# --- Plot ---
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# Time domain
axes[0, 0].plot(t * 1e3, signal, color='#2B6CB0', linewidth=0.8)
axes[0, 0].set_xlabel('Time (ms)')
axes[0, 0].set_ylabel('Voltage (V)')
axes[0, 0].set_title('Time Domain', fontweight='bold')
axes[0, 0].grid(True, alpha=0.3)

# FFT spectrum
axes[0, 1].semilogy(freqs / 1e3, fft_mag, color='#0D9488', linewidth=0.8)
axes[0, 1].set_xlabel('Frequency (kHz)')
axes[0, 1].set_ylabel('Magnitude (V)')
axes[0, 1].set_title('FFT Spectrum', fontweight='bold')
axes[0, 1].grid(True, alpha=0.3)
axes[0, 1].axvline(x=f_dominant / 1e3, color='red', linestyle='--',
                    alpha=0.5, label=f'f₀={f_dominant:.0f} Hz')
axes[0, 1].legend()

# Harmonic content (zoomed)
max_harm_freq = f_dominant * (NUM_HARMONICS + 1)
mask = freqs <= max_harm_freq
axes[1, 0].stem(freqs[mask] / 1e3, fft_mag[mask], linefmt='-',
                markerfmt='o', basefmt='gray')
axes[1, 0].set_xlabel('Frequency (kHz)')
axes[1, 0].set_ylabel('Magnitude (V)')
axes[1, 0].set_title('Harmonic Content', fontweight='bold')
axes[1, 0].grid(True, alpha=0.3)

# Quality report
axes[1, 1].axis('off')
summary_text = (
    f"Signal Quality Report\n"
    f"{'─' * 30}\n"
    f"Frequency:  {f_dominant:.1f} Hz\n"
    f"Amplitude:  {max(signal)-min(signal):.4f} Vpp\n"
    f"SNR:        {snr_db:.1f} dB\n"
    f"THD:        {thd_pct:.2f}%\n"
    f"{'─' * 30}\n"
    f"Samples:    {N}\n"
    f"Sample Rate:{fs/1e3:.1f} kSa/s\n"
)
axes[1, 1].text(0.1, 0.9, summary_text, transform=axes[1, 1].transAxes,
                fontsize=13, verticalalignment='top', fontfamily='monospace',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

plt.suptitle('Expected Output: Exercise 3.2 — FFT, SNR & THD Analysis',
             fontsize=13, fontweight='bold', color='#1A365D')
plt.tight_layout()
plt.savefig('ex3_2_expected.png', dpi=150, bbox_inches='tight')
print("✓ Saved: ex3_2_expected.png")

# Console output
print("\n--- Expected Console Output ---")
print(f"Captured: {N} samples at {fs/1e3:.1f} kSa/s")
print(f"\nDominant frequency: {f_dominant:.1f} Hz")
print(f"Peak FFT amplitude: {peak_amp:.4f} V")
print(f"\nSNR: {snr_db:.1f} dB")
print(f"  Signal power: {signal_power:.6e}")
print(f"  Noise power:  {noise_power:.6e}")
for h_num, h_amp in enumerate(harmonics, 2):
    print(f"  Harmonic {h_num}: {f_dominant*h_num:.0f} Hz, "
          f"amplitude = {h_amp:.6f} V")
print(f"\nTHD: {thd_pct:.2f}%")
print(f"\n{'='*50}")
print(f"SIGNAL QUALITY REPORT")
print(f"{'='*50}")
print(f"  Frequency:    {f_dominant:.1f} Hz "
      f"(expected: 1000 Hz, error: {abs(f_dominant-1e3)/1e3*100:.2f}%)")
print(f"  SNR:          {snr_db:.1f} dB "
      f"({'GOOD' if snr_db > 40 else 'FAIR'})")
print(f"  THD:          {thd_pct:.2f}% "
      f"({'GOOD' if thd_pct < 1 else 'FAIR'})")
