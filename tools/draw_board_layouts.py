#!/usr/bin/env python3
"""
draw_board_layouts.py
Generates the canonical dual-pane board layout for Blinkfyr on the Jaycar HP9556 perfboard:
- Pane 1: Solder / Trace Side (Copper tracks facing up, C1 left -> C16 right)
- Pane 2: Component Side (Component bodies facing up, C16 left <- C1 right)
"""

import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches

fig, (ax_solder, ax_comp) = plt.subplots(1, 2, figsize=(24, 15.5), dpi=180)
fig.patch.set_facecolor('#ffffff')

def draw_board_pane(ax, is_solder_side=True):
    bg_color = '#ede0c8' if is_solder_side else '#f6efe0'
    ax.set_facecolor('#ffffff')

    board_rect = patches.FancyBboxPatch(
        (0.1, -1.3), 16.8, 18.8,
        boxstyle="round,pad=0.2,rounding_size=0.4",
        facecolor=bg_color, edgecolor='#b5945b', linewidth=3, zorder=0
    )
    ax.add_patch(board_rect)

    # Corner mounting holes
    for mx in [0.8, 16.2]:
        for my in [-0.6, 16.7]:
            ax.add_patch(patches.Circle((mx, my), 0.38, facecolor='white', edgecolor='#a38756', linewidth=1.8, zorder=1))

    def col_x(c):
        return c if is_solder_side else (17 - c)

    track_alpha = 0.40 if is_solder_side else 0.15
    track_style = '-' if is_solder_side else '--'

    def draw_track(c_pts, r_pts, color, width=15):
        xs = [col_x(c) for c in c_pts]
        ys = r_pts
        ax.plot(xs, ys, color=color, linewidth=width, linestyle=track_style,
                solid_capstyle='round', solid_joinstyle='round', alpha=track_alpha, zorder=1)

    pos_color = '#d62828'   # Red = +9V to +15V DC Rail
    neg_color = '#1d3557'   # Blue = Common GND (-Rail)
    strip_color = '#a86b32' # Copper = 2-Pin Strips

    # 1. POSITIVE POWER NETWORK:
    draw_track([2, 15], [0, 0], color=pos_color, width=16)
    draw_track([2, 1, 1], [0, 0.4, 16], color=pos_color, width=16)
    draw_track([15, 16, 16], [0, 0.4, 16], color=pos_color, width=16)
    for c in [4, 8, 12]:
        draw_track([c, c], [0, 15], color=pos_color, width=16)

    # 2. NEGATIVE (GND) NETWORK:
    draw_track([2, 15], [16, 16], color=neg_color, width=16)
    for c in [5, 9, 13]:
        draw_track([c, c], [1, 16], color=neg_color, width=16)

    # 3. 2-PIN HORIZONTAL STRIPS (R1..R15):
    for r in range(1, 16):
        for (c1, c2) in [(2, 3), (6, 7), (10, 11), (14, 15)]:
            draw_track([c1, c2], [r, r], color=strip_color, width=16)

    # 4. Draw all board holes
    for c in range(2, 16):
        ax.add_patch(patches.Circle((col_x(c), 0), 0.21, facecolor='#faf6ee', edgecolor='#aaaaaa', linewidth=1.1, zorder=2))
    for r in range(1, 16):
        for c in range(1, 17):
            if c in [1, 4, 8, 12, 16]:
                edge = '#c97a7e'
            elif c in [5, 9, 13]:
                edge = '#748cab'
            else:
                edge = '#999999'
            ax.add_patch(patches.Circle((col_x(c), r), 0.21, facecolor='#faf6ee', edgecolor=edge, linewidth=1.1, zorder=2))
    for c in [1, 16]:
        ax.add_patch(patches.Circle((col_x(c), 16), 0.21, facecolor='#faf6ee', edgecolor='#c97a7e', linewidth=1.2, zorder=2))
    for c in range(2, 16):
        ax.add_patch(patches.Circle((col_x(c), 16), 0.21, facecolor='#faf6ee', edgecolor='#748cab', linewidth=1.1, zorder=2))

    # Column & Row Labels
    for c in range(1, 17):
        ax.text(col_x(c), -0.52, f"C{c}", ha='center', va='center', fontsize=8.8, fontweight='bold', color='#222222')
    for c in [1, 4, 8, 12, 16]:
        ax.text(col_x(c), -0.95, "+DC", ha='center', va='center', fontsize=7.2, fontweight='bold', color='#b51724',
                bbox=dict(boxstyle='round,pad=0.10', facecolor='#ffe3e3', edgecolor='#b51724', lw=1))
    for c in [5, 9, 13]:
        ax.text(col_x(c), 16.58, "GND", ha='center', va='center', fontsize=7.2, fontweight='bold', color='#142847',
                bbox=dict(boxstyle='round,pad=0.10', facecolor='#dbe4ff', edgecolor='#142847', lw=1))

    ax.text(0.38, 0, "R0(+)", ha='center', va='center', fontsize=7.5, fontweight='bold', color='#b51724')
    for r in range(1, 16):
        ax.text(0.38, r, f"R{r}", ha='center', va='center', fontsize=8.8, fontweight='bold', color='#222222')
    ax.text(0.38, 16, "R16(-)", ha='center', va='center', fontsize=7.5, fontweight='bold', color='#142847')

    # Styling for components
    comp_alpha = 0.55 if is_solder_side else 1.0
    comp_ls = '--' if is_solder_side else '-'

    # Helper: Resistors
    def draw_resistor(c1, r1, c2, r2, label, color='#fef3c7', border='#b45309'):
        x1, y1 = col_x(c1), r1
        x2, y2 = col_x(c2), r2
        ax.plot([x1, x2], [y1, y2], color='#333333', linewidth=3.2, linestyle=comp_ls, alpha=comp_alpha, zorder=4)
        ax.scatter([x1, x2], [y1, y2], s=80, color='#333333', alpha=comp_alpha, zorder=5)
        mx, my = (x1 + x2) / 2.0, (y1 + y2) / 2.0
        w, h = (1.85, 0.52) if abs(x2 - x1) >= abs(y2 - y1) else (0.52, 1.85)
        rect = patches.FancyBboxPatch((mx - w/2, my - h/2), w, h, boxstyle="round,pad=0.04,rounding_size=0.14",
                                      facecolor=color, edgecolor=border, linewidth=1.8, linestyle=comp_ls, alpha=comp_alpha, zorder=5)
        ax.add_patch(rect)
        ax.text(mx, my, label, ha='center', va='center', fontsize=7.2, fontweight='bold', color='#1e293b', alpha=comp_alpha, zorder=6)

    # Helper: Jumpers
    def draw_jumper(c1, r1, c2, r2, color='#0284c7'):
        x1, x2 = col_x(c1), col_x(c2)
        ax.plot([x1, x2], [r1, r2], color=color, linewidth=4.0, linestyle=comp_ls, alpha=comp_alpha, zorder=4)
        ax.scatter([x1, x2], [r1, r2], s=80, color=color, edgecolors='white', linewidth=1.2, alpha=comp_alpha, zorder=5)

    # 1. MOSFET (IRF520) in Column 2 (Rows 6, 7, 8)
    mx = col_x(2)
    # Heatsink tab
    tab_x = (mx - 0.50) if is_solder_side else (mx + 0.32)
    ax.add_patch(patches.Rectangle((tab_x, 5.6), 0.18, 2.8, facecolor='#94a3b8', edgecolor='#475569', lw=1.2,
                                   linestyle=comp_ls, alpha=comp_alpha, zorder=4))
    # Plastic body
    body_x = (mx - 0.32) if is_solder_side else (mx - 0.50)
    ax.add_patch(patches.FancyBboxPatch((body_x, 5.6), 0.64, 2.8, boxstyle="round,pad=0.04,rounding_size=0.1",
                                        facecolor='#1e293b', edgecolor='#0f172a', lw=1.8, linestyle=comp_ls, alpha=comp_alpha, zorder=5))
    ax.scatter([mx, mx, mx], [6, 7, 8], s=85, color='#ffd166', edgecolors='#1e293b', lw=1.5, zorder=6)
    ax.text(mx, 7.0, "IRF520", ha='center', va='center', fontsize=7.0, fontweight='bold', color='white',
            rotation=90, alpha=comp_alpha, zorder=7)

    # 2. Gate Resistors
    draw_resistor(2, 1, 2, 4, "220Ω\nR_gate")
    draw_resistor(2, 5, 5, 5, "10kΩ\nR_pd")

    # 3. Drain Monitoring LED & Resistor
    draw_resistor(6, 0, 6, 3, "1kΩ\nR_led")
    # LED
    led_x = col_x(7)
    ax.add_patch(patches.Circle((led_x, 4.5), 0.42, facecolor='#4ade80', edgecolor='#15803d', lw=1.8,
                                linestyle=comp_ls, alpha=comp_alpha, zorder=5))
    ax.text(led_x, 4.5, "LED", ha='center', va='center', fontsize=6.8, fontweight='bold', color='#14532d', alpha=comp_alpha, zorder=6)
    draw_jumper(7, 3, 7, 4, color='#15803d')

    # 4. Flyback Diode (1N4004) across (R8, C4) to (R8, C7)
    d_x1, d_x2 = col_x(4), col_x(7)
    ax.plot([d_x1, d_x2], [8, 8], color='#333333', lw=3.2, linestyle=comp_ls, alpha=comp_alpha, zorder=4)
    ax.scatter([d_x1, d_x2], [8, 8], s=80, color='#333333', zorder=5)
    d_mx = (d_x1 + d_x2) / 2.0
    ax.add_patch(patches.FancyBboxPatch((d_mx - 0.7, 7.7), 1.4, 0.6, boxstyle="round,pad=0.04,rounding_size=0.12",
                                        facecolor='#fef08a', edgecolor='#ca8a04', lw=1.6, linestyle=comp_ls, alpha=comp_alpha, zorder=5))
    ax.text(d_mx, 8.0, "1N4004", ha='center', va='center', fontsize=7.0, fontweight='bold', color='#854d0e', alpha=comp_alpha, zorder=6)

    # 5. Piezo Buzzer (PKM22EPP-40) in Column 15 (Rows 5 & 9)
    bx = col_x(15)
    ax.add_patch(patches.Circle((bx, 7.0), 2.15, facecolor='#fee2e2', edgecolor='#b91c1c', lw=2.0,
                                linestyle=comp_ls, alpha=0.35 if is_solder_side else 0.70, zorder=4))
    ax.scatter([bx, bx], [5, 9], s=90, color='#b91c1c', edgecolors='white', lw=1.4, zorder=5)
    ax.text(bx, 7.0, "PKM22EPP-40\nPiezo Buzzer\n(4.0 kHz)", ha='center', va='center', fontsize=7.5,
            fontweight='bold', color='#991b1b', alpha=comp_alpha, zorder=6)
    draw_jumper(14, 2, 14, 5, color='#b91c1c')
    draw_jumper(13, 9, 14, 9, color='#1e40af')

    # 6. Tactile Button across C11..C14 (Rows 12..14)
    btn_x1, btn_x2 = min(col_x(11), col_x(14)), max(col_x(11), col_x(14))
    ax.add_patch(patches.FancyBboxPatch((btn_x1 - 0.3, 11.7), 3.6, 2.6, boxstyle="round,pad=0.05,rounding_size=0.2",
                                        facecolor='#f1f5f9', edgecolor='#475569', lw=1.8, linestyle=comp_ls, alpha=comp_alpha, zorder=4))
    ax.scatter([btn_x1, btn_x2, btn_x1, btn_x2], [12, 12, 14, 14], s=80, color='#475569', edgecolors='white', lw=1.2, zorder=5)
    ax.text((btn_x1 + btn_x2)/2.0, 13.0, "Mode / Sync\nButton", ha='center', va='center', fontsize=8.0,
            fontweight='bold', color='#1e293b', alpha=comp_alpha, zorder=6)
    draw_jumper(9, 14, 10, 14, color='#1e40af')

    # 7. Drain Output Jumpers & Return
    draw_jumper(3, 8, 3, 16, color='#1e40af') # Source to GND
    draw_jumper(3, 7, 6, 7, color='#7c3aed')  # Drain to DC Jack

    # 8. LTV-4N35 Optocoupler across C10 and C7 (Rows 9..11)
    x_c7, x_c10 = col_x(7), col_x(10)
    x_left, x_right = min(x_c7, x_c10), max(x_c7, x_c10)

    opto_body = patches.FancyBboxPatch(
        (x_left + 0.35, 8.62), 2.30, 2.76,
        boxstyle="round,pad=0.05,rounding_size=0.15",
        facecolor='#ffffff', edgecolor='#0f172a', linewidth=2.4, linestyle=comp_ls, alpha=comp_alpha, zorder=7
    )
    ax.add_patch(opto_body)

    # Top notch
    notch = patches.Wedge((8.5, 8.62), 0.28, 180, 360, facecolor='#f3e5c8', edgecolor='#0f172a', linewidth=2.0, zorder=8)
    ax.add_patch(notch)

    # Pin 1 Dot
    dot_x = (x_c10 - 0.58) if is_solder_side else (x_c10 + 0.58)
    ax.add_patch(patches.Circle((dot_x, 9.0), 0.16, facecolor='#d62828', edgecolor='black', linewidth=1.2, zorder=9))

    # Opto legs
    for r in [9, 10, 11]:
        ax.plot([x_left, x_left + 0.35], [r, r], color='#333333', linewidth=4.0, zorder=6)
        ax.plot([x_right - 0.35, x_right], [r, r], color='#333333', linewidth=4.0, zorder=6)
        ax.scatter([x_c10, x_c7], [r, r], s=120, color='#ffd166', edgecolors='#0f172a', linewidth=1.6, zorder=8)

    # Opto Pin Labels
    off_c10 = -0.52 if is_solder_side else 0.52
    off_c7  = 0.52 if is_solder_side else -0.52
    ax.text(x_c10 + off_c10, 9.0,  "1", ha='center', va='center', fontsize=8.5, fontweight='bold', color='#d62828', zorder=9)
    ax.text(x_c10 + off_c10, 10.0, "2", ha='center', va='center', fontsize=8.5, fontweight='bold', color='#1e40af', zorder=9)
    ax.text(x_c10 + off_c10, 11.0, "3", ha='center', va='center', fontsize=8.0, fontweight='bold', color='#94a3b8', zorder=9)
    ax.text(x_c7  + off_c7,  11.0, "4", ha='center', va='center', fontsize=8.5, fontweight='bold', color='#059669', zorder=9)
    ax.text(x_c7  + off_c7,  10.0, "5", ha='center', va='center', fontsize=8.5, fontweight='bold', color='#dc2626', zorder=9)
    ax.text(x_c7  + off_c7,  9.0,  "6", ha='center', va='center', fontsize=8.0, fontweight='bold', color='#94a3b8', zorder=9)

    ax.text(8.5, 10.0, "LTV-4N35\nOptocoupler", ha='center', va='center', fontsize=7.5, fontweight='bold', color='#0f172a', zorder=9)

    # 9. Opto Input Resistor (560 Ohm / 1.0k)
    draw_resistor(11, 6, 11, 9, "560Ω\nR_in", color='#a7f3d0', border='#059669')

    # 10. Opto Jumpers:
    # Pin 2 (R10, C11) to GND Rail (R10, C13)
    draw_jumper(11, 10, 13, 10, color='#1e40af')
    # Pin 5 (R10, C6) to +DC Rail (R10, C4)
    draw_jumper(6, 10, 4, 10, color='#dc2626')

    # 11. Opto Output Pin 4 to Gate Node (R11, C6 to R1, C3)
    x_c3, x_c6 = col_x(3), col_x(6)
    rad_val = 0.35 if is_solder_side else -0.35
    ax.annotate(
        "", xy=(x_c3, 1), xytext=(x_c6, 11),
        arrowprops=dict(arrowstyle="->", color='#059669', lw=3.5, linestyle='-', connectionstyle=f"arc3,rad={rad_val}"),
        zorder=10
    )
    ax.scatter([x_c3, x_c6], [1, 11], s=120, color='#059669', edgecolors='white', linewidth=1.5, zorder=10)

    # 12. External Flying Leads (Arduino & DC Jack)
    # Arduino Pin 8 Input Wire at (R6, C10)
    x_c10 = col_x(10)
    ax.plot([x_c10, x_c10], [6, -1.65], color='#2a9d8f', linewidth=3.5, zorder=10)
    ax.scatter([x_c10], [6], s=120, color='#2a9d8f', edgecolors='white', linewidth=1.5, zorder=11)
    ax.text(x_c10, -1.75, "Arduino Pin 8\n(Sync Signal)", ha='center', va='center',
            fontsize=8.5, fontweight='bold', color='white',
            bbox=dict(boxstyle='round,pad=0.25', facecolor='#2a9d8f', edgecolor='#111111', lw=1.5), zorder=11)

    # Underside Solder Bridges (Shown primarily on Solder Side)
    if is_solder_side:
        # Bridge #1: (R4, C2) to (R6, C2)
        ax.plot([col_x(2), col_x(2)], [4, 6], color='#eab308', lw=7.0, zorder=7)
        ax.text(col_x(2) + 0.55, 5.0, "Bridge #1\n(Gate Bus)", ha='left', va='center', fontsize=6.8, fontweight='bold', color='#854d0e')

        # Bridge #2: (R6, C6) to (R8, C6)
        ax.plot([col_x(6), col_x(6)], [6, 8], color='#eab308', lw=7.0, zorder=7)
        ax.text(col_x(6) - 0.55, 7.0, "Bridge #2\n(Drain Bus)", ha='right', va='center', fontsize=6.8, fontweight='bold', color='#854d0e')

    if is_solder_side:
        ax.set_title("1. SOLDER / TRACE SIDE (Where You Apply Solder)\n"
                     "C1 on LEFT ---> C16 on RIGHT  |  Optocoupler Pin 1 Dot is at TOP-RIGHT (R9, C10)",
                     fontsize=12.5, fontweight='bold', pad=24, color='#7c2d12')
    else:
        ax.set_title("2. COMPONENT SIDE (Where You Insert Components)\n"
                     "C16 on LEFT <--- C1 on RIGHT  |  Optocoupler Pin 1 Dot is at TOP-LEFT (R9, C10)",
                     fontsize=12.5, fontweight='bold', pad=24, color='#1e3a8a')

    ax.set_xlim(-2.2, 19.2)
    ax.set_ylim(18.0, -2.6)
    ax.set_aspect('equal')
    ax.axis('off')

draw_board_pane(ax_solder, is_solder_side=True)
draw_board_pane(ax_comp, is_solder_side=False)

plt.suptitle("blinkfyr: Complete Dual-Pane Perfboard Layout (Jaycar HP9556)",
             fontsize=15.5, fontweight='bold', y=0.98)
plt.tight_layout(rect=[0, 0, 1, 0.95])

script_dir = os.path.dirname(os.path.abspath(__file__))
repo_root = os.path.dirname(script_dir)
out_path = os.path.join(repo_root, 'docs', 'images', 'board_layout_both_sides.png')
plt.savefig(out_path, dpi=180)
print(f"Saved {out_path} successfully!")
