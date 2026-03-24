import io
import json
import os
from datetime import datetime
import tomllib, toml

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas


def get_config_dir() -> str:
    return "configs"


def get_profile_file() -> str:
    candidates = [
        os.path.join(".streamlit", "profile.toml"),
        "profile.toml",
    ]
    for candidate in candidates:
        if os.path.exists(candidate):
            return candidate
    return candidates[0]


def get_default_config_file() -> str:
    return f"{get_config_dir()}/demo.txt"


def get_default_profile_file() -> str:
    return "profile_default.toml"


def get_default_app_agence() -> str:
    return ""


def get_default_app_title() -> str:
    return "Estimation de vente immobilière"


def build_display_title(agence: str, title: str) -> str:
    agence = str(agence).strip()
    title = str(title).strip() or get_default_app_title()
    return f"{agence} - {title}" if agence else title


def ensure_config_dir() -> None:
    os.makedirs(get_config_dir(), exist_ok=True)


def sanitize_filename(name: str, fallback: str = "mandat") -> str:
    safe_name = (
        str(name)
        .strip()
        .replace(" ", "_")
        .replace("/", "_")
        .replace("\\", "_")
        .replace(":", "_")
        .replace("*", "_")
        .replace("?", "_")
        .replace('"', "_")
        .replace("<", "_")
        .replace(">", "_")
        .replace("|", "_")
    )
    return safe_name or fallback


def list_config_files() -> list[str]:
    ensure_config_dir()
    files = []
    for name in os.listdir(get_config_dir()):
        if name.lower().endswith(".txt"):
            files.append(os.path.join(get_config_dir(), name).replace("\\", "/"))
    return sorted(files)


def default_honoraires_bareme() -> dict:
    return {
        "seuil_1_max": 70000.0,
        "seuil_1_forfait": 5000.0,
        "seuil_2_max": 150000.0,
        "seuil_2_taux": 0.07,
        "seuil_3_max": 400000.0,
        "seuil_3_taux": 0.06,
        "seuil_4_taux": 0.05,
    }


def default_notaire_params() -> dict:
    return {
        "emol_seuil_1_max": 6500.0,
        "emol_taux_1": 0.03870,
        "emol_seuil_2_max": 17000.0,
        "emol_taux_2": 0.01596,
        "emol_seuil_3_max": 60000.0,
        "emol_taux_3": 0.01064,
        "emol_taux_4": 0.00799,
        "formalites_fixes": 850.0,
        "debours_fixes": 400.0,
        "droits_taux": 0.063185,
        "securite_taux": 0.001,
        "tva_taux": 0.20,
        "mobilier_plafond_taux": 0.05,
    }


def default_config() -> dict:
    return {
        "mandat": "1234 N 5678",
        "client_id": "00000-2026",
        "mode_honoraires": "bareme",
        "prix_net_vendeur_initial": 250000.0,
        "honoraires_agence_taux": 0.05,
        "honoraires_agence_taux_fixe": 0.0,
        "honoraires_agence_forfait": 0.0,
        "honoraires_agence_forfait_taux": 0.0,
        "mobilier_montant": 0.0,
    }


def save_config_file(filepath: str, config: dict) -> None:
    folder = os.path.dirname(filepath)
    if folder:
        os.makedirs(folder, exist_ok=True)

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)


def load_config_file(filepath: str) -> dict:
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def ensure_default_config_file() -> None:
    ensure_config_dir()
    default_file = get_default_config_file()
    if not os.path.exists(default_file):
        save_config_file(default_file, default_config())


def write_default_profile(profile_file: str) -> None:
    folder = os.path.dirname(profile_file)
    if folder:
        os.makedirs(folder, exist_ok=True)

    bareme = default_honoraires_bareme()
    default_config_name = get_default_config_file().replace("\\", "/")
    app_title = get_default_app_title()

    with open(profile_file, "w", encoding="utf-8") as f:
        f.write("[app]\n")
        f.write(f'agence = "{get_default_app_agence()}"\n')
        f.write(f'title = "{app_title}"\n\n')

        f.write("[config]\n")
        f.write(f'name = "{default_config_name}"\n\n')

        f.write("[honoraires]\n")
        f.write(f"seuil_1_max = {bareme['seuil_1_max']}\n")
        f.write(f"seuil_1_forfait = {bareme['seuil_1_forfait']}\n")
        f.write(f"seuil_2_max = {bareme['seuil_2_max']}\n")
        f.write(f"seuil_2_taux = {bareme['seuil_2_taux']}\n")
        f.write(f"seuil_3_max = {bareme['seuil_3_max']}\n")
        f.write(f"seuil_3_taux = {bareme['seuil_3_taux']}\n")
        f.write(f"seuil_4_taux = {bareme['seuil_4_taux']}\n\n")

        notaire = default_notaire_params()
        f.write("[notaire]\n")
        f.write(f"emol_seuil_1_max = {notaire['emol_seuil_1_max']}\n")
        f.write(f"emol_taux_1 = {notaire['emol_taux_1']}\n")
        f.write(f"emol_seuil_2_max = {notaire['emol_seuil_2_max']}\n")
        f.write(f"emol_taux_2 = {notaire['emol_taux_2']}\n")
        f.write(f"emol_seuil_3_max = {notaire['emol_seuil_3_max']}\n")
        f.write(f"emol_taux_3 = {notaire['emol_taux_3']}\n")
        f.write(f"emol_taux_4 = {notaire['emol_taux_4']}\n")
        f.write(f"formalites_fixes = {notaire['formalites_fixes']}\n")
        f.write(f"debours_fixes = {notaire['debours_fixes']}\n")
        f.write(f"droits_taux = {notaire['droits_taux']}\n")
        f.write(f"securite_taux = {notaire['securite_taux']}\n")
        f.write(f"tva_taux = {notaire['tva_taux']}\n")
        f.write(f"mobilier_plafond_taux = {notaire['mobilier_plafond_taux']}\n")


def ensure_default_profile_file() -> None:
    default_profile_file = get_default_profile_file()
    if not os.path.exists(default_profile_file):
        write_default_profile(default_profile_file)


def load_raw_toml_file(filepath: str) -> dict:
    with open(filepath, "rb") as f:
        return tomllib.load(f)


def profile_from_toml_data(data: dict) -> dict:
    app_data = data.get("app", {})
    config_data = data.get("config", {})
    honoraires_data = data.get("honoraires", {})
    notaire_data = data.get("notaire", {})
    merged_honoraires = default_honoraires_bareme()
    merged_honoraires.update(honoraires_data)

    merged_notaire = default_notaire_params()
    merged_notaire.update(notaire_data)

    agence = app_data.get("agence", get_default_app_agence())
    title = app_data.get("title", get_default_app_title())

    return {
        "agence": agence,
        "title": title,
        "display_title": build_display_title(agence, title),
        "config_name": config_data.get("name", get_default_config_file()),
        "honoraires": merged_honoraires,
        "notaire": merged_notaire,
    }


