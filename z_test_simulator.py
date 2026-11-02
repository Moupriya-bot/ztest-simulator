import math
import re

import matplotlib.pyplot as plt
import numpy as np
import streamlit as st
from scipy.stats import norm

st.set_page_config(page_title="Z-test simulator", page_icon="📐", layout="wide")

INK, BLUE, CORAL, TEAL, MUTED = "#14213D", "#3A6EA5", "#E5484D", "#1B998B", "#6B7A90"
plt.rcParams.update({"savefig.transparent": True, "font.size": 10})

# ---------------------------------------------------------------
# Look and feel (graph-paper background, ink-blue text)
# ---------------------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:wght@500;700&family=Source+Sans+3:wght@400;600&display=swap');
.stApp { background-color:#F3F6FA;
  background-image:linear-gradient(rgba(20,33,61,.05) 1px,transparent 1px),linear-gradient(90deg,rgba(20,33,61,.05) 1px,transparent 1px);
  background-size:28px 28px; }
.stApp, .stApp p, .stApp label, .stApp li { font-family:'Source Sans 3',sans-serif; color:#14213D; }
[data-testid="stIconMaterial"] { font-family:'Material Symbols Rounded' !important; }
textarea, input { background:#FFFFFF !important; color:#14213D !important; -webkit-text-fill-color:#14213D !important; }
[data-baseweb="textarea"], [data-baseweb="base-input"] { background:#FFFFFF !important; border:1.5px solid #14213D !important; border-radius:4px !important; }
[data-baseweb="select"] > div { background:#FFFFFF !important; color:#14213D !important; }
[data-baseweb="select"] span { color:#14213D !important; }
h1,h2,h3,[data-testid="stMetricValue"] { font-family:'Bricolage Grotesque',sans-serif !important; color:#14213D !important; }
h1 { font-size:2.6rem !important; letter-spacing:-0.02em; margin-bottom:0 !important; }
#MainMenu, footer { visibility:hidden; }
header[data-testid="stHeader"] { background:transparent; }
[data-testid="stSidebar"] { background:#E6ECF4; border-right:1.5px solid #14213D; }
[data-testid="stSidebar"] h3 { font-size:1.05rem !important; margin-top:1rem; }
.stButton>button, [data-testid="stFormSubmitButton"]>button { background:#14213D; color:#fff; border:none; border-radius:4px; padding:.5rem 1.6rem; font-weight:600; }
.stButton>button:hover, [data-testid="stFormSubmitButton"]>button:hover { background:#3A6EA5; color:#fff; }
.stButton>button p, [data-testid="stFormSubmitButton"]>button p { color:#fff !important; }
[data-testid="stForm"] { border:none; padding:0; }
[data-testid="stMetricValue"] { font-size:2rem !important; }
[data-testid="stMetricLabel"] p { color:#6B7A90 !important; }
button[data-baseweb="tab"] p { font-family:'Bricolage Grotesque',sans-serif; font-size:1.05rem; }
.lede { font-size:1.15rem; color:#4A5A72 !important; margin:.2rem 0 1.4rem 0; }
.verdict { background:#fff; border:1.5px solid #14213D; border-radius:4px; padding:1.3rem 1.6rem 1rem 1.6rem; margin-bottom:1.5rem; }
.vhead { font-family:'Bricolage Grotesque',sans-serif; font-size:1.7rem; font-weight:700; line-height:1.2; }
.vhead.rej { color:#E5484D; } .vhead.keep { color:#1B998B; }
.vsub { color:#4A5A72; margin:.2rem 0 2.2rem 0; }
.track { position:relative; height:16px; background:#E3F4F1; border-radius:2px; }
.zone { position:absolute; top:0; height:100%; background:#FBD9DB; }
.zone.l { left:0; } .zone.r { right:0; }
.zone span, .mid { position:absolute; top:22px; font-size:.8rem; color:#6B7A90; white-space:nowrap; }
.zone.l span { left:0; } .zone.r span { right:0; }
.mid { left:50%; transform:translateX(-50%); }
.marker { position:absolute; top:-12px; width:4px; height:40px; background:#14213D; transform:translateX(-2px); }
.marker b { position:absolute; bottom:44px; left:50%; transform:translateX(-50%); background:#14213D; color:#fff; padding:2px 8px; border-radius:3px; font-size:.85rem; white-space:nowrap; }
.facts { display:flex; gap:2.5rem; margin-top:2.6rem; color:#4A5A72; font-size:.95rem; }
.facts b { color:#14213D; }
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------------
# Maths helpers
# ---------------------------------------------------------------
def ztest(m1, m2, s1, s2, n1, n2, alpha):
    z = (m1 - m2) / math.sqrt(s1**2 / n1 + s2**2 / n2)
    return z, 2 * norm.sf(abs(z)), norm.ppf(1 - alpha / 2)


def simulate_z(mu1, mu2, s1, s2, n1, n2, sims):
    a = np.random.normal(mu1, s1, (sims, n1)).mean(axis=1)
    b = np.random.normal(mu2, s2, (sims, n2)).mean(axis=1)
    return (a - b) / np.sqrt(s1**2 / n1 + s2**2 / n2)


def read_data(text, name):
    """Turn typed text like '0.5, 0.4 0.6' into a list of numbers. Stops the app with a message if it is wrong."""
    parts = [t for t in re.split(r"[,;\s]+", text.strip()) if t]
    try:
        values = np.array([float(t) for t in parts])
    except ValueError:
        st.error(f"{name}: only numbers are allowed. Check for letters or typing mistakes.")
        st.stop()
    if len(values) < 2 or not np.all(np.isfinite(values)):
        st.error(f"{name}: enter at least 2 normal numbers.")
        st.stop()
    return values


def new_fig():
    fig, ax = plt.subplots(figsize=(7, 3.2))
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(MUTED)
    ax.tick_params(colors=MUTED)
    ax.xaxis.label.set_color(MUTED)
    ax.yaxis.label.set_color(MUTED)
    ax.grid(alpha=0.2)
    return fig, ax


def show(fig):
    fig.tight_layout()
    st.pyplot(fig)
    plt.close(fig)


def verdict(z, p, alpha, crit):
    rejected = p < alpha
    zone_w = (4 - crit) / 8 * 100
    pos = min(max((z + 4) / 8 * 100, 3), 97)
    head = "The gap is real: reject H₀" if rejected else "Could be luck: fail to reject H₀"
    sub = ("A gap this big would be rare if the groups were truly the same."
           if rejected else "A gap this size can easily happen by chance, so there is not enough proof.")
    st.markdown(
        f'<div class="verdict"><div class="vhead {"rej" if rejected else "keep"}">{head}</div>'
        f'<div class="vsub">{sub}</div>'
        f'<div class="track"><div class="zone l" style="width:{zone_w:.1f}%"><span>reject H₀</span></div>'
        f'<div class="zone r" style="width:{zone_w:.1f}%"><span>reject H₀</span></div>'
        f'<div class="mid">luck zone</div>'
        f'<div class="marker" style="left:{pos:.1f}%"><b>Z = {z:.2f}</b></div></div>'
        f'<div class="facts"><span>P-value <b>{p:.4f}</b></span><span>Alpha <b>{alpha}</b></span>'
        f'<span>Cut-off Z <b>±{crit:.2f}</b></span></div></div>',
        unsafe_allow_html=True)


# ---------------------------------------------------------------
# Sidebar controls
# ---------------------------------------------------------------
st.sidebar.markdown("## Settings")
st.sidebar.markdown("### Population std")
st.sidebar.caption("A Z-test needs the true spread (std) of each group to be known already.")
s1 = st.sidebar.number_input("Std group 1", min_value=0.0001, value=0.10, step=0.01, format="%.4f",
                             help="Bigger means scores are more scattered.")
s2 = st.sidebar.number_input("Std group 2", min_value=0.0001, value=0.12, step=0.01, format="%.4f")
st.sidebar.markdown("### How strict?")
alpha = st.sidebar.selectbox("Alpha", [0.01, 0.05, 0.10], index=1,
                             help="Smaller alpha means you need stronger proof before saying the groups differ.")

# ---------------------------------------------------------------
# Header
# ---------------------------------------------------------------
st.title("Z-test simulator")
st.markdown('<p class="lede">Enter your data for two groups and see if the gap between them is real or just luck.</p>',
            unsafe_allow_html=True)

# ---------------------------------------------------------------
# Data input: the averages and sample sizes come from here
# ---------------------------------------------------------------
st.markdown("### Your data")
st.caption("Type or paste the scores of each group. Separate the numbers with commas, spaces or new lines. Then click Calculate.")
DEFAULT_1 = "0.52, 0.41, 0.47, 0.39, 0.55, 0.43, 0.48, 0.36, 0.50, 0.44"
DEFAULT_2 = "0.38, 0.45, 0.33, 0.41, 0.36, 0.47, 0.40, 0.35, 0.44, 0.42"
with st.form("data_form"):
    d1, d2 = st.columns(2)
    text1 = d1.text_area("Group 1 scores", DEFAULT_1, height=120)
    text2 = d2.text_area("Group 2 scores", DEFAULT_2, height=120)
    clicked = st.form_submit_button("Calculate")

# Read the data only when Calculate is clicked (and once at the start with the example data)
if clicked or "data" not in st.session_state:
    st.session_state["data"] = (read_data(text1, "Group 1"), read_data(text2, "Group 2"))
data1, data2 = st.session_state["data"]
n1, n2 = len(data1), len(data2)          # how many values were typed
m1, m2 = float(data1.mean()), float(data2.mean())   # averages calculated from the data

c1, c2, c3, c4 = st.columns(4)
c1.metric("Group 1 values", n1)
c2.metric("Group 1 average", f"{m1:.3f}", help="Sum of all scores divided by how many there are.")
c3.metric("Group 2 values", n2)
c4.metric("Group 2 average", f"{m2:.3f}", help="Sum of all scores divided by how many there are.")

# ---------------------------------------------------------------
# Test and verdict
# ---------------------------------------------------------------
z, p, crit = ztest(m1, m2, s1, s2, n1, n2, alpha)
verdict(z, p, alpha, crit)

tab1, tab2, tab3 = st.tabs(["The test", "Repeat it many times", "Change the sample size"])

# ---------------------------------------------------------------
# Tab 1: the single test
# ---------------------------------------------------------------
with tab1:
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Group 1 average", f"{m1:.2f}")
    c2.metric("Group 2 average", f"{m2:.2f}")
    c3.metric("Gap", f"{m1 - m2:+.2f}")
    c4.metric("Z-score", f"{z:.2f}")

    left, right = st.columns(2)
    with left:
        st.markdown("### Where each average could land")
        st.caption("If the two bumps overlap a lot, the gap is easy to get by luck.")
        se1, se2 = s1 / math.sqrt(n1), s2 / math.sqrt(n2)
        x = np.linspace(min(m1 - 4 * se1, m2 - 4 * se2), max(m1 + 4 * se1, m2 + 4 * se2), 600)
        fig, ax = new_fig()
        for mu, se, col, name in ((m1, se1, BLUE, "Group 1"), (m2, se2, CORAL, "Group 2")):
            ax.plot(x, norm.pdf(x, mu, se), color=col, label=name)
            ax.fill_between(x, norm.pdf(x, mu, se), color=col, alpha=0.18)
        ax.set_xlabel("Average score")
        ax.set_yticks([])
        ax.legend(frameon=False)
        show(fig)
    with right:
        st.markdown("### Z-score on the bell curve")
        st.caption("The bell shows Z-scores when there is no real difference.")
        lim = max(4, abs(z) + 0.5)
        x = np.linspace(-lim, lim, 800)
        fig, ax = new_fig()
        ax.plot(x, norm.pdf(x), color=INK)
        ax.fill_between(x, norm.pdf(x), where=np.abs(x) >= crit, color=CORAL, alpha=0.35, label="Reject zone")
        ax.axvline(z, color=BLUE, lw=2.5, label=f"Your Z = {z:.2f}")
        ax.set_xlabel("Z-score")
        ax.set_yticks([])
        ax.legend(frameon=False)
        show(fig)

# ---------------------------------------------------------------
# Tab 2: repeated simulation
# ---------------------------------------------------------------
with tab2:
    st.markdown(
        "Here the two averages are treated as the **true** averages. We run the experiment again and again "
        "with fresh random scores and count how often the test says \"there is a difference\". "
        "If the groups really differ, that share is the test's **power**. "
        "If they are equal, it should land near alpha (false alarms).")
    sims = st.slider("Number of repeats", 100, 5000, 1000, 100)
    if st.button("Run simulation"):
        st.session_state["sim"] = {"z": simulate_z(m1, m2, s1, s2, n1, n2, sims), "alpha": alpha}

    if "sim" in st.session_state:
        zs, a = st.session_state["sim"]["z"], st.session_state["sim"]["alpha"]
        cr = norm.ppf(1 - a / 2)
        rej = int(np.sum(2 * norm.sf(np.abs(zs)) < a))
        c1, c2, c3 = st.columns(3)
        c1.metric("Said \"different\"", rej)
        c2.metric("Said \"not sure\"", len(zs) - rej)
        c3.metric("Rejection rate", f"{rej / len(zs) * 100:.1f}%")
        st.caption(f"Made with alpha = {a}. Run again after changing settings.")
        fig, ax = new_fig()
        _, edges, patches = ax.hist(zs, bins=30, color=BLUE, alpha=0.85)
        for e, patch in zip(edges[:-1], patches):
            if abs(e + (edges[1] - edges[0]) / 2) >= cr:
                patch.set_facecolor(CORAL)
        ax.axvline(cr, ls="--", color=INK, lw=1)
        ax.axvline(-cr, ls="--", color=INK, lw=1)
        ax.set_xlabel("Z-score from each repeat (red = test said different)")
        ax.set_ylabel("Count")
        show(fig)

# ---------------------------------------------------------------
# Tab 3: sample size experiment
# ---------------------------------------------------------------
with tab3:
    st.markdown("More data makes the test better at spotting a real gap. "
                "This repeats the experiment at many sample sizes (same size for both groups).")
    c1, c2 = st.columns(2)
    sims_size = c1.slider("Repeats per size", 100, 2000, 500, 100)
    max_n = c2.slider("Largest sample size", 50, 500, 200, 50)
    if st.button("Run experiment"):
        sizes = list(range(10, max_n + 1, 10))
        rates = [float(np.mean(2 * norm.sf(np.abs(simulate_z(m1, m2, s1, s2, n, n, sims_size))) < alpha))
                 for n in sizes]
        st.session_state["size_exp"] = {"sizes": sizes, "rates": rates, "alpha": alpha}

    if "size_exp" in st.session_state:
        e = st.session_state["size_exp"]
        fig, ax = new_fig()
        ax.plot(e["sizes"], e["rates"], marker="o", ms=4, color=BLUE, label="Rejection rate")
        ax.axhline(0.8, ls=":", color=TEAL, label="80% power")
        ax.axhline(e["alpha"], ls=":", color=CORAL, label=f"Alpha = {e['alpha']}")
        ax.set_ylim(0, 1)
        ax.set_xlabel("Sample size per group")
        ax.set_ylabel("Rejection rate")
        ax.legend(frameon=False)
        show(fig)
