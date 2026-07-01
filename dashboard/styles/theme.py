"""Global CSS injection that transforms Streamlit into an enterprise UI.

The stylesheet is fully variable-driven: neutral/surface colors are defined per
theme mode (``dark`` / ``light``) while accent colors, gradients, and radii stay
constant. Switching mode simply swaps the ``:root`` variable values, so every
component restyles consistently without duplicated rules.
"""

from __future__ import annotations

import streamlit as st

from dashboard.config import THEME

# Mode-specific neutral / surface tokens. Accent colors live in THEME and are
# shared across both modes.
_MODE_VARS: dict[str, dict[str, str]] = {
    "dark": {
        "bg": "#090B11",
        "bg_secondary": "#0F121D",
        "card": "rgba(15, 18, 29, 0.6)",
        "text": "#FFFFFF",
        "text_secondary": "#E2E8F0",
        "text_muted": "#94A3B8",
        "border": "rgba(255, 255, 255, 0.06)",
        "border_glass": "rgba(255, 255, 255, 0.06)",
        "hover": "rgba(124, 58, 237, 0.12)",
        "hover_strong": "rgba(124, 58, 237, 0.20)",
        "surface": "rgba(255, 255, 255, 0.02)",
        "surface_2": "rgba(255, 255, 255, 0.03)",
        "code_bg": "rgba(15, 18, 29, 0.6)",
        "sidebar_grad": "#0B0D16",
        "popover_bg": "rgba(15, 18, 29, 0.97)",
        "expander_bg": "rgba(15, 18, 29, 0.5)",
        "validation_bg": "rgba(15, 18, 29, 0.6)",
        "empty_bg": "rgba(15, 18, 29, 0.5)",
        "scroll": "rgba(255, 255, 255, 0.08)",
        "scroll_hover": "rgba(255, 255, 255, 0.15)",
        "shadow": "rgba(0, 0, 0, 0.50)",
        "float_bg": "rgba(15, 18, 29, 0.85)",
        "tint_1": "rgba(124, 58, 237, 0.08)",
        "tint_2": "rgba(6, 182, 212, 0.06)",
    },
    "light": {
        "bg": "#090B11",
        "bg_secondary": "#0F121D",
        "card": "rgba(15, 18, 29, 0.6)",
        "text": "#FFFFFF",
        "text_secondary": "#E2E8F0",
        "text_muted": "#94A3B8",
        "border": "rgba(255, 255, 255, 0.06)",
        "border_glass": "rgba(255, 255, 255, 0.06)",
        "hover": "rgba(124, 58, 237, 0.12)",
        "hover_strong": "rgba(124, 58, 237, 0.20)",
        "surface": "rgba(255, 255, 255, 0.02)",
        "surface_2": "rgba(255, 255, 255, 0.03)",
        "code_bg": "rgba(15, 18, 29, 0.6)",
        "sidebar_grad": "#0B0D16",
        "popover_bg": "rgba(15, 18, 29, 0.97)",
        "expander_bg": "rgba(15, 18, 29, 0.5)",
        "validation_bg": "rgba(15, 18, 29, 0.6)",
        "empty_bg": "rgba(15, 18, 29, 0.5)",
        "scroll": "rgba(255, 255, 255, 0.08)",
        "scroll_hover": "rgba(255, 255, 255, 0.15)",
        "shadow": "rgba(0, 0, 0, 0.50)",
        "float_bg": "rgba(15, 18, 29, 0.85)",
        "tint_1": "rgba(124, 58, 237, 0.08)",
        "tint_2": "rgba(6, 182, 212, 0.06)",
    },
}


def inject_global_styles(mode: str = "dark") -> None:
    """Inject the global stylesheet for the given theme mode. Forces dark theme.

    Args:
        mode: Ignored (forced to "dark").
    """
    st.markdown(_build_css("dark"), unsafe_allow_html=True)


def inject_motion_preference(enabled: bool) -> None:
    """Disable all motion when the user turns animations off."""
    if enabled:
        return
    st.markdown(
        "<style>*,*::before,*::after"
        "{animation:none!important;transition:none!important;}</style>",
        unsafe_allow_html=True,
    )