def load_profile() -> dict:
    profile_file = get_profile_file()

    if not os.path.exists(profile_file):
        write_default_profile(profile_file)

    ensure_default_profile_file()
    data = load_raw_toml_file(profile_file)
    return profile_from_toml_data(data)


def load_default_profile() -> dict:
    ensure_default_profile_file()
    data = load_raw_toml_file(get_default_profile_file())
    return profile_from_toml_data(data)


def build_profile_editor_data(profile: dict) -> dict:
    return {
        "app": {
            "agence": profile["agence"],
            "title": profile["title"],
        },
        "config": {
            "name": profile["config_name"],
        },
        "honoraires": {
            "seuil_1_max": profile["honoraires"]["seuil_1_max"],
            "seuil_2_max": profile["honoraires"]["seuil_2_max"],
            "seuil_3_max": profile["honoraires"]["seuil_3_max"],
            "seuil_1_forfait": profile["honoraires"]["seuil_1_forfait"],
            "seuil_2_taux": profile["honoraires"]["seuil_2_taux"],
            "seuil_3_taux": profile["honoraires"]["seuil_3_taux"],
            "seuil_4_taux": profile["honoraires"]["seuil_4_taux"],
        },
        "notaire": {
            "emol_seuil_1_max": profile["notaire"]["emol_seuil_1_max"],
            "emol_taux_1": profile["notaire"]["emol_taux_1"],
            "emol_seuil_2_max": profile["notaire"]["emol_seuil_2_max"],
            "emol_taux_2": profile["notaire"]["emol_taux_2"],
            "emol_seuil_3_max": profile["notaire"]["emol_seuil_3_max"],
            "emol_taux_3": profile["notaire"]["emol_taux_3"],
            "emol_taux_4": profile["notaire"]["emol_taux_4"],
            "formalites_fixes": profile["notaire"]["formalites_fixes"],
            "debours_fixes": profile["notaire"]["debours_fixes"],
            "droits_taux": profile["notaire"]["droits_taux"],
            "securite_taux": profile["notaire"]["securite_taux"],
            "tva_taux": profile["notaire"]["tva_taux"],
            "mobilier_plafond_taux": profile["notaire"]["mobilier_plafond_taux"],
        },
    }

def save_profile_editor_data(profile_data: dict) -> None:
    profile_dict = {
        "app": {
            "agence": str(profile_data["app"]["agence"]),
            "title": str(profile_data["app"]["title"]),
        },
        "config": {
            "name": str(profile_data["config"]["name"]),
        },
        "honoraires": {
            "seuil_1_max": int(profile_data["honoraires"]["seuil_1_max"]),
            "seuil_1_forfait": int(profile_data["honoraires"]["seuil_1_forfait"]),
            "seuil_2_max": int(profile_data["honoraires"]["seuil_2_max"]),
            "seuil_2_taux": float(profile_data["honoraires"]["seuil_2_taux"]),
            "seuil_3_max": int(profile_data["honoraires"]["seuil_3_max"]),
            "seuil_3_taux": float(profile_data["honoraires"]["seuil_3_taux"]),
            "seuil_4_taux": float(profile_data["honoraires"]["seuil_4_taux"]),
        },
        "notaire": {
            "emol_seuil_1_max": int(profile_data["notaire"]["emol_seuil_1_max"]),
            "emol_taux_1": float(profile_data["notaire"]["emol_taux_1"]),
            "emol_seuil_2_max": int(profile_data["notaire"]["emol_seuil_2_max"]),
            "emol_taux_2": float(profile_data["notaire"]["emol_taux_2"]),
            "emol_seuil_3_max": int(profile_data["notaire"]["emol_seuil_3_max"]),
            "emol_taux_3": float(profile_data["notaire"]["emol_taux_3"]),
            "emol_taux_4": float(profile_data["notaire"]["emol_taux_4"]),
            "formalites_fixes": int(profile_data["notaire"]["formalites_fixes"]),
            "debours_fixes": int(profile_data["notaire"]["debours_fixes"]),
            "droits_taux": float(profile_data["notaire"]["droits_taux"]),
            "securite_taux": float(profile_data["notaire"]["securite_taux"]),
            "tva_taux": float(profile_data["notaire"]["tva_taux"]),
            "mobilier_plafond_taux": float(profile_data["notaire"]["mobilier_plafond_taux"]),
        },
    }

    with open(get_profile_file(), "w", encoding="utf-8") as f:
        toml.dump(profile_dict, f)


def apply_profile_to_session(profile: dict) -> None:
    st.session_state.app_agence = profile["agence"]
    st.session_state.app_title = profile["title"]
    st.session_state.app_display_title = profile["display_title"]
    st.session_state.init_file = profile["config_name"]
    st.session_state.honoraires_bareme = dict(profile["honoraires"])
    st.session_state.notaire_params = dict(profile["notaire"])


def ensure_session_defaults() -> None:
    cfg = default_config()

    st.session_state.setdefault("mandat", str(cfg["mandat"]))
    st.session_state.setdefault("client_id", str(cfg["client_id"]))
    st.session_state.setdefault("mode_honoraires", str(cfg["mode_honoraires"]))
    st.session_state.setdefault("prix_net_vendeur_initial", float(cfg["prix_net_vendeur_initial"]))

    st.session_state.setdefault("honoraires_agence_taux_pct", float(cfg["honoraires_agence_taux"]) * 100.0)
    st.session_state.setdefault("honoraires_agence_taux_fixe_pct", float(cfg["honoraires_agence_taux_fixe"]) * 100.0)
    st.session_state.setdefault("honoraires_agence_forfait_eur", float(cfg["honoraires_agence_forfait"]))
    st.session_state.setdefault("honoraires_agence_forfait_taux_pct", float(cfg["honoraires_agence_forfait_taux"]) * 100.0)

    st.session_state.setdefault("mobilier_montant_eur", float(cfg["mobilier_montant"]))

    st.session_state.setdefault("save_message", "")
    st.session_state.setdefault("upload_error", "")
    st.session_state.setdefault("show_open_dialog", False)
    st.session_state.setdefault("show_profile_dialog", False)
    st.session_state.setdefault("pending_load_default_config", False)


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


def euros_to_rate(prix_nv: float, montant: float) -> float:
    if prix_nv <= 0:
        return 0.0
    return montant / prix_nv


def rate_to_euros(prix_nv: float, taux: float) -> float:
    return prix_nv * taux


