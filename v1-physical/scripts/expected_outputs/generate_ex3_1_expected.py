"""
Expected Output Generator: Exercise 3.1 — Datalogger Streaming
================================================================
Generates reference streaming statistics plot (no hardware needed).

Run: python generate_ex3_1_expected.py
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

np.random.seed(77)

# Simulate 10 seconds of streaming at 10 kSa/s
SAMPLE_RATE = 10e3
DURATION = 10
SIGNAL_FREQ = 100
NUM_SAMPLES = int(SAMPLE_RATE * DURATION)
CHUNK_SIZE = 1024

t = np.arange(NUM_SAMPLES) / SAMPLE_RATE
signal = 0.5 * np.sin(2 * np.pi * SIGNAL_FREQ * t) + np.random.normal(0, 0.005, NUM_SAMPLES)

# Break into chunks and compute per-chunk stats
chunks = [signal[i:i + CHUNK_SIZE] for i in range(0, NUM_SAMPLES, CHUNK_SIZE)]
chunk_means = [np.mean(c) for c in chunks]
chunk_stds = [np.std(c) for c in chunks]
chunk_vpps = [max(c) - min(c) for c in chunks]
chunk_times = [i * CHUNK_SIZE / SAMPLE_RATE for i in range(len(chunks))]

fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# --- Raw signal (first 2000 samples) ---
ax = axes[0, 0]
n_show = 2000
ax.plot(t[:n_show] * 1e3, signal[:n_show], color='#2B6CB0', linewidth=0.5)
ax.set_xlabel('Time (ms)')
ax.set_ylabel('Voltage (V)')
ax.set_title('Raw Stream (First 2000 Samples)', fontweight='bold')
ax.grid(True, alpha=0.3)

# --- Vpp per chunk ---
ax = axes[0, 1]
ax.plot(chunk_times, chunk_vpps, 'o-', color='#0D9488', markersize=3, linewidth=1)
ax.axhline(y=np.mean(chunk_vpps), color='red', linestyle='--',
           label=f'Mean: {np.mean(chunk_vpps):.4f}V')
ax.set_xlabel('Time (s)')
ax.set_ylabel('Vpp (V)')
ax.set_title('Peak-to-Peak per Chunk', fontweight='bold')
ax.grid(True, alpha=0.3)
ax.legend()

# --- Running mean ---
ax = axes[1, 0]
running_mean = np.cumsum(signal) / np.arange(1, NUM_SAMPLES + 1)
ax.plot(t, running_mean, color='#DD6B20', linewidth=1)
ax.set_xlabel('Time (s)')
ax.set_ylabel('Running Mean (V)')
ax.set_title('Running Mean Voltage', fontweight='bold')
ax.grid(True, alpha=0.3)
ax.axhline(y=0, color='gray', linestyle=':', alpha=0.5)

# --- Summary statistics ---
ax = axes[1, 1]
ax.axis('off')
summary = (
    f"Streaming Summary\n"
    f"{'─' * 35}\n"
    f"Total samples:   {NUM_SAMPLES:,}\n"
    f"Total chunks:    {len(chunks)}\n"
    f"Duration:        {DURATION} seconds\n"
    f"Sample rate:     {SAMPLE_RATE/1e3:.0f} kSa/s\n"
    f"{'─' * 35}\n"
    f"Overall Mean:    {np.mean(signal):.6f} V\n"
    f"Overall Std:     {np.std(signal):.6f} V\n"
    f"Overall Vpp:     {max(signal)-min(signal):.4f} V\n"
    f"Min:             {min(signal):.4f} V\n"
    f"Max:             {max(signal):.4f} V\n"
)
ax.text(0.1, 0.9, summary, transform=ax.transAxes,
        fontsize=13, verticalalignment='top', fontfamily='monospace',
        bbox=dict(boxstyle='round', facecolor='#E6FFFA', alpha=0.8))

plt.suptitle('Expected Output: Exercise 3.1 — Datalogger Streaming',
             fontsize=13, fontweight='bold', color='#1A365D')
plt.tight_layout()
plt.savefig('ex3_1_expected.png', dpi=150, bbox_inches='tight')
print("✓ Saved: ex3_1_expected.png")

# Console output
print("\n--- Expected Console Output ---")
print(f"Streaming: {DURATION}s at {SAMPLE_RATE/1e3:.0f} kSa/s")
print(f"Test signal: {SIGNAL_FREQ} Hz sine wave\n")
print(f"{'Chunk':>6} | {'Samples':>8} | {'Mean (V)':>10} | "
      f"{'Std (V)':>10} | {'Vpp (V)':>10}")
print("-" * 58)
for i in range(min(5, len(chunks))):
    c = chunks[i]
    print(f"{i+1:>6} | {len(c):>8} | "
          f"{np.mean(c):>10.4f} | {np.std(c):>10.4f} | "
          f"{max(c)-min(c):>10.4f}")
print(f"  ... ({len(chunks)} total chunks)")
print(f"\nStream complete!")
print(f"\n{'='*58}")
print(f"STREAMING SUMMARY")
print(f"{'='*58}")
print(f"  Total samples:   {NUM_SAMPLES:,}")
print(f"  Total chunks:    {len(chunks)}")
print(f"  Actual duration: {DURATION:.1f} seconds")
print(f"  Effective rate:  {NUM_SAMPLES/DURATION:,.0f} Sa/s")
print(f"  Overall Mean:    {np.mean(signal):.6f} V")
print(f"  Overall Std:     {np.std(signal):.6f} V")
print(f"  Overall Vpp:     {max(signal)-min(signal):.4f} V")