def _build_css(mode: str) -> str:
    """Construct the full stylesheet for the requested mode."""
    p = THEME.palette
    g = THEME.gradients
    r = THEME.radius
    v = _MODE_VARS.get(mode, _MODE_VARS["dark"])
    root_vars = "".join(f"--{name.replace('_', '-')}: {value};" for name, value in v.items())
    return f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

:root {{
    {root_vars}
    --success: {p.success};
    --warning: {p.warning};
    --danger: {p.danger};
    --info: {p.info};
    --purple: {p.purple};
    --pink: {p.pink};
    --orange: {p.orange};
    --grad-hero: {g.hero};
    --grad-metric: {g.metric};
    --grad-button: {g.button};
    --radius-card: {r.card};
    --radius-button: {r.button};
    --radius-chart: {r.chart};
}}

html, body, [class*="css"], .stApp {{ font-family: {THEME.font_family}; color: var(--text); }}

.stApp {{
    background:
        radial-gradient(900px circle at 12% -5%, var(--tint-1), transparent 45%),
        radial-gradient(800px circle at 95% 5%, var(--tint-2), transparent 42%),
        var(--bg);
}}

/* Hide only specific Streamlit chrome — never the whole header. */
#MainMenu, footer {{ visibility: hidden; }}
header[data-testid="stHeader"] {{ background: transparent; }}
[data-testid="stToolbar"], [data-testid="stDecoration"] {{ display: none; }}

/* Sidebar permanently visible: remove collapse / expand arrows entirely. */
[data-testid="stSidebarCollapseButton"],
[data-testid="stExpandSidebarButton"],
[data-testid="stSidebarCollapsedControl"],
[data-testid="collapsedControl"] {{ display: none !important; }}
[data-testid="stSidebar"] {{
    visibility: visible !important;
    transform: none !important;
    width: 320px !important;
    min-width: 300px !important;
    max-width: 320px !important;
}}
@media (max-width: 1024px) {{
    [data-testid="stSidebar"] {{
        width: 300px !important;
    }}
}}

.block-container {{ padding: 2.5rem 3rem 5rem 3rem; max-width: 1280px; }}

::-webkit-scrollbar {{ width: 10px; height: 10px; }}
::-webkit-scrollbar-track {{ background: transparent; }}
::-webkit-scrollbar-thumb {{ background: var(--scroll); border-radius: 8px; }}
::-webkit-scrollbar-thumb:hover {{ background: var(--scroll-hover); }}

/* ----------------------------- Sidebar ----------------------------- */
[data-testid="stSidebar"] {{
    background: var(--sidebar-grad);
    border-right: 1px solid var(--border);
}}
[data-testid="stSidebar"] .block-container {{
    padding: 1.5rem 1rem;
}}

/* Spacing grid */
[data-testid="stSidebar"] [data-testid="stVerticalBlock"] {{
    gap: 8px !important;
}}

.hq-brand {{
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 8px 8px 4px 8px !important;
}}
.hq-brand-logo {{
    padding: 4px 6px 4px 6px;
}}
.hq-brand-logo img {{
    width: 100%;
    max-width: 180px;
    height: auto;
    display: block;
}}
.hq-brand-mark {{
    width: 32px;
    height: 32px;
    border-radius: 8px;
    background: var(--purple);
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 0 12px rgba(124, 58, 237, 0.3);
    font-weight: 800;
    color: white;
    font-size: 14px;
}}
.hq-brand-name {{
    font-size: 20px !important;
    font-weight: 700 !important;
    letter-spacing: -0.03em !important;
    line-height: 1.2 !important;
    color: #FFFFFF !important;
}}
.hq-brand-sub {{
    font-size: 12px !important;
    color: var(--text-muted) !important;
    font-weight: 500 !important;
    line-height: 1.2 !important;
    margin-top: 2px !important;
}}
.hq-sidebar-divider {{
    height: 1px;
    background: var(--border);
    margin: 6px 4px 12px 4px;
}}
.hq-menu-label {{
    font-size: 11px !important;
    font-weight: 700 !important;
    letter-spacing: 0.15em !important;
    text-transform: uppercase !important;
    color: var(--text-muted) !important;
    padding: 24px 8px 8px 8px !important;
    margin: 0 !important;
}}