def compute_honoraires_bareme(prix_nv: float, bareme: dict) -> tuple[float, float]:
    s1 = float(bareme.get("seuil_1_max", 70000.0))
    f1 = float(bareme.get("seuil_1_forfait", 5000.0))
    s2 = float(bareme.get("seuil_2_max", 150000.0))
    t2 = float(bareme.get("seuil_2_taux", 0.07))
    s3 = float(bareme.get("seuil_3_max", 400000.0))
    t3 = float(bareme.get("seuil_3_taux", 0.06))
    t4 = float(bareme.get("seuil_4_taux", 0.05))

    if prix_nv < s1:
        montant = f1
    elif prix_nv <= s2:
        montant = prix_nv * t2
    elif prix_nv <= s3:
        montant = prix_nv * t3
    else:
        montant = prix_nv * t4

    taux = euros_to_rate(prix_nv, montant)
    return montant, taux


def compute_honoraires(
    prix_nv: float,
    mode_honoraires: str,
    honoraires_taux: float,
    honoraires_forfait: float,
    honoraires_forfait_taux_mem: float,
    bareme: dict,
) -> tuple[float, float]:
    if mode_honoraires == "bareme":
        return compute_honoraires_bareme(prix_nv, bareme)

    if mode_honoraires == "fixe":
        montant = rate_to_euros(prix_nv, honoraires_taux)
        return montant, honoraires_taux

    montant = honoraires_forfait
    taux = honoraires_forfait_taux_mem
    return montant, taux


def clamp_mobilier(prix_fai: float, mobilier: float, notaire_params: dict) -> float:
    plafond = float(notaire_params.get("mobilier_plafond_taux", 0.05)) * max(prix_fai, 0.0)
    return max(0.0, min(float(mobilier), plafond))


def calc_frais_notaire(prix_fai: float, mobilier: float, notaire_params: dict) -> dict:
    mobilier_retenu = clamp_mobilier(prix_fai, mobilier, notaire_params)
    base = max(0.0, prix_fai - mobilier_retenu)

    s1 = float(notaire_params.get("emol_seuil_1_max", 6500.0))
    t1 = float(notaire_params.get("emol_taux_1", 0.03870))
    s2 = float(notaire_params.get("emol_seuil_2_max", 17000.0))
    t2 = float(notaire_params.get("emol_taux_2", 0.01596))
    s3 = float(notaire_params.get("emol_seuil_3_max", 60000.0))
    t3 = float(notaire_params.get("emol_taux_3", 0.01064))
    t4 = float(notaire_params.get("emol_taux_4", 0.00799))

    emol = 0.0
    emol += min(base, s1) * t1
    emol += max(0.0, min(base, s2) - s1) * t2
    emol += max(0.0, min(base, s3) - s2) * t3
    emol += max(0.0, base - s3) * t4
    emol = round(emol)

    formalites = round(float(notaire_params.get("formalites_fixes", 850.0)))
    debours = round(float(notaire_params.get("debours_fixes", 400.0)))
    droits = round(base * float(notaire_params.get("droits_taux", 0.063185)))
    securite = round(base * float(notaire_params.get("securite_taux", 0.001)))

    total_1 = emol + formalites
    tva = round(total_1 * float(notaire_params.get("tva_taux", 0.20)))
    total_2 = droits + securite + tva
    # frais = round(total_1 + total_2 + debours)
    frais = round((total_1 + total_2 + debours) / 100.0) * 100
    pct_prix = round(100.0 * frais / prix_fai, 1) if prix_fai > 0 else 0.0

    return {
        "prix_fai": round(prix_fai),
        "mobilier_declare": round(mobilier),
        "mobilier_retenu": round(mobilier_retenu),
        "base_calcul": round(base),
        "emoluments": emol,
        "formalites": formalites,
        "total_1": total_1,
        "droits": droits,
        "securite": securite,
        "tva": tva,
        "total_2": total_2,
        "debours": debours,
        "frais": frais,
        "pct_prix": pct_prix,
    }


def load_config_into_session(cfg: dict) -> None:
    default_cfg = default_config()

    st.session_state.mandat = str(cfg.get("mandat", default_cfg["mandat"]))
    st.session_state.client_id = str(cfg.get("client_id", default_cfg["client_id"]))

    mode_honoraires = str(cfg.get("mode_honoraires", default_cfg["mode_honoraires"])).lower()
    if mode_honoraires not in ("bareme", "fixe", "forfait"):
        mode_honoraires = default_cfg["mode_honoraires"]
    st.session_state.mode_honoraires = mode_honoraires

    st.session_state.prix_net_vendeur_initial = float(
        cfg.get("prix_net_vendeur_initial", default_cfg["prix_net_vendeur_initial"])
    )

    st.session_state.honoraires_agence_taux_pct = float(
        cfg.get("honoraires_agence_taux", default_cfg["honoraires_agence_taux"])
    ) * 100.0

    st.session_state.honoraires_agence_taux_fixe_pct = float(
        cfg.get(
            "honoraires_agence_taux_fixe",
            cfg.get("honoraires_agence_taux", default_cfg["honoraires_agence_taux_fixe"]),
        )
    ) * 100.0

    st.session_state.honoraires_agence_forfait_eur = float(
        cfg.get("honoraires_agence_forfait", default_cfg["honoraires_agence_forfait"])
    )

    forfait_taux_cfg = float(
        cfg.get(
            "honoraires_agence_forfait_taux",
            euros_to_rate(
                st.session_state.prix_net_vendeur_initial,
                st.session_state.honoraires_agence_forfait_eur,
            ),
        )
    )
    st.session_state.honoraires_agence_forfait_taux_pct = forfait_taux_cfg * 100.0

    st.session_state.mobilier_montant_eur = float(
        cfg.get("mobilier_montant", default_cfg["mobilier_montant"])
    )


def current_config_from_session() -> dict:
    ensure_session_defaults()

    return {
        "mandat": st.session_state.mandat,
        "client_id": st.session_state.client_id,
        "mode_honoraires": st.session_state.mode_honoraires,
        "prix_net_vendeur_initial": float(st.session_state.prix_net_vendeur_initial),
        "honoraires_agence_taux": float(st.session_state.honoraires_agence_taux_pct) / 100.0,
        "honoraires_agence_taux_fixe": float(st.session_state.honoraires_agence_taux_fixe_pct) / 100.0,
        "honoraires_agence_forfait": float(st.session_state.honoraires_agence_forfait_eur),
        "honoraires_agence_forfait_taux": float(st.session_state.honoraires_agence_forfait_taux_pct) / 100.0,
        "mobilier_montant": float(st.session_state.mobilier_montant_eur),
    }


def config_to_json(config: dict) -> str:
    return json.dumps(config, ensure_ascii=False, sort_keys=True)


def get_current_save_path() -> str:
    ensure_session_defaults()
    mandat = sanitize_filename(st.session_state.mandat, fallback="mandat")
    return os.path.join(get_config_dir(), f"{mandat}.txt")


