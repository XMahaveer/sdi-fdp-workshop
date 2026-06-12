# MCC Experiment Guide — Threshold Detector

**Day 5 MCC Session | 60 minutes hands-on | 5-Day SDI Lab Automation FDP (v2.0)**

**Trainer:** Mahaveer. Rajendra. Savanur — Head of Engineering & AI Systems
**Organization:** Spruha Build-in Solutions | Powered by Moku:Go — Liquid Instruments

---

## Goal

Feel the **Moku Custom Instrument (MCC)** architecture by completing a
minimal custom instrument: a threshold detector that

1. reads analog **InputA**,
2. compares it to a threshold that **Python sets via Control0**,
3. drives **OutputA** HIGH (+1 V) while the signal is above threshold, and
4. reports **threshold crossings per second** to Python via **Status0**.

This is intentionally simple. The point is the *architecture* — how your
Verilog lives inside the Moku infrastructure — not DSP.

## Files

| File | Role |
|------|------|
| `mcc_threshold_detector_skeleton.v` | You complete the 3 TODO blocks |
| `mcc_threshold_detector_solution.v` | Trainer reference (not distributed) |
| `mcc_threshold_detector_host.py` | Python side: sets threshold, reads counts |

## The 5 differences from your FPGA lab (recap)

| Your FPGA lab | MCC |
|---|---|
| Name your own top module | Top module is always `CustomWrapper` |
| Pick your clock | `Clk` is the 125 MHz system clock, fixed |
| Define your own ports | Port list is fixed — logic goes inside |
| Raw integer signals | Q1.15 signed 16-bit: `32767 = +1.0 V`, `-32768 = -1.0 V` |
| JTAG / hardware programmer | Python ⇄ FPGA via `Control0–19` (in) and `Status0–3` (out) |

Two more Moku:Go-specific facts: **OutputD is not physical** on Moku:Go,
and **OutputC is disconnected in 3-slot MIM mode** (fine here — we use
2-slot). Synthesis happens on the **Liquid Instruments cloud**, not in
your local Vivado.

## Step-by-Step

### Step 1 — Read the skeleton (10 min)

Open `mcc_threshold_detector_skeleton.v`. Find and identify out loud:
the fixed module name, the 125 MHz clock, the full Control0–19 port
block (all 20 must be declared even when unused), and the Status
registers (`output reg` — *outputs* from your Verilog, a direction
faculty often invert).

### Step 2 — Complete TODO 1: the comparator (10 min)

One line. Both `InputA` and `threshold` are signed Q1.15:

```verilog
wire above = ($signed(InputA) > threshold);
```

Why `$signed()`? Port signals arrive as plain bit vectors; without the
cast, Verilog compares them as unsigned and negative voltages would read
as huge positive numbers.

### Step 3 — Complete TODO 2: the output driver (5 min)

Inside the clocked block, drive full scale while above threshold:

```verilog
if (above)
    OutputA <= 16'sh7FFF;   // +1.0 V
else
    OutputA <= 16'd0;       // 0 V
```

### Step 4 — Complete TODO 3: crossings per second (15 min)

The skeleton already detects a rising crossing (`crossing`). Count them,
and once every second (125,000,000 clock cycles) latch the count into
`Status0` and restart:

```verilog
if (tick_counter == ONE_SECOND - 1) begin
    Status0 <= crossing ? crossing_counter + 1 : crossing_counter;
    tick_counter <= 32'd0;
    crossing_counter <= 32'd0;
end
else begin
    tick_counter <= tick_counter + 1;
    if (crossing)
        crossing_counter <= crossing_counter + 1;
end
```

Discussion point: why latch-and-reset instead of letting Python compute
the rate? (Answer: the FPGA's one-second window is exact; Python's
`time.sleep(1)` is not.)

### Step 5 — Compile in the cloud (10 min, trainer-led)

1. Sign in to the Liquid Instruments MCC build portal
   (see https://apis.liquidinstruments.com/mcc/ for current workflow)
2. Create a project targeting **Moku:Go**, upload your completed `.v` file
3. Start the build — synthesis runs on their cloud (NOT local Vivado)
4. Download the resulting bitstream file when the build succeeds

> Trainer note: pre-compile the solution bitstream before the session so
> there is a known-good fallback if the venue network is slow.

### Step 6 — Run it (10 min)

1. BNC cable: **Output 1 → Input 1**
2. In `mcc_threshold_detector_host.py`, set `BITSTREAM` to your
   downloaded file path (the Moku IP comes from `../config.py`)
3. Run it. The Waveform Generator in Slot 2 produces a 100 Hz sine;
   your instrument in Slot 1 watches it.

**Expected result:** `Status0` reads **~100 crossings/sec** (one rising
crossing per cycle of the 100 Hz sine, threshold at half amplitude).

Experiments to try:

| Change | Expected effect |
|--------|-----------------|
| Threshold → 30000 (above the peak) | crossings → 0 |
| Threshold → 0 *(careful: 0 means "use default 8192" in our design)* | still ~100 |
| Signal frequency → 250 Hz | crossings → ~250 |
| Amplitude below threshold | crossings → 0 |

## Where this fits in your syllabus

- **Digital Design / VLSI lab:** real synthesis constraints, fixed-point
  formats, register interfaces — beyond the bare-FPGA flow
- **DSP lab:** the comparator is the front door; swap in a filter next
- **Communication Systems:** the validated ASK/PSK/FSK modulator sources
  follow this exact CustomWrapper pattern at larger scale
- **Instrumentation:** students see how commercial SDI equipment is
  actually built — an instrument shell plus a custom DSP core

## Common mistakes to warn students about

1. Renaming `CustomWrapper` — build fails
2. Designing timing for the 50 MHz clock from their lab board — it's 125 MHz
3. Outputting raw integers without Q1.15 scaling — tiny or clipped signals
4. Forgetting to declare all 20 Control ports — build fails
5. Declaring Status registers as inputs — they are `output reg`
6. Expecting `$finish`/testbench constructs to synthesize — simulation only
7. Initializing LUTs from `.mif` files — use `initial begin` with
   `$rtoi`/`$sin`/`$cos` instead
