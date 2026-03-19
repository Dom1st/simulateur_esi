import os
import io
import json
from datetime import datetime

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas


APP_TITLE = "ESI - Simulateur de Vente"
CONFIG_DIR = "configs"
DEFAULT_DEMO_FILE = os.path.join(CONFIG_DIR, "demo.txt")


def ensure_config_dir() -> None:
    os.makedirs(CONFIG_DIR, exist_ok=True)


def default_demo_config() -> dict:
    return {
        "client_title": "00000-2026",
        "prix_net_vendeur_initial": 250000.0,
        "honoraires_agence_taux": 0.05,
        "frais_notaire_taux": 0.08,
        "taux_reduction_notaire": 0.0,
    }


def save_config_file(filepath: str, config: dict) -> None:
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)


def load_config_file(filepath: str) -> dict:
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def ensure_demo_file() -> None:
    ensure_config_dir()
    if not os.path.exists(DEFAULT_DEMO_FILE):
        save_config_file(DEFAULT_DEMO_FILE, default_demo_config())


def infer_display_mode() -> str:
    user_agent = ""
    try:
        user_agent = st.context.headers.get("user-agent", "").lower()
    except Exception:
        pass

    if any(x in user_agent for x in ["windows", "x11", "macintosh", "linux x86_64"]):
        return "PC"

    if "android" in user_agent and "mobile" not in user_agent:
        return "PC"

    if any(x in user_agent for x in ["iphone", "mobile"]):
        return "Mobile"

    if "ipad" in user_agent:
        return "PC"

    return "PC"


def load_config_into_session(cfg: dict) -> None:
    st.session_state.client_title = cfg["client_title"]
    st.session_state.prix_net_vendeur_initial = float(cfg["prix_net_vendeur_initial"])
    st.session_state.honoraires_agence_taux_pct = float(cfg["honoraires_agence_taux"]) * 100.0
    st.session_state.frais_notaire_taux_pct = float(cfg["frais_notaire_taux"]) * 100.0
    st.session_state.taux_reduction_notaire_pct = float(cfg["taux_reduction_notaire"]) * 100.0


def current_config_from_session() -> dict:
    return {
        "client_title": st.session_state.client_title,
        "prix_net_vendeur_initial": st.session_state.prix_net_vendeur_initial,
        "honoraires_agence_taux": st.session_state.honoraires_agence_taux_pct / 100.0,
        "frais_notaire_taux": st.session_state.frais_notaire_taux_pct / 100.0,
        "taux_reduction_notaire": st.session_state.taux_reduction_notaire_pct / 100.0,
    }


def build_dataframe(
    prix_nv_initial: float,
    honoraires_taux: float,
    notaire_taux: float,
    reduction_notaire_taux: float,
) -> pd.DataFrame:
    rows = []
    for variation in range(0, -6, -1):
        coef = 1 + variation / 100.0

        prix_nv = prix_nv_initial * coef
        honoraires = prix_nv * honoraires_taux
        prix_fai = prix_nv + honoraires

        frais_notaire_base = prix_fai * notaire_taux
        cout_total = prix_fai + frais_notaire_base

        frais_notaire_reduits = prix_fai * (1 - reduction_notaire_taux) * notaire_taux
        cout_total_reduit = prix_fai + frais_notaire_reduits

        rows.append(
            {
                "Variation": variation,
                "Prix net vendeur": prix_nv,
                "Prix FAI": prix_fai,
                "Coût acquéreur total": cout_total,
                "Coût avec frais de notaire réduits": cout_total_reduit,
            }
        )

    return pd.DataFrame(rows)


def get_style_params(display_mode: str) -> dict:
    if display_mode == "Mobile":
        return {
            "figsize": (7, 10),
            "title_size": 16,
            "axis_size": 12,
            "tick_size": 11,
            "legend_size": 11,
            "label_size": 11,
            "green_label_size": 10,
            "line_width": 2.2,
            "marker_size": 6,
        }

    return {
        "figsize": (13.33, 7.5),
        "title_size": 20,
        "axis_size": 16,
        "tick_size": 14,
        "legend_size": 13,
        "label_size": 18,
        "green_label_size": 16,
        "line_width": 2.5,
        "marker_size": 7,
    }