def save_current_config(show_message: bool = True) -> None:
    ensure_session_defaults()

    config = current_config_from_session()
    save_path = get_current_save_path()
    save_config_file(save_path, config)
    st.session_state.last_saved_config_json = config_to_json(config)
    st.session_state.last_saved_path = save_path
    st.session_state.pending_selected_config_file = save_path.replace("\\", "/")
    if show_message:
        st.session_state.save_message = f"Simulation sauvée : {save_path}"


def autosave_current_config_if_changed() -> None:
    config = current_config_from_session()
    current_json = config_to_json(config)
    save_path = get_current_save_path()
    last_json = st.session_state.get("last_saved_config_json", "")
    last_path = st.session_state.get("last_saved_path", "")

    if current_json != last_json or save_path != last_path:
        save_config_file(save_path, config)
        st.session_state.last_saved_config_json = current_json
        st.session_state.last_saved_path = save_path
        st.session_state.pending_selected_config_file = save_path.replace("\\", "/")


def apply_pending_selected_file() -> None:
    pending = st.session_state.get("pending_selected_config_file", None)
    if pending is not None:
        st.session_state.selected_config_file = pending
        st.session_state.selected_config_file_dialog = pending
        del st.session_state["pending_selected_config_file"]


def init_internal_tracking_state() -> None:
    if "_prev_mode_honoraires" not in st.session_state:
        st.session_state._prev_mode_honoraires = st.session_state.mode_honoraires

    if "_prev_prix_net_vendeur_initial" not in st.session_state:
        st.session_state._prev_prix_net_vendeur_initial = float(st.session_state.prix_net_vendeur_initial)

    if "_prev_honoraires_agence_forfait_eur" not in st.session_state:
        st.session_state._prev_honoraires_agence_forfait_eur = float(st.session_state.honoraires_agence_forfait_eur)


def sync_honoraires_state() -> None:
    current_mode = st.session_state.mode_honoraires
    current_prix_nv = float(st.session_state.prix_net_vendeur_initial)
    current_forfait = float(st.session_state.honoraires_agence_forfait_eur)

    prev_mode = st.session_state._prev_mode_honoraires
    prev_forfait = float(st.session_state._prev_honoraires_agence_forfait_eur)

    mode_changed = current_mode != prev_mode
    forfait_changed = current_forfait != prev_forfait

    if current_mode == "fixe" and mode_changed:
        last_fixed_pct = float(st.session_state.honoraires_agence_taux_fixe_pct)

        if last_fixed_pct <= 0:
            if prev_mode == "bareme":
                _, taux_bar = compute_honoraires_bareme(
                    current_prix_nv,
                    st.session_state.honoraires_bareme,
                )
                st.session_state.honoraires_agence_taux_pct = taux_bar * 100.0
                st.session_state.honoraires_agence_taux_fixe_pct = taux_bar * 100.0
            else:
                st.session_state.honoraires_agence_taux_fixe_pct = float(
                    st.session_state.honoraires_agence_taux_pct
                )
        else:
            st.session_state.honoraires_agence_taux_pct = last_fixed_pct

    if current_mode == "fixe":
        st.session_state.honoraires_agence_taux_fixe_pct = float(
            st.session_state.honoraires_agence_taux_pct
        )

    if current_mode == "forfait":
        if mode_changed or forfait_changed:
            st.session_state.honoraires_agence_forfait_taux_pct = euros_to_rate(
                current_prix_nv,
                current_forfait,
            ) * 100.0

    st.session_state._prev_mode_honoraires = current_mode
    st.session_state._prev_prix_net_vendeur_initial = current_prix_nv
    st.session_state._prev_honoraires_agence_forfait_eur = current_forfait


def build_dataframe(
    prix_nv_initial: float,
    mode_honoraires: str,
    honoraires_taux: float,
    honoraires_forfait: float,
    honoraires_forfait_taux_mem: float,
    mobilier_montant: float,
    honoraires_bareme: dict,
    notaire_params: dict,
) -> pd.DataFrame:
    rows = []

    for variation in range(0, -6, -1):
        coef = 1 + variation / 100.0
        prix_nv = prix_nv_initial * coef

        honoraires, taux_calcule = compute_honoraires(
            prix_nv=prix_nv,
            mode_honoraires=mode_honoraires,
            honoraires_taux=honoraires_taux,
            honoraires_forfait=honoraires_forfait,
            honoraires_forfait_taux_mem=honoraires_forfait_taux_mem,
            bareme=honoraires_bareme,
        )

        prix_fai = prix_nv + honoraires
        notaire_normal = calc_frais_notaire(prix_fai, 0.0, notaire_params)
        notaire_reduit = calc_frais_notaire(prix_fai, mobilier_montant, notaire_params)
        prix_total = prix_fai + notaire_normal["frais"]
        prix_total_reduit = prix_fai + notaire_reduit["frais"]

        rows.append(
            {
                "Variation": variation,
                "Prix net vendeur": prix_nv,
                "Honoraires": honoraires,
                "Taux honoraires": taux_calcule,
                "Prix FAI": prix_fai,
                "Frais de notaire": notaire_normal["frais"],
                "Frais de notaire réduits": notaire_reduit["frais"],
                "Mobilier retenu": notaire_reduit["mobilier_retenu"],
                "Prix total acquéreur": prix_total,
                "Prix total acquéreur avec frais de notaire réduit": prix_total_reduit,
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
        df["Prix total acquéreur"],
        marker="o",
        linewidth=params["line_width"],
        markersize=params["marker_size"],
        label="Prix total acquéreur",
    )
    ax.plot(
        df["Variation"],
        df["Prix total acquéreur avec frais de notaire réduit"],
        linestyle="--",
        marker="o",
        linewidth=params["line_width"],
        markersize=params["marker_size"],
        color="green",
        label="Prix total acquéreur avec frais de notaire réduit",
    )

    ax.set_xlim(0, -5)

    values = df[
        [
            "Prix net vendeur",
            "Prix FAI",
            "Prix total acquéreur",
            "Prix total acquéreur avec frais de notaire réduit",
        ]
    ]
    y_min_value = values.min().min()
    y_max_value = values.max().max()

    y_min = int(np.floor(y_min_value / 10000.0) * 10000) - 10000
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
        (line_total, "Prix total acquéreur"),
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

    for x, y in zip(df["Variation"], df["Prix total acquéreur avec frais de notaire réduit"]):
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

    now = datetime.now().strftime("%d/%m/%Y %H:%M")
    ax.set_xlabel("Variation du prix (%)", fontsize=params["axis_size"])
    ax.set_ylabel("Montant (K€)", fontsize=params["axis_size"])
    # ax.set_title(
    #     f"{chart_title} - édition du {now}",
    #     fontsize=params["title_size"],
    #     fontweight="bold",
    # )
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=params["legend_size"])

    fig.tight_layout()
    return fig