/* Sidebar Inactive Button State (Secondary) */
[data-testid="stSidebar"] .stButton > button[kind="secondary"] {{
    width: 100%;
    text-align: left;
    justify-content: flex-start;
    background: transparent;
    border: 1px solid transparent;
    color: var(--text-secondary) !important;
    font-weight: 500;
    font-size: 15px;
    padding: 8px 12px;
    border-radius: 8px;
    margin: 0;
    transition: background 200ms ease, border-color 200ms ease, color 200ms ease, transform 200ms ease, box-shadow 200ms ease;
}}
[data-testid="stSidebar"] .stButton > button[kind="secondary"]:hover {{
    background: var(--hover) !important;
    border-color: rgba(255, 255, 255, 0.04) !important;
    color: #FFFFFF !important;
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}}
[data-testid="stSidebar"] .stButton > button[kind="secondary"]:focus {{
    box-shadow: none !important;
    outline: none !important;
}}
[data-testid="stSidebar"] .stButton > button[kind="secondary"] [data-testid="stIconMaterial"] {{
    color: var(--text-muted) !important;
    margin-right: 8px !important;
    font-size: 18px !important;
    transition: color 200ms ease;
}}
[data-testid="stSidebar"] .stButton > button[kind="secondary"]:hover [data-testid="stIconMaterial"] {{
    color: #8B5CF6 !important;
}}

/* Sidebar Active Button State (Primary) */
[data-testid="stSidebar"] .stButton > button[kind="primary"] {{
    width: 100%;
    text-align: left;
    justify-content: flex-start;
    background: rgba(124, 58, 237, 0.12) !important;
    border: 1px solid rgba(124, 58, 237, 0.25) !important;
    color: #FFFFFF !important;
    font-weight: 700 !important;
    font-size: 15px;
    padding: 8px 12px;
    border-radius: 8px;
    margin: 0;
    box-shadow: 0 0 12px rgba(124, 58, 237, 0.15), 0 0 4px rgba(124, 58, 237, 0.1) !important;
    position: relative !important;
    transition: background 200ms ease, border-color 200ms ease, color 200ms ease;
}}
[data-testid="stSidebar"] .stButton > button[kind="primary"]::before {{
    content: "" !important;
    position: absolute !important;
    left: 0 !important;
    top: 25% !important;
    height: 50% !important;
    width: 3px !important;
    background: #7C3AED !important;
    border-radius: 2px !important;
    z-index: 10 !important;
}}
[data-testid="stSidebar"] .stButton > button[kind="primary"] [data-testid="stIconMaterial"] {{
    color: #8B5CF6 !important;
    margin-right: 8px !important;
    font-size: 18px !important;
}}
[data-testid="stSidebar"] .stButton > button[kind="primary"]:focus {{
    box-shadow: 0 0 12px rgba(124, 58, 237, 0.15), 0 0 4px rgba(124, 58, 237, 0.1) !important;
    outline: none !important;
}}

/* Sidebar bordered containers styled as cards */
[data-testid="stSidebar"] [data-testid="stVerticalBlockBorderWrapper"] {{
    background: rgba(17, 24, 39, 0.4) !important;
    border: 1px solid rgba(255, 255, 255, 0.08) !important;
    border-radius: 12px !important;
    padding: 12px 14px !important;
    margin-bottom: 4px !important;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15) !important;
    transition: border-color 200ms ease, box-shadow 200ms ease;
}}
[data-testid="stSidebar"] [data-testid="stVerticalBlockBorderWrapper"]:hover {{
    border-color: rgba(124, 58, 237, 0.20) !important;
    box-shadow: 0 6px 16px rgba(124, 58, 237, 0.06) !important;
}}

/* Clean nested controls styling */
[data-testid="stSidebar"] [data-testid="stVerticalBlockBorderWrapper"] [data-testid="stToggle"] {{
    padding: 2px 0 !important;
    margin: 0 !important;
}}
[data-testid="stSidebar"] [data-testid="stVerticalBlockBorderWrapper"] [data-testid="stToggle"] label p {{
    font-size: 13px !important;
    font-weight: 500 !important;
    color: var(--text-secondary) !important;
}}

