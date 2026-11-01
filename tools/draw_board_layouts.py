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

    track_alpha = 0.35 if is_solder_side else 0.15
    track_style = '-' if is_solder_side else '--'

    def draw_track(c_pts, r_pts, color, width=15):
        xs = [col_x(c) for c in c_pts]
        ys = r_pts
        ax.plot(xs, ys, color=color, linewidth=width, linestyle=track_style,
                solid_capstyle='round', solid_joinstyle='round', alpha=track_alpha, zorder=1)

    pos_color = '#d62828'   # Red = +12V Rail
    neg_color = '#1d3557'   # Blue = Common GND (-Rail)
    strip_color = '#a86b32' # Copper = 2-Pin Strips

    # 1. POSITIVE (+12V) NETWORK:
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
            # Highlight the active strips used by the new Optocoupler addition!
            is_active_strip = (
                (r in [6, 9, 10] and (c1, c2) == (10, 11)) or
                (r in [10, 11] and (c1, c2) == (6, 7)) or
                (r == 1 and (c1, c2) == (2, 3))
            )
            if is_active_strip:
                xs = [col_x(c1), col_x(c2)]
                ax.plot(xs, [r, r], color='#b86b28', linewidth=16, linestyle=track_style,
                        solid_capstyle='round', alpha=0.70 if is_solder_side else 0.35, zorder=1.2)
            else:
                draw_track([c1, c2], [r, r], color=strip_color, width=16)

    # 4. Draw all holes
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
        ax.text(col_x(c), -0.95, "+12V", ha='center', va='center', fontsize=7.2, fontweight='bold', color='#b51724',
                bbox=dict(boxstyle='round,pad=0.10', facecolor='#ffe3e3', edgecolor='#b51724', lw=1))
    for c in [5, 9, 13]:
        ax.text(col_x(c), 16.58, "GND", ha='center', va='center', fontsize=7.2, fontweight='bold', color='#142847',
                bbox=dict(boxstyle='round,pad=0.10', facecolor='#dbe4ff', edgecolor='#142847', lw=1))

    ax.text(0.38, 0, "R0(+)", ha='center', va='center', fontsize=7.5, fontweight='bold', color='#b51724')
    for r in range(1, 16):
        ax.text(0.38, r, f"R{r}", ha='center', va='center', fontsize=8.8, fontweight='bold', color='#222222')
    ax.text(0.38, 16, "R16(-)", ha='center', va='center', fontsize=7.5, fontweight='bold', color='#142847')

    # ================= GREYED-OUT EXISTING COMPONENTS (CONTEXT ONLY) =================
    old_alpha = 0.20

    def draw_old_resistor(c1, r1, c2, r2, label):
        x1, y1 = col_x(c1), r1
        x2, y2 = col_x(c2), r2
        ax.plot([x1, x2], [y1, y2], color='#777777', linewidth=3.0, alpha=old_alpha, zorder=3)
        ax.scatter([x1, x2], [y1, y2], s=70, color='#666666', alpha=old_alpha, zorder=3)
        mx, my = (x1 + x2) / 2.0, (y1 + y2) / 2.0
        w, h = (1.85, 0.50) if abs(x2 - x1) >= abs(y2 - y1) else (0.54, 1.85)
        rect = patches.FancyBboxPatch((mx - w/2, my - h/2), w, h, boxstyle="round,pad=0.04,rounding_size=0.14",
                                      facecolor='#cccccc', edgecolor='#666666', linewidth=1.5, alpha=old_alpha, zorder=3)
        ax.add_patch(rect)
        ax.text(mx, my, label, ha='center', va='center', fontsize=6.5, color='#555555', alpha=0.45, zorder=3)

    def draw_old_jumper(c1, r1, c2, r2):
        ax.plot([col_x(c1), col_x(c2)], [r1, r2], color='#666666', linewidth=3.5, alpha=old_alpha, zorder=3)
        ax.scatter([col_x(c1), col_x(c2)], [r1, r2], s=70, color='#555555', alpha=old_alpha, zorder=3)

    # Old MOSFET
    mx = col_x(2)
    ax.add_patch(patches.FancyBboxPatch((mx - 0.42, 5.55), 0.84, 2.9, boxstyle="round,pad=0.05,rounding_size=0.1",
                                        facecolor='#666666', edgecolor='#444444', linewidth=1.5, alpha=old_alpha, zorder=3))
    ax.scatter([mx, mx, mx], [6, 7, 8], s=75, color='#888888', alpha=old_alpha, zorder=3)
    ax.text(mx, 7.0, "IRF520", ha='center', va='center', fontsize=6.5, color='#444444', alpha=0.45, rotation=90, zorder=3)

    # Old Resistors & Diode & LED
    draw_old_resistor(2, 1, 2, 4, "220Ω")
    draw_old_resistor(2, 5, 5, 5, "10kΩ")
    draw_old_resistor(6, 0, 6, 3, "1kΩ")
    draw_old_resistor(14, 2, 14, 5, "220Ω")
    draw_old_jumper(3, 8, 3, 16)
    draw_old_jumper(3, 7, 6, 7)
    draw_old_jumper(4, 8, 7, 8)
    draw_old_jumper(7, 3, 7, 6)
    draw_old_jumper(13, 9, 14, 9)
    draw_old_jumper(9, 14, 10, 14)

    # Old LED Circle
    ax.add_patch(patches.Circle((col_x(7), 4.5), 0.45, facecolor='#999999', edgecolor='#666666', alpha=old_alpha, zorder=3))
    # Old Buzzer Circle
    ax.add_patch(patches.Circle((col_x(15), 7), 2.15, facecolor='#888888', edgecolor='#555555', alpha=0.14, zorder=3))
    ax.scatter([col_x(15), col_x(15)], [5, 9], s=75, color='#777777', alpha=old_alpha, zorder=3)
    ax.text(col_x(15), 7.0, "Buzzer", ha='center', va='center', fontsize=7, color='#555555', alpha=0.40, zorder=3)
    # Old Pushbutton
    x_b1, x_b2 = min(col_x(11), col_x(14)), max(col_x(11), col_x(14))
    ax.add_patch(patches.FancyBboxPatch((x_b1 - 0.3, 11.7), 3.6, 2.6, boxstyle="round,pad=0.05,rounding_size=0.2",
                                        facecolor='#999999', edgecolor='#555555', alpha=0.16, zorder=3))
    ax.scatter([x_b1, x_b2, x_b1, x_b2], [12, 12, 14, 14], s=70, color='#777777', alpha=old_alpha, zorder=3)
    ax.text((x_b1 + x_b2)/2.0, 13.0, "Button", ha='center', va='center', fontsize=7, color='#555555', alpha=0.40, zorder=3)


    # ================= BRIGHT HIGHLIGHTED NEW OPTOCOUPLER ADDITIONS =================
    new_comp_alpha = 0.72 if is_solder_side else 1.0
    new_comp_ls = '--' if is_solder_side else '-'

    # 1. LTV-4N35 Optocoupler across Col 10 (Pins 1, 2, 3) and Col 7 (Pins 6, 5, 4) on Rows 9, 10, 11:
    # Look at how clean this is:
    # - On Component Side (Right Pane): C10 is at LEFT of chip, C7 is at RIGHT of chip!
    #   So Notch is at TOP (R9), and Pin 1 Dot is at TOP-LEFT (R9, C10)!
    #   Left pins (C10): Pin 1 (R9,C10), Pin 2 (R10,C10), Pin 3 (R11,C10).
    #   Right pins (C7): Pin 6 (R9,C7),  Pin 5 (R10,C7),  Pin 4 (R11,C7).
    # - On Solder Side (Left Pane): C7 is at LEFT of chip, C10 is at RIGHT of chip!
    #   So Pin 1 Dot is at TOP-RIGHT (R9, C10)!
    x_c7, x_c10 = col_x(7), col_x(10)
    x_left, x_right = min(x_c7, x_c10), max(x_c7, x_c10)

    opto_body = patches.FancyBboxPatch(
        (x_left + 0.35, 8.62), 2.30, 2.76,
        boxstyle="round,pad=0.05,rounding_size=0.15",
        facecolor='#ffffff', edgecolor='#111111', linewidth=2.6, linestyle=new_comp_ls, alpha=new_comp_alpha, zorder=7
    )
    ax.add_patch(opto_body)

    # Top semicircular notch at Row 8.62, centered between x_left and x_right (x = 8.5)
    notch = patches.Wedge((8.5, 8.62), 0.28, 180, 360, facecolor='#f3e5c8', edgecolor='#111111', linewidth=2.0, zorder=8)
    ax.add_patch(notch)

    # Pin 1 Red Dot near (R9, C10)!
    dot_x = (x_c10 - 0.58) if is_solder_side else (x_c10 + 0.58)
    ax.add_patch(patches.Circle((dot_x, 9.0), 0.16, facecolor='#d62828', edgecolor='black', linewidth=1.2, zorder=9))

    # Draw 6 legs & solder pads at (R9..11, C10) and (R9..11, C7)
    for r in [9, 10, 11]:
        ax.plot([x_left, x_left + 0.35], [r, r], color='#333333', linewidth=4.5, zorder=6)
        ax.plot([x_right - 0.35, x_right], [r, r], color='#333333', linewidth=4.5, zorder=6)
        ax.scatter([x_c10, x_c7], [r, r], s=130, color='#ffd166', edgecolors='#111111', linewidth=1.8, zorder=8)

    # Pin number labels inside optocoupler body
    off_c10 = -0.52 if is_solder_side else 0.52
    off_c7  = 0.52 if is_solder_side else -0.52
    ax.text(x_c10 + off_c10, 9.0,  "1", ha='center', va='center', fontsize=8.5, fontweight='bold', color='#d62828', zorder=9)
    ax.text(x_c10 + off_c10, 10.0, "2", ha='center', va='center', fontsize=8.5, fontweight='bold', color='#111111', zorder=9)
    ax.text(x_c10 + off_c10, 11.0, "3", ha='center', va='center', fontsize=8.0, fontweight='bold', color='#888888', zorder=9)
    ax.text(x_c7  + off_c7,  11.0, "4", ha='center', va='center', fontsize=8.5, fontweight='bold', color='#0f766e', zorder=9)
    ax.text(x_c7  + off_c7,  10.0, "5", ha='center', va='center', fontsize=8.5, fontweight='bold', color='#d62828', zorder=9)
    ax.text(x_c7  + off_c7,  9.0,  "6", ha='center', va='center', fontsize=8.0, fontweight='bold', color='#888888', zorder=9)

    side_note = "(Pin 1 Dot TOP-RIGHT)" if is_solder_side else "(Pin 1 Dot TOP-LEFT)"
    ax.text(8.5, 10.0, f"LTV-4N35\n{side_note}", ha='center', va='center', fontsize=7.5, fontweight='bold', color='#111111', zorder=9)

    # 2. NEW 560 Ohm (or 1k Ohm) Opto LED Resistor:
    # From (R6, C11) to (R9, C11) [spans 2 empty holes: R7,C11 & R8,C11!]
    x_c11 = col_x(11)
    ax.plot([x_c11, x_c11], [6, 9], color='#222222', linewidth=4.0, linestyle=new_comp_ls, alpha=new_comp_alpha, zorder=6)
    ax.scatter([x_c11, x_c11], [6, 9], s=120, color='#111111', edgecolors='white', linewidth=1.2, zorder=7)
    res_rect = patches.FancyBboxPatch(
        (x_c11 - 0.32, 6.58), 0.64, 1.84,
        boxstyle="round,pad=0.04,rounding_size=0.14",
        facecolor='#a7f3d0', edgecolor='#065f46', linewidth=2.4, linestyle=new_comp_ls, alpha=new_comp_alpha, zorder=8
    )
    ax.add_patch(res_rect)
    ax.text(x_c11, 7.5, "NEW\n560Ω\n(or 1kΩ)", ha='center', va='center', fontsize=7.2, fontweight='bold', color='#064e3b', zorder=9)

    # 3. NEW Jumper: Opto Pin 2 (R10, C11) -> GND Rail (R10, C13)
    x_c13 = col_x(13)
    ax.plot([x_c11, x_c13], [10, 10], color='#1d3557', linewidth=5.0, linestyle=new_comp_ls, alpha=new_comp_alpha, zorder=6)
    ax.scatter([x_c11, x_c13], [10, 10], s=120, color='#1d3557', edgecolors='white', linewidth=1.2, zorder=7)
    ax.text((x_c11 + x_c13)/2.0, 10.52, "NEW: Opto->GND\n(R10,C11 to R10,C13)", ha='center', va='top', fontsize=7.2, fontweight='bold',
            color='#1d3557', bbox=dict(boxstyle='round,pad=0.14', facecolor='#dbe4ff', edgecolor='#1d3557', lw=1.2), zorder=9)

    # 4. NEW Jumper: Opto Pin 5 (R10, C6) -> +12V Rail (R10, C4)
    x_c6, x_c4 = col_x(6), col_x(4)
    ax.plot([x_c6, x_c4], [10, 10], color='#d62828', linewidth=5.0, linestyle=new_comp_ls, alpha=new_comp_alpha, zorder=6)
    ax.scatter([x_c6, x_c4], [10, 10], s=120, color='#d62828', edgecolors='white', linewidth=1.2, zorder=7)
    ax.text((x_c6 + x_c4)/2.0, 10.52, "NEW: Opto +12V\n(R10,C6 to R10,C4)", ha='center', va='top', fontsize=7.2, fontweight='bold',
            color='#b51724', bbox=dict(boxstyle='round,pad=0.14', facecolor='#ffe3e3', edgecolor='#b51724', lw=1.2), zorder=9)

    # 5. Repurposed Wire: Connect existing (R1, C3) wire into (R11, C6) [Opto Pin 4 +12V Output]!
    x_c3 = col_x(3)
    rad_val = 0.35 if is_solder_side else -0.35
    ax.annotate(
        "", xy=(x_c3, 1), xytext=(x_c6, 11),
        arrowprops=dict(arrowstyle="->", color='#0f766e', lw=3.8, linestyle='-', connectionstyle=f"arc3,rad={rad_val}"),
        zorder=10
    )
    ax.scatter([x_c3, x_c6], [1, 11], s=130, color='#0f766e', edgecolors='white', linewidth=1.5, zorder=10)
    lbl_x = 3.2 if is_solder_side else (17 - 3.2)
    ax.text(lbl_x, 12.6, "MOVE EXISTING (R1,C3) WIRE:\nSolder free end into (R11, C6)\n(Sends +12V to MOSFET Gate!)",
            ha='center', va='center', fontsize=8.0, fontweight='bold', color='white',
            bbox=dict(boxstyle='round,pad=0.25', facecolor='#0f766e', edgecolor='#111111', lw=1.5), zorder=11)

    # 6. NEW Arduino Pin 8 Wire at (R6, C10):
    x_c10 = col_x(10)
    ax.plot([x_c10, x_c10], [6, -1.65], color='#2a9d8f', linewidth=4.0, zorder=10)
    ax.scatter([x_c10], [6], s=130, color='#2a9d8f', edgecolors='white', linewidth=1.5, zorder=11)
    ax.text(x_c10, -1.75, "NEW: Arduino Pin 8 Wire\nSolder into (R6, C10)", ha='center', va='center',
            fontsize=8.5, fontweight='bold', color='white',
            bbox=dict(boxstyle='round,pad=0.28', facecolor='#2a9d8f', edgecolor='#111111', lw=1.5), zorder=11)

    if is_solder_side:
        ax.set_title("1. SOLDER / TRACE SIDE (Where You Apply Solder)\n"
                     "C1 on LEFT ---> C16 on RIGHT  |  Optocoupler Pin 1 Dot is at TOP-RIGHT (R9, C10)",
                     fontsize=12.5, fontweight='bold', pad=24, color='#7c2d12')
    else:
        ax.set_title("2. COMPONENT SIDE (Where You Insert Optocoupler & Resistor)\n"
                     "C16 on LEFT <--- C1 on RIGHT  |  Optocoupler Pin 1 Dot is at TOP-LEFT (R9, C10)",
                     fontsize=12.5, fontweight='bold', pad=24, color='#1e3a8a')

    ax.set_xlim(-2.2, 19.2)
    ax.set_ylim(18.0, -2.6)
    ax.set_aspect('equal')
    ax.axis('off')

draw_board_pane(ax_solder, is_solder_side=True)
draw_board_pane(ax_comp, is_solder_side=False)

plt.suptitle("Step 3 Final Guide: Adding the LTV-4N35 Optocoupler (+12V Gate Booster) — Both Sides",
             fontsize=15.5, fontweight='bold', y=0.98)
plt.tight_layout(rect=[0, 0, 1, 0.95])
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
repo_root = os.path.dirname(script_dir)
out_path = os.path.join(repo_root, 'docs', 'images', 'optocoupler_addition_both_sides.png')
plt.savefig(out_path, dpi=180)
print(f"Saved {out_path} successfully!")