def build_pdf_bytes(
    fig,
    chart_title: str,
    df: pd.DataFrame,
    mandat: str,
    client_id: str,
    mode_honoraires: str,
    taux_courant: float,
    montant_courant: float,
) -> bytes:
    image_buffer = io.BytesIO()
    fig.savefig(image_buffer, format="png", dpi=220, bbox_inches="tight")
    image_buffer.seek(0)

    pdf_buffer = io.BytesIO()
    c = canvas.Canvas(pdf_buffer, pagesize=landscape(A4))
    width, height = landscape(A4)

    c.setFont("Helvetica-Bold", 18)
    c.drawString(30, height - 30, chart_title)

    c.setFont("Helvetica", 12)
    c.drawString(30, height - 48, f"Mandat : {mandat}")
    c.drawString(260, height - 48, f"Référence : {client_id}")

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

    mode_label = {
        "bareme": "barème",
        "fixe": "taux fixe",
        "forfait": "forfait",
    }.get(mode_honoraires, mode_honoraires)
    cfn_dd = st.session_state.get("current_frais_notaire_dialog_data", {})
    footer_text  = (
        f"Mode honoraires : {mode_label}   |   "
        f"Taux : {taux_courant * 100:.1f} %   |   "
        f"Honoraires : {montant_courant:,.0f} €".replace(",", " ")
    )
    # Ajout des frais de notaire
    if cfn_dd:
        frais_txt = (
            f"{cfn_dd.get('frais', 0):,.0f} € "
            f"({cfn_dd.get('pct_prix', 0):.1f} %)"
        ).replace(",", " ")

        footer_text += f"   |   Frais de notaire : {frais_txt}"

    c.setFont("Helvetica", 10)
    c.drawString(30, 25, footer_text)

    c.showPage()
    c.save()
    pdf_buffer.seek(0)
    return pdf_buffer.getvalue()


def load_selected_config_file(filepath: str | None = None) -> None:
    selected_file = filepath or st.session_state.get("selected_config_file", "")
    if not selected_file:
        st.session_state.upload_error = "Aucun fichier sélectionné."
        return

    if not os.path.exists(selected_file):
        st.session_state.upload_error = f"Fichier introuvable : {selected_file}"
        return

    st.session_state.pending_load_config_file = selected_file
    st.session_state.upload_error = ""
    st.session_state.save_message = ""


def apply_pending_loaded_config() -> None:
    pending_file = st.session_state.get("pending_load_config_file", None)

    if pending_file is None:
        return

    try:
        cfg = load_config_file(pending_file)
        load_config_into_session(cfg)
        init_internal_tracking_state()

        st.session_state.last_saved_config_json = config_to_json(current_config_from_session())
        st.session_state.last_saved_path = get_current_save_path()
        st.session_state.upload_error = ""
        st.session_state.pending_selected_config_file = pending_file
        st.session_state.save_message = f"Simulation chargée : {pending_file}"
    except Exception as exc:
        st.session_state.upload_error = f"Simulation invalide : {exc}"
    finally:
        if "pending_load_config_file" in st.session_state:
            del st.session_state["pending_load_config_file"]


def load_default_config() -> None:
    st.session_state.pending_load_default_config = True
    st.session_state.upload_error = ""
    st.session_state.save_message = ""


def apply_pending_default_config() -> None:
    if not st.session_state.get("pending_load_default_config", False):
        return

    try:
        cfg = default_config()
        load_config_into_session(cfg)
        init_internal_tracking_state()
        st.session_state.last_saved_config_json = config_to_json(current_config_from_session())
        st.session_state.last_saved_path = get_current_save_path()
        st.session_state.save_message = ""
        st.session_state.upload_error = ""
    finally:
        st.session_state.pending_load_default_config = False


def init_session_state(profile: dict) -> None:
    ensure_default_config_file()

    if "initialized" not in st.session_state:
        init_file = profile["config_name"]

        if os.path.exists(init_file):
            cfg = load_config_file(init_file)
        else:
            cfg = default_config()
            save_config_file(init_file, cfg)

        load_config_into_session(cfg)

        apply_profile_to_session(profile)
        st.session_state.init_file = init_file
        st.session_state.profile_editor_data = build_profile_editor_data(profile)
        st.session_state.profile_editor_defaults = build_profile_editor_data(load_default_profile())
        st.session_state.upload_error = ""
        st.session_state.save_message = ""
        st.session_state.initialized = True
        st.session_state.show_open_dialog = False
        st.session_state.show_profile_dialog = False
        st.session_state.pending_load_default_config = False

        init_internal_tracking_state()

        initial_config = current_config_from_session()
        st.session_state.last_saved_config_json = config_to_json(initial_config)
        st.session_state.last_saved_path = get_current_save_path()

        available_files = list_config_files()
        if init_file.replace("\\", "/") in available_files:
            st.session_state.selected_config_file = init_file.replace("\\", "/")
        elif available_files:
            st.session_state.selected_config_file = available_files[0]
        else:
            st.session_state.selected_config_file = ""

        st.session_state.selected_config_file_dialog = st.session_state.selected_config_file


def get_current_honoraires_display_values() -> tuple[float, float]:
    prix_nv = float(st.session_state.prix_net_vendeur_initial)
    mode = st.session_state.mode_honoraires
    taux = float(st.session_state.honoraires_agence_taux_pct) / 100.0
    forfait = float(st.session_state.honoraires_agence_forfait_eur)
    forfait_taux_mem = float(st.session_state.honoraires_agence_forfait_taux_pct) / 100.0
    bareme = st.session_state.honoraires_bareme

    montant, taux_affiche = compute_honoraires(
        prix_nv=prix_nv,
        mode_honoraires=mode,
        honoraires_taux=taux,
        honoraires_forfait=forfait,
        honoraires_forfait_taux_mem=forfait_taux_mem,
        bareme=bareme,
    )
    return montant, taux_affiche


def format_honoraires_caption(montant_courant: float, taux_courant: float) -> str:
    return f"Honoraires : {montant_courant:,.0f} €  ({taux_courant * 100:.1f} %)".replace(",", " ")

def format_notaire_caption(frais_notaire: dict) -> str:
    return (
        f"Frais de notaire : {frais_notaire['frais']:,.0f} €  ({frais_notaire['pct_prix']:.1f} %)"
        .replace(",", " ")
    )

def render_sidebar_messages(placeholder) -> None:
    if st.session_state.get("save_message"):
        placeholder.success(st.session_state.save_message)
    elif st.session_state.get("upload_error"):
        placeholder.error(st.session_state.upload_error)
    else:
        placeholder.empty()