/* Refresh Button styling */
[data-testid="stSidebar"] .hq-refresh + div.stButton button {{
    background: rgba(124, 58, 237, 0.08) !important;
    border: 1px solid rgba(124, 58, 237, 0.20) !important;
    color: #FFFFFF !important;
    font-weight: 600 !important;
    font-size: 13px !important;
    border-radius: 8px !important;
    padding: 6px 12px !important;
    transition: all 200ms ease !important;
    text-align: center !important;
    justify-content: center !important;
}}
[data-testid="stSidebar"] .hq-refresh + div.stButton button:hover {{
    background: rgba(124, 58, 237, 0.16) !important;
    border-color: rgba(124, 58, 237, 0.40) !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 12px rgba(124, 58, 237, 0.20) !important;
}}
[data-testid="stSidebar"] .hq-refresh + div.stButton button:hover [data-testid="stIconMaterial"] {{
    animation: hq-spin 700ms cubic-bezier(0.5, 0, 0.5, 1) !important;
}}

/* Submission Ready card */
.hq-side-status {{
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 12px 14px;
    border-radius: 12px;
    transition: all 200ms ease;
    margin-top: 4px;
}}
.hq-side-status.success {{
    background: linear-gradient(135deg, rgba(34, 197, 94, 0.08) 0%, rgba(34, 197, 94, 0.02) 100%);
    border: 1px solid rgba(34, 197, 94, 0.20);
    box-shadow: 0 4px 12px rgba(34, 197, 94, 0.04);
}}
.hq-side-status.success .hq-side-status-icon {{
    display: flex;
    align-items: center;
    justify-content: center;
    width: 20px;
    height: 20px;
    border-radius: 50%;
    background: rgba(34, 197, 94, 0.15);
    color: #22C55E;
    font-size: 11px;
    font-weight: 700;
}}
.hq-side-status.success .hq-side-status-title {{
    font-size: 13px;
    font-weight: 600;
    color: #22C55E;
    line-height: 1.2;
}}
.hq-side-status.success .hq-side-status-desc {{
    font-size: 11px;
    color: rgba(34, 197, 94, 0.85);
    line-height: 1.2;
    margin-top: 2px;
}}

.hq-side-status.error {{
    background: linear-gradient(135deg, rgba(239, 68, 68, 0.08) 0%, rgba(239, 68, 68, 0.02) 100%);
    border: 1px solid rgba(239, 68, 68, 0.20);
    box-shadow: 0 4px 12px rgba(239, 68, 68, 0.04);
}}
.hq-side-status.error .hq-side-status-icon {{
    display: flex;
    align-items: center;
    justify-content: center;
    width: 20px;
    height: 20px;
    border-radius: 50%;
    background: rgba(239, 68, 68, 0.15);
    color: #EF4444;
    font-size: 10px;
    font-weight: 700;
}}
.hq-side-status.error .hq-side-status-title {{
    font-size: 13px;
    font-weight: 600;
    color: #EF4444;
    line-height: 1.2;
}}
.hq-side-status.error .hq-side-status-desc {{
    font-size: 11px;
    color: rgba(239, 68, 68, 0.85);
    line-height: 1.2;
    margin-top: 2px;
}}

.hq-side-status.pending {{
    background: linear-gradient(135deg, rgba(255, 255, 255, 0.04) 0%, rgba(255, 255, 255, 0.01) 100%);
    border: 1px solid rgba(255, 255, 255, 0.08);
}}
.hq-side-status.pending .hq-side-status-icon {{
    display: flex;
    align-items: center;
    justify-content: center;
    width: 20px;
    height: 20px;
    border-radius: 50%;
    background: rgba(255, 255, 255, 0.06);
    color: var(--text-muted);
    font-size: 11px;
}}
.hq-side-status.pending .hq-side-status-title {{
    font-size: 13px;
    font-weight: 600;
    color: var(--text-secondary);
    line-height: 1.2;
}}
.hq-side-status.pending .hq-side-status-desc {{
    font-size: 11px;
    color: var(--text-muted);
    line-height: 1.2;
    margin-top: 2px;
}}