def plot_chart(
    df: pd.DataFrame,
    chart_title: str,
    display_mode: str,
    prix_nv_initial: float,
    honoraires_taux: float,
    notaire_taux: float,
    reduction_notaire_taux: float,
):
    params = get_style_params(display_mode)

    fig, ax = plt.subplots(figsize=params["figsize"])

    line_nv, = ax.plot(
        df["Variation"],
        df["Prix net vendeur"],
        marker="o",
        linewidth=params["line_width"],
        markersize=params["marker_size"],
        label="Prix net vendeur",
    )
    line_fai, = ax.plot(
        df["Variation"],
        df["Prix FAI"],
        marker="o",
        linewidth=params["line_width"],
        markersize=params["marker_size"],
        label="Prix FAI",
    )
    line_total, = ax.plot(
        df["Variation"],
        df["Coût acquéreur total"],
        marker="o",
        linewidth=params["line_width"],
        markersize=params["marker_size"],
        label="Coût acquéreur total",
    )
    ax.plot(
        df["Variation"],
        df["Coût avec frais de notaire réduits"],
        linestyle="--",
        marker="o",
        linewidth=params["line_width"],
        markersize=params["marker_size"],
        color="green",
        label="Coût avec frais de notaire réduits",
    )

    ax.set_xlim(0, -5)

    coef_min = 1 - 0.05
    prix_nv_min = prix_nv_initial * coef_min
    honoraires_min = prix_nv_min * honoraires_taux
    prix_fai_min = prix_nv_min + honoraires_min
    cout_total_min = prix_fai_min * (1 + notaire_taux)
    cout_total_reduit_min = prix_fai_min * (1 + (1 - reduction_notaire_taux) * notaire_taux)

    y_min_value = min(
        prix_nv_min,
        prix_fai_min,
        cout_total_min,
        cout_total_reduit_min,
    )
    y_min = int(np.floor(y_min_value / 10000.0) * 10000) - 10000

    values = df[
        [
            "Prix net vendeur",
            "Prix FAI",
            "Coût acquéreur total",
            "Coût avec frais de notaire réduits",
        ]
    ]
    y_max_value = values.max().max()
    y_max = int(np.ceil(y_max_value / 10000.0) * 10000) + 10000

    ax.set_ylim(y_min, y_max)
    yticks = np.arange(y_min, y_max + 1, 10000)
    ax.set_yticks(yticks)
    ax.set_yticklabels([f"{int(y / 1000)}K" for y in yticks], fontsize=params["tick_size"])
    ax.set_xticks(df["Variation"])
    ax.set_xticklabels([f"{v}%" for v in df["Variation"]], fontsize=params["tick_size"])

    for line, col in [
        (line_nv, "Prix net vendeur"),
        (line_fai, "Prix FAI"),
        (line_total, "Coût acquéreur total"),
    ]:
        color = line.get_color()
        for x, y in zip(df["Variation"], df[col]):
            ax.text(
                x,
                y,
                f"{y / 1000:.0f}K",
                ha="center",
                va="bottom",
                fontsize=params["label_size"],
                fontweight="bold",
                color=color,
            )

    for x, y in zip(df["Variation"], df["Coût avec frais de notaire réduits"]):
        ax.text(
            x,
            y,
            f"{y / 1000:.0f}K",
            ha="center",
            va="top",
            fontsize=params["green_label_size"],
            fontweight="bold",
            color="green",
        )

    ax.set_xlabel("Variation du prix (%)", fontsize=params["axis_size"])
    ax.set_ylabel("Montant (K€)", fontsize=params["axis_size"])
    from datetime import datetime

    now = datetime.now().strftime("%d/%m/%Y %H:%M")
    ax.set_title(
        f"Simulation vente - édition du {now}", 
        fontsize=params["title_size"], fontweight="bold")
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=params["legend_size"])

    fig.tight_layout()
    return fig


def build_pdf_bytes(fig, chart_title: str, df: pd.DataFrame, client_title: str) -> bytes:
    image_buffer = io.BytesIO()
    fig.savefig(image_buffer, format="png", dpi=220, bbox_inches="tight")
    image_buffer.seek(0)

    pdf_buffer = io.BytesIO()
    c = canvas.Canvas(pdf_buffer, pagesize=landscape(A4))
    width, height = landscape(A4)

    c.setFont("Helvetica-Bold", 18)
    c.drawString(30, height - 30, chart_title)

    c.setFont("Helvetica", 12)
    c.drawString(30, height - 48, f"Client {client_title}")

    c.setFont("Helvetica", 10)
    c.drawString(30, height - 64, f"Généré le {datetime.now().strftime('%d/%m/%Y %H:%M')}")

    img = ImageReader(image_buffer)
    c.drawImage(
        img,
        20,
        80,
        width=width - 40,
        height=height - 150,
        preserveAspectRatio=True,
        mask="auto",
    )

    c.setFont("Helvetica", 10)
    cfg_line = (
        f"Prix NV initial: {df.iloc[0]['Prix net vendeur'] / 1000:.0f} K€   |   "
        f"Plage: 0% à -5%   |   "
        f"Courbe verte pointillée: frais de notaire réduits"
    )
    c.drawString(30, 25, cfg_line)

    c.showPage()
    c.save()
    pdf_buffer.seek(0)
    return pdf_buffer.getvalue()


def apply_uploaded_config() -> None:
    key = f"config_uploader_{st.session_state.uploader_nonce}"
    uploaded_file = st.session_state.get(key)

    if uploaded_file is None:
        return

    try:
        imported_cfg = json.loads(uploaded_file.getvalue().decode("utf-8"))
        load_config_into_session(imported_cfg)
        st.session_state.upload_error = ""
        st.session_state.uploader_nonce += 1
    except Exception as exc:
        st.session_state.upload_error = f"Fichier invalide : {exc}"