@st.dialog("Estimation des frais de notaire")
def show_frais_notaire_dialog() -> None:
    import streamlit.components.v1 as components

    frais_notaire = st.session_state.get("current_frais_notaire_dialog_data", {})
    pct_prix = f"({frais_notaire['pct_prix']:.1f} %)"

    if not frais_notaire:
        st.info("Aucune donnée disponible.")
        return

    item_labels = {
        "prix_fai": "Prix FAI",
        "mobilier_declare": "Valeur mobilier déclarée",
        "mobilier_retenu": "Valeur mobilier retenue (5% FAI maxi)",
        "base_calcul": "Base de calcul (1-3)",
        "emoluments": "Emoluments du notaire",
        "formalites": "Formalites",
        "total_1": "Total notaire (3+4)",
        "droits": "Droits d'enregistrement",
        "securite": "Securite immobilière",
        "tva": "TVA (20%) sur Total notaire",
        "total_2": "Total taxes (6+7+8)",
        "debours": "Débours (Frais annexes)",
        "frais": f"Total (notaire+taxes+débours)   ~{pct_prix}",
    }

    display_order = [
        "prix_fai",
        "mobilier_declare",
        "mobilier_retenu",
        "base_calcul",
        "emoluments",
        "formalites",
        "total_1",
        "droits",
        "securite",
        "tva",
        "total_2",
        "debours",
        "frais",
    ]

    # lignes à mettre en valeur (gras + espacement)
    bold_rows_1_based = {4, 7, 11, 13}

    def fmt_eur(value) -> str:
        return f"{int(round(float(value))):,}".replace(",", " ") + " €"

    table_rows = []
    for idx, key in enumerate(display_order, start=1):
        if key not in frais_notaire:
            continue

        label = item_labels[key]
        value = fmt_eur(frais_notaire[key])

        row_style = ""
        if idx in bold_rows_1_based:
            row_style = "font-weight:700; padding-top:5px; padding-bottom:30px;"

        table_rows.append(
            f"""
            <tr>
                <td style="padding:8px 10px; border-bottom:1px solid #333; color:#888; {row_style}">
                    {idx}
                </td>
                <td style="padding:8px 12px; border-bottom:1px solid #333; {row_style}">
                    {label}
                </td>
                <td style="padding:8px 12px; border-bottom:1px solid #333; text-align:right; white-space:nowrap; font-variant-numeric:tabular-nums; {row_style}">
                    {value}
                </td>
            </tr>
            """
        )

    html = f"""
    <html>
    <head>
        <style>
            body {{
                margin: 0;
                font-family: sans-serif;
            }}
            .wrapper {{
                max-height: 520px;
                overflow-y: auto;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                font-size: 15px;
            }}
        </style>
    </head>
    <body>
        <div class="wrapper">
            <table>
                <tbody>
                    {''.join(table_rows)}
                </tbody>
            </table>
        </div>
    </body>
    </html>
    """

    components.html(html, height=560, scrolling=False)

def format_param_label(param_name: str) -> str:
    # mapping explicite des clés → libellés métier
    mapping = {
    # honoraires
    "seuil_1_max": "Seuil 1 max (en €)",
    "seuil_2_max": "Seuil 2 max (en €)",
    "seuil_3_max": "Seuil 3 max (en €)",
    "seuil_1_forfait": "Seuil 1 forfait (en €)",
    "seuil_2_taux": "Seuil 2 taux",
    "seuil_3_taux": "Seuil 3 taux",
    "seuil_4_taux": "Seuil 4 taux",

    # notaire
    "emol_seuil_1_max": "Émolument seuil 1 max (en €)",
    "emol_taux_1": "Émolument taux 1",
    "emol_seuil_2_max": "Émolument seuil 2 max (en €)",
    "emol_taux_2": "Émolument taux 2",
    "emol_seuil_3_max": "Émolument seuil 3 max (en €)",
    "emol_taux_3": "Émolument taux 3",
    "emol_taux_4": "Émolument taux 4",
    "formalites_fixes": "Formalités fixes (en €)",
    "debours_fixes": "Débours fixes (en €)",
    "droits_taux": "Droits taux",
    "securite_taux": "Sécurité taux",
    "tva_taux": "TVA taux",
    "mobilier_plafond_taux": "Mobilier plafond taux",

    # app / config
    "agence": "Agence",
    "title": "Titre",
    "name": "Nom",
    }

    if param_name in mapping:
        return mapping[param_name]

    label = param_name.replace("_", " ")
    return label[:1].upper() + label[1:] if label else label

@st.dialog("Paramètres", width="medium")
def show_profile_dialog() -> None:
    def is_text_param(param_name: str) -> bool:
        return param_name in ["agence", "title", "name"]

    def is_percent_param(param_name: str) -> bool:
        return "taux" in param_name

    def is_int_param(param_name: str) -> bool:
        return (not is_text_param(param_name)) and (not is_percent_param(param_name))

    editor_data = st.session_state.get(
        "profile_editor_data",
        build_profile_editor_data(load_profile()),
    )
    default_data = st.session_state.get(
        "profile_editor_defaults",
        build_profile_editor_data(load_default_profile()),
    )
    widget_rev = st.session_state.get("profile_editor_widget_rev", 0)

    st.caption("Modification du fichier profile.toml utilisé par l'application.")

    section_labels = {
        "app": "Application",
        "config": "Configuration",
        "honoraires": "Barème honoraires",
        "notaire": "Frais de notaire",
    }

    ordered_sections = ["app", "config", "honoraires", "notaire"]
    tab_labels = [section_labels[name] for name in ordered_sections]
    tabs = st.tabs(tab_labels)

    for tab, section_name in zip(tabs, ordered_sections):
        section_values = editor_data[section_name]

        with tab:
            header_cols = st.columns([1.5, 2.2, 1.0])
            header_cols[0].markdown("**Paramètre**")
            header_cols[1].markdown("**Valeur**")
            header_cols[2].markdown("**Action**")

            for param_name in section_values.keys():
                row_cols = st.columns([1.5, 2.2, 1.0])

                default_value = default_data[section_name][param_name]
                current_value = editor_data[section_name][param_name]
                widget_key = f"profile_edit::{widget_rev}::{section_name}::{param_name}"

                with row_cols[0]:
                    st.write(format_param_label(param_name))

                with row_cols[1]:
                    if is_text_param(param_name):
                        edited_value = st.text_input(
                            label=f"{section_name}.{param_name}",
                            value=str(current_value),
                            label_visibility="collapsed",
                            key=widget_key,
                        )

                    elif is_percent_param(param_name):
                        try:
                            numeric_value = float(current_value)
                        except (TypeError, ValueError):
                            numeric_value = float(default_value)

                        display_value = round(numeric_value * 100.0, 6)

                        edited_display = st.number_input(
                            label=f"{section_name}.{param_name}",
                            value=float(display_value),
                            step=0.000001,
                            format="%.6f",
                            label_visibility="collapsed",
                            key=widget_key,
                        )

                        edited_value = round(float(edited_display) / 100.0, 12)

                    else:
                        try:
                            numeric_value = int(round(float(current_value)))
                        except (TypeError, ValueError):
                            numeric_value = int(round(float(default_value)))

                        edited_display = st.number_input(
                            label=f"{section_name}.{param_name}",
                            value=int(numeric_value),
                            step=1,
                            format="%d",
                            label_visibility="collapsed",
                            key=widget_key,
                        )

                        edited_value = int(edited_display)

                    editor_data[section_name][param_name] = edited_value

                with row_cols[2]:
                    if st.button(
                        "Par défaut",
                        key=f"profile_default::{section_name}::{param_name}",
                        use_container_width=True,
                    ):
                        editor_data[section_name][param_name] = default_value
                        st.session_state.profile_editor_data = editor_data
                        st.session_state.profile_editor_widget_rev = widget_rev + 1
                        st.rerun()

    st.session_state.profile_editor_data = editor_data

    btn_col_1, btn_col_2, btn_col_3 = st.columns(3)

    with btn_col_1:
        if st.button("Par défaut", key="profile_defaults_all", use_container_width=True):
            defaults = build_profile_editor_data(load_default_profile())
            st.session_state.profile_editor_defaults = defaults
            st.session_state.profile_editor_data = defaults
            st.session_state.profile_editor_widget_rev = widget_rev + 1
            st.rerun()

    with btn_col_2:
        if st.button("Appliquer", key="profile_apply", type="primary", use_container_width=True):
            profile_data = st.session_state.profile_editor_data
            save_profile_editor_data(profile_data)
            applied_profile = load_profile()
            apply_profile_to_session(applied_profile)
            st.session_state.profile_editor_data = build_profile_editor_data(applied_profile)
            st.session_state.profile_editor_defaults = build_profile_editor_data(load_default_profile())
            st.session_state.profile_editor_widget_rev = widget_rev + 1
            # st.session_state.save_message = f"Paramètres appliqués : {get_profile_file()}"
            st.session_state.show_profile_dialog = False
            st.rerun()

    with btn_col_3:
        if st.button("Annuler", key="profile_cancel", use_container_width=True):
            current_profile = load_profile()
            st.session_state.profile_editor_data = build_profile_editor_data(current_profile)
            st.session_state.profile_editor_defaults = build_profile_editor_data(load_default_profile())
            st.session_state.profile_editor_widget_rev = widget_rev + 1
            st.session_state.show_profile_dialog = False
            st.rerun()

