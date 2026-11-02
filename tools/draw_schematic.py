#!/usr/bin/env python3
"""
draw_schematic.py
Generates a clean, simple, un-cluttered schematic for blinkfyr.
"""

import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches

fig, ax = plt.subplots(figsize=(20, 11), dpi=200)
fig.patch.set_facecolor('#ffffff')
ax.set_facecolor('#ffffff')

# Colors
COLOR_WIRE = '#1e293b'
COLOR_VCC  = '#dc2626'
COLOR_GND  = '#1e40af'
COLOR_SIG  = '#047857'

def draw_wire(pts, color=COLOR_WIRE, lw=2.2, ls='-'):
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    ax.plot(xs, ys, color=color, linewidth=lw, linestyle=ls, zorder=2)

def draw_dot(pt, color=COLOR_WIRE, s=65):
    ax.scatter([pt[0]], [pt[1]], s=s, color=color, zorder=5)

def draw_resistor(x, y, orient='h', length=1.3, label='R', val='1kΩ'):
    if orient == 'h':
        hw, hh = length / 2.0, 0.28
        ax.plot([x - hw - 0.35, x - hw], [y, y], color=COLOR_WIRE, lw=2.0, zorder=2)
        ax.plot([x + hw, x + hw + 0.35], [y, y], color=COLOR_WIRE, lw=2.0, zorder=2)
        rect = patches.Rectangle((x - hw, y - hh), length, hh*2, facecolor='#fef3c7', edgecolor='#b45309', lw=1.6, zorder=3)
        ax.add_patch(rect)
        if label:
            ax.text(x, y + 0.42, label, ha='center', va='bottom', fontsize=9.0, fontweight='bold', color='#92400e')
        ax.text(x, y, val, ha='center', va='center', fontsize=8.5, fontweight='bold', color='#1e293b')
    else:
        hw, hh = 0.28, length / 2.0
        ax.plot([x, x], [y - hh - 0.35, y - hh], color=COLOR_WIRE, lw=2.0, zorder=2)
        ax.plot([x, x], [y + hh, y + hh + 0.35], color=COLOR_WIRE, lw=2.0, zorder=2)
        rect = patches.Rectangle((x - hw, y - hh), hw*2, length, facecolor='#fef3c7', edgecolor='#b45309', lw=1.6, zorder=3)
        ax.add_patch(rect)
        txt = f"{label}\n{val}" if label else val
        ax.text(x + 0.45, y, txt, ha='left', va='center', fontsize=8.5, fontweight='bold', color='#92400e')

# Main rails
Y_VCC = 9.8
Y_GND = 1.2

# Power rails
draw_wire([(1.0, Y_VCC), (19.0, Y_VCC)], color=COLOR_VCC, lw=3.2)
ax.text(1.0, Y_VCC + 0.32, "+9V to +15V DC IN (Battery / Bench Supply)", ha='left', va='bottom', fontsize=11, fontweight='bold', color=COLOR_VCC)

draw_wire([(1.0, Y_GND), (19.0, Y_GND)], color=COLOR_GND, lw=3.2)
ax.text(1.0, Y_GND - 0.35, "COMMON GROUND (0V)", ha='left', va='top', fontsize=11, fontweight='bold', color=COLOR_GND)

# 1. Arduino Uno
ard_box = patches.FancyBboxPatch((1.6, 2.4), 3.0, 6.2, boxstyle="round,pad=0.1,rounding_size=0.2",
                                facecolor='#e0f2fe', edgecolor='#0284c7', lw=2.2, zorder=2)
ax.add_patch(ard_box)
ax.text(3.1, 7.8, "Arduino Uno\n(ATmega328P)", ha='center', va='center', fontsize=11, fontweight='bold', color='#0369a1')

# Arduino Power Pins
ax.text(2.3, 8.2, "VIN", ha='left', va='center', fontsize=9, fontweight='bold')
draw_wire([(2.3, 8.5), (2.3, Y_VCC)], color=COLOR_VCC, lw=2.0)
draw_dot((2.3, Y_VCC), color=COLOR_VCC)

