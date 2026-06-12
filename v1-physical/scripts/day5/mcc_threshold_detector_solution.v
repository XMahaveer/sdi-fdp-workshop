`timescale 1ns/1ps

// ========================================================================
// Moku Custom Instrument (MCC) — Threshold Detector SOLUTION
// 5-Day SDI Lab Automation FDP (v2.0) — Day 5 MCC Session
// TRAINER REFERENCE — do not distribute to participants
//
//   - Reads analog InputA (16-bit signed Q1.15, 125 MSa/s)
//   - Compares to threshold from Python (Control0, Q1.15 in low 16 bits)
//   - OutputA = +1.0 V while above threshold, 0 V otherwise
//   - Status0 = threshold crossings per second (rising crossings)
//
// Architecture follows the validated ASK_Modulator_Demodulator.v
// pattern: full fixed port list, Control defaults, single clocked block.
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
// Control register mapping with default
// Default threshold: 0x2000 = 8192 = 0.25 of full scale (~0.25 V)
// ========================================================================
wire signed [15:0] threshold = (Control0[15:0] == 0) ? 16'sh2000
                                                     : Control0[15:0];

// ========================================================================
// SOLUTION 1 — Comparator: signed Q1.15 comparison
// ========================================================================
wire above = ($signed(InputA) > threshold);

// ========================================================================
// Crossing detector: rising edge of 'above'
// ========================================================================
reg above_prev;
wire crossing = above & ~above_prev;

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

        // SOLUTION 2 — Output driver: full scale while above threshold
        if (above)
            OutputA <= 16'sh7FFF;        // +1.0 V (Q1.15 full scale)
        else
            OutputA <= 16'd0;            // 0 V

        // SOLUTION 3 — Crossings-per-second counter
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
    end
end

// Tie off unused outputs
always @(posedge Clk) begin
    OutputB <= 16'd0;
    OutputC <= 16'd0;
    OutputD <= 16'd0;
    Status1 <= 32'd0;
    Status2 <= 32'd0;
    Status3 <= 32'd0;
end

endmodule