@st.dialog("Choisir une simulation")
def open_config_dialog() -> None:
    config_files = list_config_files()
    if not config_files:
        config_files = [""]

    current_selected = st.session_state.get("selected_config_file_dialog", "")
    if current_selected not in config_files:
        current_selected = config_files[0]

    selected = st.selectbox(
        "Fichier de simulation",
        options=config_files,
        index=config_files.index(current_selected) if current_selected in config_files else 0,
        format_func=lambda x: os.path.basename(x) if x else "(aucun fichier)",
        label_visibility="collapsed",
        key="dialog_file_selector_widget",
    )

    col_ok, col_cancel = st.columns(2)

    with col_ok:
        if st.button(
            "Ok",
            key="btn_load_selected_config_dialog",
            use_container_width=True,
            disabled=not bool(selected),
        ):
            st.session_state.selected_config_file_dialog = selected
            load_selected_config_file(selected)
            st.session_state.show_open_dialog = False
            st.rerun()

    with col_cancel:
        if st.button(
            "Annuler",
            key="btn_cancel_selected_config_dialog",
            use_container_width=True,
        ):
            st.session_state.show_open_dialog = False
            st.rerun()

def sidebar_action_controls() -> None:
    config = current_config_from_session()
    safe_file_name = sanitize_filename(config["mandat"], fallback="mandat")
    config_bytes = json.dumps(config, ensure_ascii=False, indent=2).encode("utf-8")

    icon_col_new, icon_col_open, icon_col_save, icon_col_download, icon_col_settings = st.sidebar.columns(5)

    with icon_col_new:
        st.button(
            "",
            key="btn_new_config",
            on_click=load_default_config,
            icon=":material/add:",
            width="stretch",
            help="Nouvelle simulation",
        )

    with icon_col_download:
        st.download_button(
            label="",
            key="btn_download_config",
            data=config_bytes,
            file_name=f"{safe_file_name}.txt",
            mime="text/plain",
            icon=":material/download:",
            width="stretch",
            help="Télécharger la simulation",
        )

    with icon_col_save:
        st.button(
            "",
            key="btn_save_config",
            on_click=save_current_config,
            kwargs={"show_message": True},
            icon=":material/save:",
            width="stretch",
            help="Sauver la simulation",
        )

    with icon_col_open:
        if st.button(
            "",
            key="btn_open_config_dialog",
            icon=":material/folder_open:",
            width="stretch",
            help="Ouvrir une simulation",
        ):
            st.session_state.selected_config_file_dialog = st.session_state.get(
                "selected_config_file",
                st.session_state.get("selected_config_file_dialog", ""),
            )
            st.session_state.show_open_dialog = True
            st.rerun()

    with icon_col_settings:
        if st.button(
            "",
            key="btn_open_profile_dialog",
            icon=":material/settings:",
            width="stretch",
            help="Paramètres",
        ):
            st.session_state.profile_editor_data = build_profile_editor_data(load_profile())
            st.session_state.profile_editor_defaults = build_profile_editor_data(load_default_profile())
            st.session_state.show_profile_dialog = True
            st.rerun()