ax.text(2.3, 2.8, "GND", ha='left', va='center', fontsize=9, fontweight='bold')
draw_wire([(2.3, 2.5), (2.3, Y_GND)], color=COLOR_GND, lw=2.0)
draw_dot((2.3, Y_GND), color=COLOR_GND)

# Arduino GPIO labels
ax.text(4.4, 7.4, "Pin 2", ha='right', va='center', fontsize=9, fontweight='bold')
ax.text(4.4, 5.6, "Pin 9", ha='right', va='center', fontsize=9, fontweight='bold')
ax.text(4.4, 3.6, "Pin 8", ha='right', va='center', fontsize=9, fontweight='bold')

# 2. Tactile Button on Pin 2
draw_wire([(4.6, 7.4), (5.6, 7.4)], color=COLOR_WIRE, lw=2.0)
btn_box = patches.FancyBboxPatch((5.6, 7.0), 1.0, 0.8, boxstyle="round,pad=0.05,rounding_size=0.1",
                                facecolor='#f8fafc', edgecolor='#475569', lw=1.6, zorder=3)
ax.add_patch(btn_box)
ax.text(6.1, 7.4, "SW1\nButton", ha='center', va='center', fontsize=7.5, fontweight='bold')
ax.text(6.1, 8.1, "Mode / Trigger\n(INPUT_PULLUP)", ha='center', va='bottom', fontsize=7.5, color='#475569')

draw_wire([(6.6, 7.4), (7.4, 7.4), (7.4, Y_GND)], color=COLOR_GND, lw=2.0)
draw_dot((7.4, Y_GND), color=COLOR_GND)

# 3. Piezo Buzzer on Pin 9
draw_wire([(4.6, 5.6), (5.5, 5.6)], color=COLOR_WIRE, lw=2.0)
buz_circle = patches.Circle((6.1, 5.6), 0.55, facecolor='#fee2e2', edgecolor='#b91c1c', lw=1.8, zorder=3)
ax.add_patch(buz_circle)
ax.text(6.1, 5.6, "Piezo\n4.0kHz", ha='center', va='center', fontsize=7.5, fontweight='bold', color='#991b1b')
ax.text(6.1, 6.35, "PKM22EPP-40\nSounder", ha='center', va='bottom', fontsize=7.5, color='#475569')

draw_wire([(6.65, 5.6), (7.4, 5.6)], color=COLOR_GND, lw=2.0)
draw_dot((7.4, 5.6), color=COLOR_GND)

# 4. Optocoupler Level-Shifter Stage on Pin 8
draw_wire([(4.6, 3.6), (5.3, 3.6)], color=COLOR_SIG, lw=2.2)
draw_resistor(6.1, 3.6, orient='h', length=1.2, label='R_in', val='560Ω')
draw_wire([(7.0, 3.6), (7.9, 3.6)], color=COLOR_SIG, lw=2.2)

# Optocoupler Box (LTV-4N35)
opto_box = patches.FancyBboxPatch((7.9, 2.5), 2.8, 3.8, boxstyle="round,pad=0.1,rounding_size=0.15",
                                 facecolor='#ffffff', edgecolor='#0f172a', lw=2.2, zorder=3)
ax.add_patch(opto_box)
ax.text(9.3, 6.55, "LTV-4N35 Optocoupler", ha='center', va='bottom', fontsize=9.5, fontweight='bold', color='#0f172a')
ax.text(9.3, 2.65, "(5V Logic -> Full Rail Drive)", ha='center', va='top', fontsize=7.2, color='#64748b', style='italic')

# Opto Pins & Internal graphics
# Pin 1 (Anode)
ax.text(8.1, 3.6, "1 (A)", ha='left', va='center', fontsize=8.0, fontweight='bold', color='#dc2626')
# Pin 2 (Cathode)
ax.text(8.1, 2.9, "2 (K)", ha='left', va='center', fontsize=8.0, fontweight='bold', color='#1e40af')
draw_wire([(7.9, 2.9), (7.4, 2.9)], color=COLOR_GND, lw=2.0)
draw_dot((7.4, 2.9), color=COLOR_GND)