/* ----------------------------- Animations ----------------------------- */
@keyframes hq-fade-up {{ from {{ opacity:0; transform:translateY(14px); }} to {{ opacity:1; transform:translateY(0); }} }}
@keyframes hq-float {{ 0%,100% {{ transform:translateY(0); }} 50% {{ transform:translateY(-18px); }} }}
@keyframes hq-pulse {{ 0%,100% {{ opacity:0.55; }} 50% {{ opacity:1; }} }}
@keyframes hq-spin {{ from {{ transform:rotate(0deg); }} to {{ transform:rotate(360deg); }} }}
@keyframes hq-shimmer {{ from {{ transform:translateX(-120%); }} to {{ transform:translateX(220%); }} }}
.hq-animate {{ animation: hq-fade-up 600ms cubic-bezier(0.22,1,0.36,1) both; }}

/* ----------------------------- Hero (vibrant in both modes) ----------------------------- */
.hq-hero {{
    position:relative; overflow:hidden; border-radius:28px; padding:56px 48px;
    background:
        radial-gradient(600px circle at 0% 0%, rgba(124,58,237,0.38), transparent 55%),
        radial-gradient(600px circle at 100% 100%, rgba(251,146,60,0.22), transparent 55%),
        #14121c;
    border:1px solid rgba(255,255,255,0.12); backdrop-filter: blur(20px);
    box-shadow: 0 30px 80px rgba(124,58,237,0.22); margin-bottom:40px;
}}
.hq-hero-orb {{ position:absolute; border-radius:50%; filter:blur(40px); opacity:0.5; animation: hq-float 9s ease-in-out infinite; }}
.hq-hero-orb.one {{ width:220px; height:220px; right:-40px; top:-60px; background:var(--grad-hero); }}
.hq-hero-orb.two {{ width:160px; height:160px; right:160px; bottom:-50px; background:linear-gradient(135deg,#3B82F6,#06B6D4); animation-delay:1.5s; }}
.hq-badge {{
    display:inline-flex; align-items:center; gap:8px; padding:7px 14px; border-radius:999px;
    background:rgba(255,255,255,0.08); border:1px solid rgba(255,255,255,0.14);
    font-size:12.5px; font-weight:600; color:#D6D9E6; backdrop-filter: blur(8px);
}}
.hq-badge .dot {{ width:7px; height:7px; border-radius:50%; background:var(--success); box-shadow:0 0 10px var(--success); animation:hq-pulse 2s infinite; }}
.hq-hero h1 {{
    font-size:54px; font-weight:800; letter-spacing:-0.03em; line-height:1.05; margin:22px 0 0 0;
    background:linear-gradient(120deg,#fff 30%,#c4b5fd 75%,#fbcfe8);
    -webkit-background-clip:text; background-clip:text; -webkit-text-fill-color:transparent;
}}
.hq-hero .subtitle {{ font-size:22px; font-weight:600; color:#FFFFFF; margin-top:10px; }}
.hq-hero .desc {{ font-size:15.5px; color:#C2C6D6; max-width:620px; margin-top:16px; line-height:1.65; }}

/* ----------------------------- Section titles ----------------------------- */
.hq-section {{ margin:14px 0 22px 0; }}
.hq-section .eyebrow {{ font-size:12px; font-weight:700; letter-spacing:0.12em; text-transform:uppercase; color:var(--purple); }}
.hq-section h2 {{ font-size:30px; font-weight:700; letter-spacing:-0.02em; margin:6px 0 0 0; }}
.hq-section .sub {{ font-size:15px; color:var(--text-secondary); margin-top:6px; }}

/* ----------------------------- Cards ----------------------------- */
.hq-card {{
    background:var(--card); border:1px solid var(--border-glass); border-radius:var(--radius-card);
    padding:22px 24px; backdrop-filter:blur(20px); box-shadow:0 18px 50px var(--shadow);
    transition: transform 250ms ease, box-shadow 250ms ease, border-color 250ms ease; height:100%;
}}
.hq-card:hover {{ transform:translateY(-4px); border-color:rgba(124,58,237,0.45); box-shadow:0 26px 60px rgba(124,58,237,0.22); }}

.hq-metric .icon {{
    width:44px; height:44px; border-radius:13px; display:flex; align-items:center; justify-content:center;
    background:rgba(124,58,237,0.16); border:1px solid rgba(124,58,237,0.3); margin-bottom:14px;
    transition: transform 250ms cubic-bezier(0.22,1,0.36,1);
}}
.hq-card:hover .hq-metric .icon, .hq-metric:hover .icon {{ transform: translateY(-2px) scale(1.06) rotate(-3deg); }}
.hq-metric .label {{ font-size:13px; color:var(--text-muted); font-weight:600; letter-spacing:0.02em; }}
.hq-metric .value {{ font-size:34px; font-weight:800; letter-spacing:-0.02em; margin:6px 0 4px 0; }}
.hq-metric .desc {{ font-size:12.5px; color:var(--text-secondary); }}
.hq-trend {{ display:inline-flex; align-items:center; gap:5px; padding:3px 9px; border-radius:999px; font-size:11.5px; font-weight:700; margin-top:10px; }}
.hq-trend.up {{ background:rgba(34,197,94,0.14); color:var(--success); }}
.hq-trend.neutral {{ background:rgba(59,130,246,0.14); color:var(--info); }}
.hq-trend.muted {{ background:rgba(125,133,151,0.16); color:var(--text-muted); }}

/* ----------------------------- Pipeline timeline ----------------------------- */
.hq-pipe {{ display:flex; align-items:center; gap:0; flex-wrap:wrap; }}
.hq-pipe-stage {{ display:flex; flex-direction:column; align-items:center; gap:8px; flex:1; min-width:90px; }}
.hq-pipe-node {{
    width:46px; height:46px; border-radius:50%; display:flex; align-items:center; justify-content:center;
    font-weight:700; border:2px solid var(--border-glass); color:var(--text-muted); background:var(--surface);
}}
.hq-pipe-node.done {{ background:rgba(34,197,94,0.16); border-color:var(--success); color:var(--success); box-shadow:0 0 18px rgba(34,197,94,0.3); }}
.hq-pipe-label {{ font-size:12px; color:var(--text-secondary); font-weight:600; text-align:center; }}
.hq-pipe-conn {{ height:2px; flex:0.5; min-width:18px; background:linear-gradient(90deg,var(--success),rgba(34,197,94,0.2)); margin-bottom:26px; }}

/* ----------------------------- Stat pills ----------------------------- */
.hq-stat {{ background:var(--surface); border:1px solid var(--border); border-radius:16px; padding:16px 18px; }}
.hq-stat .k {{ font-size:12px; color:var(--text-muted); font-weight:600; }}
.hq-stat .v {{ font-size:24px; font-weight:700; margin-top:4px; }}

/* ----------------------------- Validation ----------------------------- */
.hq-validation {{ border-radius:24px; padding:38px 36px; text-align:center; backdrop-filter:blur(20px); }}
.hq-validation.ok {{ background:radial-gradient(500px circle at 50% 0%,rgba(34,197,94,0.18),transparent 60%),var(--validation-bg); border:1px solid rgba(34,197,94,0.4); }}
.hq-validation.fail {{ background:radial-gradient(500px circle at 50% 0%,rgba(239,68,68,0.18),transparent 60%),var(--validation-bg); border:1px solid rgba(239,68,68,0.4); }}
.hq-validation.unknown {{ background:var(--validation-bg); border:1px solid var(--border-glass); }}
.hq-validation .ring {{ width:84px; height:84px; border-radius:50%; display:flex; align-items:center; justify-content:center; margin:0 auto 18px auto; }}
.hq-validation.ok .ring {{ background:rgba(34,197,94,0.15); border:2px solid var(--success); animation:hq-pulse 2.4s infinite; }}
.hq-validation.fail .ring {{ background:rgba(239,68,68,0.15); border:2px solid var(--danger); }}
.hq-validation.unknown .ring {{ background:rgba(125,133,151,0.12); border:2px solid var(--text-muted); }}
.hq-validation h3 {{ font-size:26px; font-weight:800; margin:0; }}
.hq-validation p {{ color:var(--text-secondary); margin-top:8px; font-size:15px; }}

/* ----------------------------- Artifact / report cards ----------------------------- */
.hq-file {{ display:flex; align-items:center; gap:16px; }}
.hq-file .ficon {{ width:46px; height:46px; border-radius:13px; display:flex; align-items:center; justify-content:center; background:rgba(59,130,246,0.14); border:1px solid rgba(59,130,246,0.3); flex-shrink:0; }}
.hq-file .fname {{ font-size:15px; font-weight:700; }}
.hq-file .fmeta {{ font-size:12px; color:var(--text-muted); margin-top:3px; }}

/* ----------------------------- Empty / error ----------------------------- */
.hq-empty {{ text-align:center; padding:48px 24px; border-radius:24px; background:var(--empty-bg); border:1px dashed var(--border-glass); }}
.hq-empty .glyph {{ font-size:34px; margin-bottom:10px; }}
.hq-empty h4 {{ font-size:19px; font-weight:700; margin:0; }}
.hq-empty p {{ color:var(--text-secondary); margin-top:8px; font-size:14px; }}
.hq-error {{ border-radius:20px; padding:20px 22px; background:rgba(239,68,68,0.08); border:1px solid rgba(239,68,68,0.3); }}
.hq-error .t {{ font-weight:700; color:var(--danger); font-size:15px; }}
.hq-error .m {{ color:var(--text-secondary); font-size:13.5px; margin-top:6px; }}

/* ----------------------------- Buttons ----------------------------- */
.stDownloadButton > button, .stButton > button {{
    border-radius:var(--radius-button); font-weight:600;
    transition: transform 220ms cubic-bezier(0.22,1,0.36,1), box-shadow 220ms ease, border-color 220ms ease, background 220ms ease;
    position:relative; overflow:hidden;
}}
.stButton > button:active, .stDownloadButton > button:active {{ transform: scale(0.97); }}
[data-testid="stMain"] .stDownloadButton > button,
[data-testid="stMain"] .stButton > button[kind="primary"] {{
    background:var(--grad-button); color:white; border:none; box-shadow:0 10px 26px rgba(124,58,237,0.32);
}}
[data-testid="stMain"] .stDownloadButton > button::after,
[data-testid="stMain"] .stButton > button[kind="primary"]::after {{
    content:""; position:absolute; top:0; left:0; width:40%; height:100%;
    background:linear-gradient(120deg, transparent, rgba(255,255,255,0.35), transparent);
    transform:translateX(-120%); pointer-events:none;
}}
[data-testid="stMain"] .stDownloadButton > button:hover,
[data-testid="stMain"] .stButton > button[kind="primary"]:hover {{ transform:translateY(-2px); box-shadow:0 18px 40px rgba(124,58,237,0.45); }}
[data-testid="stMain"] .stDownloadButton > button:hover::after,
[data-testid="stMain"] .stButton > button[kind="primary"]:hover::after {{ animation: hq-shimmer 900ms ease; }}
[data-testid="stMain"] .stButton > button[kind="secondary"] {{
    background:var(--surface-2); color:var(--text); border:1px solid var(--border-glass); backdrop-filter:blur(8px);
}}
[data-testid="stMain"] .stButton > button[kind="secondary"]:hover {{
    border-color:rgba(124,58,237,0.5); background:rgba(124,58,237,0.10); transform:translateY(-2px); box-shadow:0 12px 28px rgba(124,58,237,0.2);
}}

/* ----------------------------- Inputs / selects ----------------------------- */
.stTextInput > div > div > input {{
    background:var(--surface-2); border:1px solid var(--border-glass); border-radius:14px; color:var(--text); transition: all 220ms ease;
}}
.stTextInput > div > div > input:focus {{ border-color:var(--purple); box-shadow:0 0 0 3px rgba(124,58,237,0.22); }}
[data-baseweb="select"] > div {{
    background:var(--surface-2) !important; border-radius:14px !important; border:1px solid var(--border-glass) !important; transition: all 220ms ease;
}}
[data-baseweb="select"] > div:hover {{ border-color:rgba(124,58,237,0.5) !important; }}
[data-baseweb="select"] > div:focus-within {{ border-color:var(--purple) !important; box-shadow:0 0 0 3px rgba(124,58,237,0.22) !important; }}
[data-baseweb="popover"] [role="listbox"] {{
    background:var(--popover-bg) !important; border:1px solid var(--border-glass) !important; border-radius:14px !important; backdrop-filter:blur(16px);
}}
[data-baseweb="popover"] [role="option"] {{ transition: background 160ms ease; border-radius:10px; }}
[data-baseweb="popover"] [role="option"]:hover {{ background:rgba(124,58,237,0.18) !important; }}

/* ----------------------------- Toggle / checkbox / slider ----------------------------- */
[data-baseweb="checkbox"] {{ transition: all 220ms ease; }}
[data-baseweb="checkbox"] > span, [data-baseweb="checkbox"] div {{
    transition: background-color 240ms ease, box-shadow 240ms ease, transform 220ms cubic-bezier(0.22,1,0.36,1) !important;
}}
[data-testid="stCheckbox"] label:hover [data-baseweb="checkbox"] div {{ transform: scale(1.05); }}
[data-baseweb="checkbox"][aria-checked="true"] div:first-child {{ box-shadow:0 0 14px rgba(124,58,237,0.5); }}
[data-testid="stSlider"] [role="slider"] {{ box-shadow:0 0 0 4px rgba(124,58,237,0.18); transition: box-shadow 220ms ease, transform 200ms ease; }}
[data-testid="stSlider"] [role="slider"]:hover {{ transform:scale(1.15); box-shadow:0 0 0 7px rgba(124,58,237,0.25); }}

button:focus-visible, [role="option"]:focus-visible, [role="switch"]:focus-visible {{
    outline:none !important; box-shadow:0 0 0 3px rgba(124,58,237,0.45) !important;
}}

/* ----------------------------- DataFrame (Glide) themed for both modes ----------------------------- */
[data-testid="stDataFrame"] {{
    border-radius:16px; overflow:hidden; border:1px solid var(--border-glass);
    --gdg-bg-cell: var(--bg-secondary);
    --gdg-bg-cell-medium: var(--surface);
    --gdg-bg-header: var(--surface);
    --gdg-bg-header-hovered: var(--hover-strong);
    --gdg-bg-header-has-focus: var(--hover-strong);
    --gdg-text-dark: var(--text);
    --gdg-text-medium: var(--text-secondary);
    --gdg-text-light: var(--text-muted);
    --gdg-border-color: var(--border);
    --gdg-horizontal-border-color: var(--border);
    --gdg-accent-color: var(--purple);
    --gdg-accent-light: rgba(124,58,237,0.18);
}}
[data-testid="stExpander"] {{ border:1px solid var(--border-glass); border-radius:16px; background:var(--expander-bg); transition: border-color 220ms ease; }}
[data-testid="stExpander"]:hover {{ border-color:rgba(124,58,237,0.35); }}
hr {{ border-color:var(--border); }}

.hq-pre {{
    margin:0; padding:18px 20px; border-radius:16px; max-height:460px; overflow:auto;
    background:var(--code-bg); border:1px solid var(--border-glass); color:var(--text-secondary);
    font-size:13px; line-height:1.6; font-family:'SFMono-Regular',Consolas,'Liberation Mono',Menlo,monospace; white-space:pre; tab-size:4;
}}
[data-testid="stText"] {{
    background:var(--code-bg); border:1px solid var(--border-glass); border-radius:16px;
    padding:16px 18px; max-height:480px; overflow:auto; color:var(--text-secondary); font-size:12.5px; line-height:1.6;
}}

.hq-footer {{ margin-top:56px; padding-top:28px; border-top:1px solid var(--border); display:flex; justify-content:space-between; flex-wrap:wrap; gap:12px; color:var(--text-muted); font-size:13px; }}
.hq-footer b {{ color:var(--text-secondary); }}

/* Keep native Streamlit text readable in both modes (base text color differs). */
[data-testid="stWidgetLabel"] p, [data-testid="stWidgetLabel"] label {{ color: var(--text-secondary) !important; }}
[data-testid="stCaptionContainer"], [data-testid="stCaptionContainer"] p {{ color: var(--text-muted) !important; }}
[data-testid="stExpander"] summary, [data-testid="stExpander"] summary p {{ color: var(--text) !important; }}
[data-testid="stMain"] .stMarkdown li {{ color: var(--text-secondary); }}

@media (prefers-reduced-motion: reduce) {{
    *, *::before, *::after {{ animation: none !important; transition: none !important; }}
}}
@media (max-width: 820px) {{
    .block-container {{ padding:1.25rem 1rem 3rem 1rem; }}
    .hq-hero {{ padding:36px 24px; }}
    .hq-hero h1 {{ font-size:38px; }}
}}
</style>
"""