def sidebar_parameter_controls() -> None:
    st.sidebar.header("Simulations")
    sidebar_action_controls()

    col_mandat, col_ref = st.sidebar.columns(2)
    with col_mandat:
        st.text_input(
            "Mandat",
            key="mandat",
            help="Référence du mandat.",
        )

    with col_ref:
        st.text_input(
            "Référence",
            key="client_id",
            help="Référence du client.",
        )

    st.sidebar.number_input(
        "Prix net vendeur initial (€)",
        min_value=0.0,
        step=10000.0,
        key="prix_net_vendeur_initial",
        format="%.0f",
    )

    st.sidebar.segmented_control(
        "Mode de calcul des honoraires",
        options=["bareme", "fixe", "forfait"],
        format_func=lambda x: {
            "bareme": "Barème",
            "fixe": "Taux fixe",
            "forfait": "Forfait",
        }[x],
        key="mode_honoraires",
        selection_mode="single",
        width="stretch",
    )

    sync_honoraires_state()
    montant_affiche_eur, taux_affiche = get_current_honoraires_display_values()
    taux_affiche_pct = taux_affiche * 100.0

    col_taux, col_montant = st.sidebar.columns(2)

    with col_taux:
        if st.session_state.mode_honoraires == "fixe":
            st.number_input(
                "Honoraires (%)",
                min_value=0.0,
                max_value=100.0,
                step=0.1,
                key="honoraires_agence_taux_pct",
                format="%.1f",
                help="Taux négocié appliqué au prix net vendeur.",
            )
            sync_honoraires_state()
            montant_affiche_eur, taux_affiche = get_current_honoraires_display_values()
        else:
            st.number_input(
                "Honoraires (%)",
                min_value=0.0,
                max_value=100.0,
                value=float(taux_affiche_pct),
                step=0.1,
                format="%.1f",
                disabled=True,
                help=(
                    "Taux calculé automatiquement par le barème."
                    if st.session_state.mode_honoraires == "bareme"
                    else "Taux coreespondant au forfait."
                ),
            )

    with col_montant:
        if st.session_state.mode_honoraires == "forfait":
            st.number_input(
                "Honoraires (€)",
                min_value=0.0,
                step=1000.0,
                key="honoraires_agence_forfait_eur",
                format="%.0f",
                help="Honoraires forfaitaires en euros.",
            )
            sync_honoraires_state()
            montant_affiche_eur, taux_affiche = get_current_honoraires_display_values()
        else:
            st.number_input(
                "Honoraires (€)",
                min_value=0.0,
                value=float(montant_affiche_eur),
                step=1000.0,
                format="%.0f",
                disabled=True,
                help="Montant recalculé automatiquement.",
            )

    prix_fai_courant = float(st.session_state.prix_net_vendeur_initial) + float(montant_affiche_eur)
    mobilier_max = clamp_mobilier(
        prix_fai_courant,
        prix_fai_courant,
        st.session_state.notaire_params,
    )

    col_frais_notaire, col_mobilier  = st.sidebar.columns(2)
    with col_mobilier:
        st.number_input(
            "Mobilier (€)",
            min_value=0.0,
            # max_value=float(mobilier_max),
            step=1000.0,
            key="mobilier_montant_eur",
            format="%.0f",
            help="Montant du mobilier retenu pour réduire l'assiette, plafonné à 5 % du prix FAI.",
        )

    frais_notaire_courant = calc_frais_notaire(
        prix_fai_courant,
        float(st.session_state.mobilier_montant_eur),
        st.session_state.notaire_params,
    )

    with col_frais_notaire:
        st.number_input(
            "Frais de notaire (€)",
            min_value=0.0,
            value=float(frais_notaire_courant["frais"]),
            step=1000.0,
            format="%.0f",
            disabled=True,
            help="Montant calculé automatiquement.",
        )

    st.sidebar.caption(format_honoraires_caption(montant_affiche_eur, taux_affiche))
    st.session_state.current_frais_notaire_dialog_data = frais_notaire_courant
    if st.sidebar.button(
        format_notaire_caption(frais_notaire_courant),
        key="btn_show_frais_notaire_dialog",
        type="tertiary",
        help="Afficher le détail du calcul des frais de notaire.",
        width="stretch",
    ):
        show_frais_notaire_dialog()


def main() -> None:
    if "profile_editor_widget_rev" not in st.session_state:
        st.session_state.profile_editor_widget_rev = 0

    profile = load_profile()

    st.set_page_config(
        page_title=profile["display_title"],
        page_icon="🏠",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    init_session_state(profile)
    ensure_session_defaults()

    apply_pending_selected_file()
    apply_pending_default_config()
    apply_pending_loaded_config()

    sidebar_parameter_controls()

    if st.session_state.get("show_open_dialog", False):
        open_config_dialog()

    if st.session_state.get("show_profile_dialog", False):
        show_profile_dialog()

    autosave_current_config_if_changed()

    sidebar_messages_placeholder = st.sidebar.empty()
    render_sidebar_messages(sidebar_messages_placeholder)

    st.title(st.session_state.app_display_title)

    subtitle = f"Mandat : {st.session_state.mandat}"
    if st.session_state.client_id.strip():
        subtitle += f", Référence : {st.session_state.client_id}"
    st.subheader(subtitle)

    display_mode = infer_display_mode()

    prix_nv_initial = float(st.session_state.prix_net_vendeur_initial)
    mode_honoraires = st.session_state.mode_honoraires
    honoraires_taux = float(st.session_state.honoraires_agence_taux_pct) / 100.0
    honoraires_forfait = float(st.session_state.honoraires_agence_forfait_eur)
    honoraires_forfait_taux_mem = float(st.session_state.honoraires_agence_forfait_taux_pct) / 100.0
    mobilier_montant = float(st.session_state.mobilier_montant_eur)
    honoraires_bareme = st.session_state.honoraires_bareme
    notaire_params = st.session_state.notaire_params

    df = build_dataframe(
        prix_nv_initial=prix_nv_initial,
        mode_honoraires=mode_honoraires,
        honoraires_taux=honoraires_taux,
        honoraires_forfait=honoraires_forfait,
        honoraires_forfait_taux_mem=honoraires_forfait_taux_mem,
        mobilier_montant=mobilier_montant,
        honoraires_bareme=honoraires_bareme,
        notaire_params=notaire_params,
    )

    fig = plot_chart(
        df=df,
        chart_title=st.session_state.app_display_title,
        display_mode=display_mode,
    )
    st.pyplot(fig, width="stretch")

    montant_courant, taux_courant = get_current_honoraires_display_values()

    pdf_bytes = build_pdf_bytes(
        fig=fig,
        chart_title=st.session_state.app_display_title,
        df=df,
        mandat=st.session_state.mandat,
        client_id=st.session_state.client_id,
        mode_honoraires=mode_honoraires,
        taux_courant=taux_courant,
        montant_courant=montant_courant,
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

        money_cols = [
            "Prix net vendeur",
            "Honoraires",
            "Prix FAI",
            "Prix total acquéreur",
            "Prix total acquéreur avec frais de notaire réduit",
        ]
        for col in money_cols:
            df_display[col] = df_display[col] / 1000.0

        df_display["Variation"] = df_display["Variation"].map(lambda x: f"{x:.0f}")
        df_display["Taux honoraires"] = df_display["Taux honoraires"].map(lambda x: f"{x * 100:.1f}")

        for col in money_cols:
            df_display[col] = df_display[col].map(
                lambda x: f"{x:,.2f}".replace(",", "X").replace(".", ",").replace("X", " ")
            )

        df_display.columns = [
            "Variation (en %)",
            "Prix net vendeur (K€)",
            "Honoraires (K€)",
            "Taux honoraires (%)",
            "Prix FAI (K€)",
            "Frais de notaire (K€)",
            "Frais de notaire réduits (K€)",
            "Mobilier retenu (K€)",
            "Prix total acquéreur (K€)",
            "Prix total acquéreur avec frais réduits (K€)",
        ]
        st.dataframe(df_display, width="stretch", hide_index=True)

        st.caption(
            format_honoraires_caption(montant_courant, taux_courant)
        )

    st.caption(f"Format détecté automatiquement : {display_mode}")


if __name__ == "__main__":
    main()