# Internal LED
ax.plot([8.6, 8.6], [3.1, 3.5], color='#dc2626', lw=2.0, zorder=4)
tri = patches.Polygon([[8.4, 3.5], [8.8, 3.5], [8.6, 3.1]], facecolor='#fca5a5', edgecolor='#dc2626', lw=1.5, zorder=5)
ax.add_patch(tri)
ax.plot([8.35, 8.85], [3.1, 3.1], color='#dc2626', lw=2.0, zorder=4)

# Optical coupling arrows
ax.annotate("", xy=(9.4, 4.3), xytext=(8.9, 3.9), arrowprops=dict(arrowstyle="->", color='#dc2626', lw=1.6))
ax.annotate("", xy=(9.4, 3.8), xytext=(8.9, 3.4), arrowprops=dict(arrowstyle="->", color='#dc2626', lw=1.6))

# Pin 5 (Collector)
ax.text(10.5, 5.5, "5 (C)", ha='right', va='center', fontsize=8.0, fontweight='bold', color='#dc2626')
draw_wire([(10.7, 5.5), (11.2, 5.5), (11.2, Y_VCC)], color=COLOR_VCC, lw=2.0)
draw_dot((11.2, Y_VCC), color=COLOR_VCC)

# Pin 4 (Emitter)
ax.text(10.5, 3.6, "4 (E)", ha='right', va='center', fontsize=8.0, fontweight='bold', color='#047857')
# Internal phototransistor text
ax.text(9.9, 4.7, "Photo-\nNPN", ha='center', va='center', fontsize=7.5, color='#334155')

# Opto Pin 4 Output Wire to Gate Network
draw_wire([(10.7, 3.6), (11.6, 3.6)], color=COLOR_SIG, lw=2.2)

# 5. MOSFET Gate Network
draw_resistor(12.3, 3.6, orient='h', length=1.0, label='R_gate', val='220Ω')
draw_wire([(13.0, 3.6), (14.2, 3.6)], color=COLOR_WIRE, lw=2.0)
draw_dot((13.4, 3.6), color=COLOR_WIRE)

# Gate pull-down resistor
draw_wire([(13.4, 3.6), (13.4, 2.7)], color=COLOR_WIRE, lw=2.0)
draw_resistor(13.4, 2.1, orient='v', length=0.8, label='', val='10kΩ')
draw_wire([(13.4, 1.6), (13.4, Y_GND)], color=COLOR_GND, lw=2.0)
draw_dot((13.4, Y_GND), color=COLOR_GND)
ax.text(12.9, 2.1, "R_pd\n10kΩ", ha='right', va='center', fontsize=8.0, fontweight='bold', color='#92400e')

# 6. Power MOSFET (IRF520)
mos_box = patches.FancyBboxPatch((14.2, 2.4), 1.5, 2.2, boxstyle="round,pad=0.08,rounding_size=0.15",
                                facecolor='#f1f5f9', edgecolor='#1e293b', lw=2.0, zorder=3)
ax.add_patch(mos_box)
ax.text(14.95, 3.5, "IRF520\nMOSFET\n(N-Ch)", ha='center', va='center', fontsize=8.5, fontweight='bold', color='#0f172a')
ax.text(14.35, 3.6, "G", ha='left', va='center', fontsize=8.0, fontweight='bold')
ax.text(14.95, 4.4, "D", ha='center', va='bottom', fontsize=8.0, fontweight='bold')
ax.text(14.95, 2.6, "S", ha='center', va='top', fontsize=8.0, fontweight='bold')

# Source to GND
draw_wire([(14.95, 2.4), (14.95, Y_GND)], color=COLOR_GND, lw=2.2)
draw_dot((14.95, Y_GND), color=COLOR_GND)

# Drain Node
draw_wire([(14.95, 4.6), (14.95, 6.4)], color=COLOR_WIRE, lw=2.2)
draw_dot((14.95, 6.4), color=COLOR_WIRE)

