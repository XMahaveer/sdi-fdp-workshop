`timescale 1ns/1ps

// ========================================================================
// Moku Custom Instrument (MCC) — Threshold Detector SKELETON
// 5-Day SDI Lab Automation FDP (v2.0) — Day 5 MCC Session
//
// Complete the three TODO blocks during the session.
//
// What this instrument does when finished:
//   - Reads analog InputA (16-bit signed Q1.15, 125 MSa/s)
//   - Compares it to a threshold set from Python via Control0
//   - Drives OutputA HIGH (+1.0 V) while the signal is above threshold,
//     0 V otherwise
//   - Counts threshold crossings per second into Status0 (read by Python)
//
// REMEMBER THE 5 MCC DIFFERENCES vs your FPGA lab:
//   1. Top module MUST be named CustomWrapper — you cannot change it
//   2. Clk is the 125 MHz system clock — platform-defined
//   3. The port list is FIXED — your logic goes inside
//   4. Signals are Q1.15 signed 16-bit (32767 = +1.0 V)
//   5. Python talks to you ONLY via Control0-19 (in) and Status0-3 (out)
//
// Trainer: Mahaveer. Rajendra. Savanur — Spruha Build-in Solutions
// Powered by Moku:Go — Liquid Instruments
// ========================================================================

module CustomWrapper(
    input wire Clk,                      // 125 MHz system clock
    input wire Reset,                    // Active-high reset
    input wire [31:0] Sync,              // Synchronization (unused)
    input wire [15:0] InputA,            // Analog Input A — our signal
    input wire [15:0] InputB,            // Unused
    input wire [15:0] InputC,            // Unused
    input wire [15:0] InputD,            // Unused
    input wire exttrig,                  // External trigger (unused)
    output reg [15:0] OutputA,           // HIGH/LOW threshold indicator
    output reg [15:0] OutputB,           // Unused
    output reg [15:0] OutputC,           // Unused
    output reg [15:0] OutputD,           // Unused (not physical on Moku:Go)
    input wire [15:0] outputinterpa,     // Interpolator (unused)
    input wire [15:0] outputinterpb,     // Interpolator (unused)
    input wire [15:0] outputinterpc,     // Interpolator (unused)
    input wire [15:0] outputinterpd,     // Interpolator (unused)
    input wire [31:0] Control0,          // Threshold value (Q1.15 in [15:0])
    input wire [31:0] Control1,          // Reserved
    input wire [31:0] Control2,          // Reserved
    input wire [31:0] Control3,          // Reserved
    input wire [31:0] Control4,          // Reserved
    input wire [31:0] Control5,          // Reserved
    input wire [31:0] Control6,          // Reserved
    input wire [31:0] Control7,          // Reserved
    input wire [31:0] Control8,          // Reserved
    input wire [31:0] Control9,          // Reserved
    input wire [31:0] Control10,         // Reserved
    input wire [31:0] Control11,         // Reserved
    input wire [31:0] Control12,         // Reserved
    input wire [31:0] Control13,         // Reserved
    input wire [31:0] Control14,         // Reserved
    input wire [31:0] Control15,         // Reserved
    input wire [31:0] Control16,         // Reserved
    input wire [31:0] Control17,         // Reserved
    input wire [31:0] Control18,         // Reserved
    input wire [31:0] Control19,         // Reserved
    output reg [31:0] Status0,           // Threshold crossings per second
    output reg [31:0] Status1,           // Reserved
    output reg [31:0] Status2,           // Reserved
    output reg [31:0] Status3            // Reserved
);

// ========================================================================
// Control register mapping with a sensible default
// Default threshold: 0x2000 = 8192 = 0.25 of full scale (~0.25 V)
// ========================================================================
wire signed [15:0] threshold = (Control0[15:0] == 0) ? 16'sh2000
                                                     : Control0[15:0];

// ========================================================================
// TODO 1 — COMPARATOR (one line)
// Make 'above' TRUE when the signed input exceeds the signed threshold.
// Hint: both InputA and threshold are signed Q1.15 — use $signed().
// ========================================================================
wire above = 1'b0;   // <-- replace this line

// ========================================================================
// Crossing detector — register the previous comparator state so we can
// see a 0 -> 1 transition (a rising crossing)
// ========================================================================
reg above_prev;
wire crossing = above & ~above_prev;     // rising edge of 'above'

// One-second tick: 125,000,000 clock cycles at 125 MHz
localparam [31:0] ONE_SECOND = 32'd125_000_000;
reg [31:0] tick_counter;
reg [31:0] crossing_counter;

// ========================================================================
// Main sequential logic
// ========================================================================
always @(posedge Clk) begin
    if (Reset) begin
        OutputA <= 16'd0;
        above_prev <= 1'b0;
        tick_counter <= 32'd0;
        crossing_counter <= 32'd0;
        Status0 <= 32'd0;
    end
    else begin
        above_prev <= above;

        // ================================================================
        // TODO 2 — OUTPUT DRIVER (2-3 lines)
        // Drive OutputA to full scale (+1.0 V = 16'sh7FFF) while 'above'
        // is true, and to 0 (16'd0) otherwise.
        // ================================================================
        OutputA <= 16'd0;   // <-- replace this line

        // ================================================================
        // TODO 3 — CROSSINGS-PER-SECOND COUNTER (5-6 lines)
        // a) Increment crossing_counter when 'crossing' is true
        // b) Increment tick_counter every clock
        // c) When tick_counter reaches ONE_SECOND - 1:
        //      - latch crossing_counter into Status0
        //      - reset both counters to zero
        // ================================================================
        // <-- your counter logic here

    end
end

// Tie off unused outputs (good MCC hygiene)
always @(posedge Clk) begin
    OutputB <= 16'd0;
    OutputC <= 16'd0;
    OutputD <= 16'd0;
    Status1 <= 32'd0;
    Status2 <= 32'd0;
    Status3 <= 32'd0;
end

endmodule