def init_session_state() -> None:
    ensure_demo_file()

    if "initialized" not in st.session_state:
        demo = load_config_file(DEFAULT_DEMO_FILE)
        load_config_into_session(demo)
        st.session_state.uploader_nonce = 0
        st.session_state.upload_error = ""
        st.session_state.initialized = True


def sidebar_load_save_controls() -> None:
    st.sidebar.subheader("Paramètres Client")

    config = current_config_from_session()
    safe_client_name = (
        config["client_title"]
        .strip()
        .replace(" ", "_")
        .replace("/", "_")
        .replace("\\", "_")
    )
    if not safe_client_name:
        safe_client_name = "client"

    config_bytes = json.dumps(config, ensure_ascii=False, indent=2).encode("utf-8")

    st.sidebar.download_button(
        label="Télécharger une copie",
        data=config_bytes,
        file_name=f"config_{safe_client_name}.txt",
        mime="text/plain",
        width="stretch",
    )

    uploader_key = f"config_uploader_{st.session_state.uploader_nonce}"
    st.sidebar.file_uploader(
        "Charger des paramètres...",
        type=["txt"],
        accept_multiple_files=False,
        key=uploader_key,
        on_change=apply_uploaded_config,
    )

    if st.session_state.get("upload_error"):
        st.sidebar.error(st.session_state.upload_error)


def sidebar_parameter_controls() -> None:
    st.sidebar.header("Paramètres")

    st.sidebar.text_input(
        "Titre client",
        key="client_title",
        help="Nom du client affiché dans le sous-titre.",
    )

    st.sidebar.number_input(
        "Prix net vendeur initial (€)",
        min_value=0.0,
        step=1000.0,
        key="prix_net_vendeur_initial",
        format="%.0f",
    )

    st.sidebar.number_input(
        "Honoraires agence (%)",
        min_value=0.0,
        max_value=100.0,
        step=0.01,
        key="honoraires_agence_taux_pct",
        format="%.2f",
    )

    st.sidebar.number_input(
        "Frais de notaire (%)",
        min_value=0.0,
        max_value=100.0,
        step=0.01,
        key="frais_notaire_taux_pct",
        format="%.2f",
    )

    st.sidebar.number_input(
        "Réduction frais de notaire (%)",
        min_value=0.0,
        max_value=100.0,
        step=0.01,
        key="taux_reduction_notaire_pct",
        format="%.2f",
    )


def main() -> None:
    st.set_page_config(
        page_title=APP_TITLE,
        page_icon="🏠",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    init_session_state()

    sidebar_load_save_controls()
    st.sidebar.divider()
    sidebar_parameter_controls()

    st.title(APP_TITLE)
    st.subheader(f"Client : {st.session_state.client_title}")

    display_mode = infer_display_mode()

    prix_nv_initial = st.session_state.prix_net_vendeur_initial
    honoraires_taux = st.session_state.honoraires_agence_taux_pct / 100.0
    notaire_taux = st.session_state.frais_notaire_taux_pct / 100.0
    reduction_notaire_taux = st.session_state.taux_reduction_notaire_pct / 100.0

    df = build_dataframe(
        prix_nv_initial=prix_nv_initial,
        honoraires_taux=honoraires_taux,
        notaire_taux=notaire_taux,
        reduction_notaire_taux=reduction_notaire_taux,
    )

    fig = plot_chart(
        df=df,
        chart_title=APP_TITLE,
        display_mode=display_mode,
        prix_nv_initial=prix_nv_initial,
        honoraires_taux=honoraires_taux,
        notaire_taux=notaire_taux,
        reduction_notaire_taux=reduction_notaire_taux,
    )

    st.pyplot(fig, width="stretch")

    pdf_bytes = build_pdf_bytes(
        fig=fig,
        chart_title=APP_TITLE,
        df=df,
        client_title=st.session_state.client_title,
    )
    st.download_button(
        label="📄 Imprimer / télécharger le PDF",
        data=pdf_bytes,
        file_name="simulation_vente.pdf",
        mime="application/pdf",
        width="stretch",
    )

    with st.expander("Voir le tableau de simulation"):
        df_display = df.copy()
        for col in df_display.columns[1:]:
            df_display[col] = df_display[col] / 1000.0

        df_display["Variation"] = df_display["Variation"].map(lambda x: f"{x:.0f}")
        for col in df_display.columns[1:]:
            df_display[col] = df_display[col].map(
                lambda x: f"{x:,.2f}".replace(",", "X").replace(".", ",").replace("X", " ")
            )

        df_display.columns = [
            "Variation (en %)",
            "Prix net vendeur (K€)",
            "Prix FAI (K€)",
            "Coût acquéreur total (K€)",
            "Coût avec frais de notaire réduits (K€)",
        ]
        st.dataframe(df_display, width="stretch", hide_index=True)

    st.caption(f"Format détecté automatiquement : {display_mode}")


if __name__ == "__main__":
    main()