# 7. Flyback Diode (1N4004) across Drain and VCC
draw_wire([(14.95, 6.4), (14.0, 6.4), (14.0, 7.3)], color=COLOR_WIRE, lw=2.0)
# Diode symbol
tri_d = patches.Polygon([[13.75, 7.3], [14.25, 7.3], [14.0, 7.8]], facecolor='#fef08a', edgecolor='#ca8a04', lw=1.5, zorder=4)
ax.add_patch(tri_d)
ax.plot([13.7, 14.3], [7.8, 7.8], color='#ca8a04', lw=2.2, zorder=5) # cathode bar
draw_wire([(14.0, 7.8), (14.0, Y_VCC)], color=COLOR_VCC, lw=2.0)
draw_dot((14.0, Y_VCC), color=COLOR_VCC)
ax.text(13.5, 7.55, "1N4004\n(Flyback)", ha='right', va='center', fontsize=7.5, fontweight='bold', color='#854d0e')

# 8. Drain Indicator LED (with 1k resistor)
draw_wire([(14.95, 6.4), (15.9, 6.4), (15.9, 6.9)], color=COLOR_WIRE, lw=2.0)
# LED symbol
tri_led = patches.Polygon([[15.65, 7.3], [16.15, 7.3], [15.9, 6.9]], facecolor='#bbf7d0', edgecolor='#15803d', lw=1.5, zorder=4)
ax.add_patch(tri_led)
ax.plot([15.6, 16.2], [6.9, 6.9], color='#15803d', lw=2.0, zorder=5) # cathode bar
draw_wire([(15.9, 7.3), (15.9, 7.8)], color=COLOR_WIRE, lw=2.0)
draw_resistor(15.9, 8.4, orient='v', length=0.8, label='', val='1kΩ')
draw_wire([(15.9, 8.9), (15.9, Y_VCC)], color=COLOR_VCC, lw=2.0)
draw_dot((15.9, Y_VCC), color=COLOR_VCC)
ax.text(16.4, 7.2, "Drain LED\n(Status)", ha='left', va='center', fontsize=7.5, fontweight='bold', color='#15803d')

# 9. Switched DC Output Jack & Load
draw_wire([(14.95, 6.4), (17.0, 6.4)], color=COLOR_WIRE, lw=2.4)
draw_wire([(17.0, Y_VCC), (17.0, 7.4)], color=COLOR_VCC, lw=2.4)
draw_dot((17.0, Y_VCC), color=COLOR_VCC)

jack_box = patches.FancyBboxPatch((16.4, 6.7), 1.2, 0.9, boxstyle="round,pad=0.04,rounding_size=0.1",
                                 facecolor='#ffffff', edgecolor='#0f172a', lw=1.8, zorder=4)
ax.add_patch(jack_box)
ax.text(17.0, 7.15, "Switched DC\nOutput Jack", ha='center', va='center', fontsize=7.5, fontweight='bold')

# External Loads Box
load_box = patches.FancyBboxPatch((16.0, 4.4), 2.8, 1.8, boxstyle="round,pad=0.08,rounding_size=0.15",
                                 facecolor='#faf5ff', edgecolor='#7e22ce', lw=1.8, zorder=3)
ax.add_patch(load_box)
ax.text(17.4, 5.8, "EXTERNAL LOADS", ha='center', va='center', fontsize=8.5, fontweight='bold', color='#7e22ce')
ax.text(17.4, 5.0, "• IR Floodlamp (~0.4A)\n• UV LepiLED (~1.1A)\n• Any 9-15V DC Load (<=5A)",
        ha='center', va='center', fontsize=7.5, color='#3b0764')

draw_wire([(17.0, 6.7), (17.0, 6.2)], color='#7e22ce', lw=2.0)

ax.set_title("blinkfyr: Schematic Diagram",
             fontsize=14.0, fontweight='bold', pad=20, color='#0f172a')

ax.set_xlim(0.0, 19.5)
ax.set_ylim(0.2, 10.8)
ax.set_aspect('equal')
ax.axis('off')

plt.tight_layout()

script_dir = os.path.dirname(os.path.abspath(__file__))
repo_root = os.path.dirname(script_dir)
out_path = os.path.join(repo_root, 'docs', 'images', 'schematic.png')
plt.savefig(out_path, dpi=200)
print(f"Saved {out_path} successfully!")
