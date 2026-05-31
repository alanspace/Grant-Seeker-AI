"""
Generate updated architecture diagram for Grant Seeker AI.
Reflects current implementation as of April 2026.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

# ── colour palette ─────────────────────────────────────────────────────────
BG_MAIN      = "#EDE7F6"   # lavender page background
BG_FRONTEND  = "#FFFFFF"   # white panel
BG_BACKEND   = "#FFFFFF"   # white panel
BG_PHASE3    = "#FFFFFF"   # white panel

C_UI         = "#1565C0"   # dark blue  – Streamlit / UI boxes
C_WORKFLOW   = "#F57F17"   # amber      – GrantSeekerWorkflow
C_AGENT      = "#2E7D32"   # dark green – ADK agents
C_MODEL      = "#6A1B9A"   # purple     – Gemini / external AI
C_EXTERNAL   = "#6A1B9A"   # purple     – Tavily / Google CSE
C_FILTER     = "#00695C"   # teal       – filters.py layer
C_EXTRACT    = "#4527A0"   # deep purple – content_extractor chain
C_CACHE      = "#37474F"   # blue-grey  – file cache / pdf
C_POST       = "#BF360C"   # deep orange – post-processing
C_ARROW      = "#37474F"
C_LABEL      = "#37474F"

WHITE = "#FFFFFF"
BLACK = "#000000"

# ── helpers ────────────────────────────────────────────────────────────────
def box(ax, x, y, w, h, color, text, fontsize=8.5, text_color=WHITE,
        style="round,pad=0.05", lw=1.5, linestyle="-",
        edge_color=None, alpha=1.0, dashed=False):
    ec = edge_color or color
    ls = "--" if dashed else linestyle
    p = FancyBboxPatch((x, y), w, h,
                       boxstyle=style,
                       linewidth=lw, linestyle=ls,
                       edgecolor=ec, facecolor=color,
                       alpha=alpha, zorder=3)
    ax.add_patch(p)
    ax.text(x + w / 2, y + h / 2, text,
            ha="center", va="center", fontsize=fontsize,
            color=text_color, fontweight="bold", zorder=4,
            wrap=True, multialignment="center")

def ghost(ax, x, y, w, h, color, text, fontsize=8.5,
          lw=1.5, dashed=True):
    """Dashed-border box (external / AI model style)."""
    ls = "--" if dashed else "-"
    p = FancyBboxPatch((x, y), w, h,
                       boxstyle="round,pad=0.05",
                       linewidth=lw, linestyle=ls,
                       edgecolor=color, facecolor=WHITE,
                       alpha=1.0, zorder=3)
    ax.add_patch(p)
    ax.text(x + w / 2, y + h / 2, text,
            ha="center", va="center", fontsize=fontsize,
            color=color, fontweight="bold", zorder=4,
            multialignment="center")

def panel(ax, x, y, w, h, label, label_color="#555555", bg="#FAFAFA",
          edge="#CCCCCC", fontsize=8):
    p = mpatches.FancyBboxPatch((x, y), w, h,
                                boxstyle="round,pad=0.1",
                                linewidth=1.2, linestyle="-",
                                edgecolor=edge, facecolor=bg,
                                alpha=0.55, zorder=1)
    ax.add_patch(p)
    ax.text(x + 0.15, y + h - 0.18, label,
            ha="left", va="top", fontsize=fontsize,
            color=label_color, fontstyle="italic", zorder=2)

def arrow(ax, x1, y1, x2, y2, label="", color=C_ARROW, lw=1.3,
          arrowstyle="-|>", connectionstyle="arc3,rad=0.0",
          fontsize=7.5):
    ax.annotate("",
                xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle=arrowstyle,
                                color=color, lw=lw,
                                connectionstyle=connectionstyle),
                zorder=5)
    if label:
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        ax.text(mx, my, label, ha="center", va="bottom",
                fontsize=fontsize, color=C_LABEL, zorder=6)

def cylinder(ax, x, y, w, h, color, text, fontsize=8):
    """Rough cylinder using patches (top ellipse + rect + bottom ellipse)."""
    ew, eh = w, 0.22
    rect = mpatches.FancyBboxPatch((x, y), w, h,
                                   boxstyle="square,pad=0",
                                   linewidth=1.2, edgecolor=color,
                                   facecolor="#ECEFF1", zorder=3)
    ax.add_patch(rect)
    top = mpatches.Ellipse((x + w/2, y + h), w/2, eh,
                            linewidth=1.2, edgecolor=color,
                            facecolor="#CFD8DC", zorder=4)
    bot = mpatches.Ellipse((x + w/2, y), w/2, eh,
                            linewidth=1.2, edgecolor=color,
                            facecolor="#ECEFF1", zorder=4)
    ax.add_patch(top); ax.add_patch(bot)
    ax.text(x + w/2, y + h/2, text,
            ha="center", va="center", fontsize=fontsize,
            color=color, fontweight="bold", zorder=5,
            multialignment="center")

# ── canvas ─────────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(17, 25))
ax.set_xlim(0, 17); ax.set_ylim(0, 25)
ax.set_aspect("equal"); ax.axis("off")
fig.patch.set_facecolor(BG_MAIN)
ax.set_facecolor(BG_MAIN)

# ══════════════════════════════════════════════════════════════════════════
# PANEL 1 – FRONTEND LAYER
# ══════════════════════════════════════════════════════════════════════════
panel(ax, 0.4, 17.2, 16.2, 5.6, "[FE]  Frontend Layer",
      label_color="#1A237E", bg="#E8EAF6", edge="#9FA8DA")

# User
box(ax, 7.5, 21.7, 2.0, 0.85, C_UI, "USER", fontsize=9)

# Streamlit App
box(ax, 5.5, 20.1, 6.0, 1.2, C_UI,
    "Streamlit Multi-Page App\n"
    "Search  |  Details  |  Proposals  |  Diagnostics",
    fontsize=8.5)

# Filter panel (inside frontend)
box(ax, 1.0, 17.6, 9.0, 1.9, C_FILTER,
    "Advanced Filters  (filters.py  --  apply_filters_to_results)\n"
    "Demographics  *  Amount Range  *  Funding Type\n"
    "Geography  *  Applicant Type  *  Project Stage",
    fontsize=8.0, style="round,pad=0.08")

# PDF Export
ghost(ax, 11.0, 17.6, 3.8, 0.9, C_CACHE,
      "PDF Export\npdf_generator.py", fontsize=8)

# Arrows – frontend flow
arrow(ax, 8.5, 21.7, 8.5, 21.3, label="1. Project\nDescription", fontsize=7)
arrow(ax, 8.5, 20.1, 8.5, 19.5, label="2. Trigger", fontsize=7)
arrow(ax, 10.8, 20.7, 12.0, 18.6, label="Export", fontsize=7,
      connectionstyle="arc3,rad=-0.2")
arrow(ax, 5.5, 20.4, 2.5, 19.6, label="", fontsize=7,
      connectionstyle="arc3,rad=0.15")

# ══════════════════════════════════════════════════════════════════════════
# PANEL 2 – BACKEND ORCHESTRATION
# ══════════════════════════════════════════════════════════════════════════
panel(ax, 3.0, 6.2, 13.5, 10.8, "[BE]  Backend Orchestration (ADK)",
      label_color="#1B5E20", bg="#E8F5E9", edge="#A5D6A7")

# GrantSeekerWorkflow
box(ax, 6.0, 15.3, 5.0, 1.1, C_WORKFLOW,
    "GrantSeekerWorkflow\nrun_with_minimum_results()  —  5-attempt loop",
    fontsize=8.5, text_color=BLACK)

# From filters → workflow
arrow(ax, 5.5, 18.3, 8.5, 16.4, label="3. Filters +\nbusiness context",
      fontsize=7, connectionstyle="arc3,rad=0.0")

# QueryGenerator
box(ax, 5.8, 13.5, 5.4, 1.0, C_AGENT, "QueryGenerator Agent\nOptimises search keywords", fontsize=8)
arrow(ax, 8.5, 15.3, 8.5, 14.5, label="Start", fontsize=7)

# GrantFinder
box(ax, 5.8, 11.5, 5.4, 1.0, C_AGENT, "GrantFinder Agent\nSelects top 5-7 leads", fontsize=8)
arrow(ax, 8.5, 13.5, 8.5, 12.5, label="Optimised\nKeywords", fontsize=7)

# GrantExtractor
box(ax, 5.8, 9.0, 5.4, 1.2, C_AGENT, "GrantExtractor Agent\nasyncio Semaphore(3) parallel", fontsize=8)
arrow(ax, 8.5, 11.5, 8.5, 10.2, label="URLs", fontsize=7)

# Content extraction strategy chain
box(ax, 3.5, 6.7, 9.5, 1.7, C_EXTRACT,
    "Content Extractor  —  4-strategy fallback chain  (content_extractor.py)\n"
    "① Tavily Extract  →  ② Google Scraper  →  ③ PDF Parser (pypdf)  →  ④ BeautifulSoup",
    fontsize=7.8, style="round,pad=0.08")
arrow(ax, 8.5, 9.0, 8.5, 8.4, label="Fetch\ncontent", fontsize=7)

# Search providers — alongside GrantFinder
ghost(ax, 12.5, 11.2, 3.2, 1.0, C_EXTERNAL, "Tavily API\n(primary search)", fontsize=7.5)
ghost(ax, 12.5, 9.7, 3.2, 1.0, C_EXTERNAL, "Google CSE\n(fallback search)", fontsize=7.5)
arrow(ax, 11.2, 12.0, 12.5, 11.8, label="Search", fontsize=7)
arrow(ax, 12.5, 11.7, 12.5, 10.7, label="fallback", fontsize=7, color="#888888")

# Post-processing box
box(ax, 4.0, 4.5, 9.0, 1.6, C_POST,
    "Post-Processing\n"
    "fit_score · viability check · deadline validation · geography filter\n"
    "adaptive threshold · dedup · assign IDs",
    fontsize=7.8, text_color=WHITE, style="round,pad=0.08")
arrow(ax, 8.5, 6.7, 8.5, 6.1, label="Extracted\ndata", fontsize=7)

# File Cache — placed below Google CSE to avoid overlap
cylinder(ax, 13.5, 7.4, 2.8, 1.5, C_CACHE, "File Cache\n24h TTL\n(JSON)", fontsize=7.5)
arrow(ax, 11.2, 9.6, 13.5, 8.6, label="Save/Load", fontsize=7,
      connectionstyle="arc3,rad=-0.1")

# Gemini Flash – shared model note (right side)
ghost(ax, 12.5, 14.2, 3.2, 0.8, C_MODEL, "Gemini Flash  (LLM)\nall 3 agents", fontsize=7.5)
for ay_src, ax_src in [(13.2, 14.2), (13.8, 14.2)]:
    pass
ax.annotate("", xy=(11.2, 14.0), xytext=(12.5, 14.6),
            arrowprops=dict(arrowstyle="-|>", color=C_MODEL, lw=1.1,
                            linestyle="dashed",
                            connectionstyle="arc3,rad=0.0"), zorder=5)
ax.text(12.0, 14.35, "LLM", ha="center", fontsize=7, color=C_MODEL)

# Return arrow: backend -> frontend
arrow(ax, 5.8, 5.0, 3.8, 17.9,
      label="4. JSON Results",
      fontsize=7.5, color="#1565C0",
      connectionstyle="arc3,rad=0.35")

# ══════════════════════════════════════════════════════════════════════════
# PANEL 3 – PHASE 3: DRAFTING
# ══════════════════════════════════════════════════════════════════════════
panel(ax, 0.4, 1.0, 6.0, 3.3, "[P3]  Phase 3: Drafting",
      label_color="#4A148C", bg="#F3E5F5", edge="#CE93D8")

box(ax, 1.0, 2.7, 4.8, 0.95, C_AGENT,
    "Writer Agent  (writer_agent.py)\nGrant proposal drafting", fontsize=8)

ghost(ax, 1.5, 1.4, 3.8, 0.85, C_MODEL, "Gemini Flash", fontsize=8)

arrow(ax, 3.4, 2.7, 3.4, 2.25, label="Draft", fontsize=7)

# User selects grant → Writer
arrow(ax, 5.5, 19.2, 2.2, 3.65,
      label="5. User\nselects\ngrant",
      fontsize=7, connectionstyle="arc3,rad=0.25")

# Writer → Streamlit (Final Proposal)
arrow(ax, 5.8, 3.15, 9.0, 20.1,
      label="6. Final Proposal",
      fontsize=7, color="#1565C0",
      connectionstyle="arc3,rad=-0.25")

# ══════════════════════════════════════════════════════════════════════════
# LEGEND
# ══════════════════════════════════════════════════════════════════════════
lx, ly = 7.5, 1.1
legend_items = [
    (C_UI,       False, "UI / Frontend component"),
    (C_WORKFLOW, False, "GrantSeekerWorkflow (orchestrator)"),
    (C_AGENT,    False, "ADK LLM Agent"),
    (C_FILTER,   False, "Filter / post-processing layer"),
    (C_EXTRACT,  False, "Content extraction chain"),
    (C_POST,     False, "Post-processing pipeline"),
    (C_EXTERNAL, True,  "External service / AI model"),
    (C_CACHE,    True,  "Storage / file cache"),
]
ax.text(lx, ly + 2.95, "Legend", ha="left", va="top",
        fontsize=9, fontweight="bold", color="#333333")
for i, (color, dash, label) in enumerate(legend_items):
    yy = ly + 2.55 - i * 0.32
    if dash:
        ghost(ax, lx, yy - 0.13, 0.85, 0.27, color, "", fontsize=1, lw=1.2)
    else:
        p = FancyBboxPatch((lx, yy - 0.13), 0.85, 0.27,
                           boxstyle="round,pad=0.03", linewidth=1,
                           edgecolor=color, facecolor=color)
        ax.add_patch(p)
    ax.text(lx + 1.05, yy, label, ha="left", va="center",
            fontsize=7.8, color="#333333")

# ══════════════════════════════════════════════════════════════════════════
# TITLE
# ══════════════════════════════════════════════════════════════════════════
ax.text(8.5, 24.6, "Grant Seeker AI  --  Updated Architecture Diagram",
        ha="center", va="center", fontsize=15, fontweight="bold", color="#1A237E")
ax.text(8.5, 24.2, "Multi-Agent System  |  Google ADK  |  Streamlit  |  Gemini Flash  |  April 2026",
        ha="center", va="center", fontsize=9, color="#555555")

plt.tight_layout(pad=0)
out = "architecture_diagram/architecture_diagram_updated.png"
fig.savefig(out, dpi=150, bbox_inches="tight", facecolor=BG_MAIN)
print(f"Saved → {out}")
