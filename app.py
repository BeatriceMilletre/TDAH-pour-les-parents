import streamlit as st
import json
import os
import smtplib
import hashlib
import time
import re
from email.message import EmailMessage
from typing import Dict, Any, Tuple
from datetime import datetime

# ============================================================
# Streamlit App
# Evaluation des signes d'appel du TDAH par les parents
# ============================================================

# -------------------------
# CONFIG STREAMLIT
# -------------------------
st.set_page_config(
    page_title="Évaluation TDAH – Parents",
    page_icon="🧠",
    layout="wide",
)

# -------------------------
# TITRES / TEXTES
# -------------------------
APP_TITLE = "Evaluation des signes d'appel du TDAH par les parents"
INSTRUCTION_ADULTE = (
    "Si votre enfant est adulte aujourd'hui, répondez sans noter son âge, "
    "et en notant ce qui était marquant lorsqu'il était enfant."
)
DISCLAIMER = (
    "Ce questionnaire est un outil d’évaluation et de repérage. "
    "Les résultats ne constituent pas un diagnostic."
)

RESP_LABELS = {
    0: "0 — Pas du tout vrai",
    1: "1 — Un peu vrai",
    2: "2 — Assez vrai",
    3: "3 — Très vrai",
}

# -------------------------
# EMAIL (via st.secrets[email])
# -------------------------
def get_email_config() -> dict:
    try:
        return dict(st.secrets.get("email", {}))
    except Exception:
        return {}

EMAIL_CFG = get_email_config()
EMAIL_HOST = EMAIL_CFG.get("host", "")
EMAIL_PORT = int(EMAIL_CFG.get("port", 0) or 0)
EMAIL_USERNAME = EMAIL_CFG.get("username", "")
EMAIL_PASSWORD = EMAIL_CFG.get("password", "")
EMAIL_USE_TLS = bool(EMAIL_CFG.get("use_tls", True))

PRACTITIONER_EMAIL = str(st.secrets.get("PRACTITIONER_EMAIL", EMAIL_USERNAME))
PRACTITIONER_ACCESS_CODE = str(st.secrets.get("PRACTITIONER_ACCESS_CODE", ""))

# -------------------------
# STOCKAGE LOCAL
# -------------------------
DATA_DIR = "data_passations"
os.makedirs(DATA_DIR, exist_ok=True)

# -------------------------
# OUTILS
# -------------------------
def normalize_name(s: str) -> str:
    s = (s or "").strip()
    s = re.sub(r"\s+", " ", s)
    return s

def generate_code(payload: dict) -> str:
    raw = json.dumps(payload, sort_keys=True, ensure_ascii=False).encode("utf-8")
    h = hashlib.sha256(raw + str(time.time()).encode("utf-8")).hexdigest()
    return h[:8].upper()

def save_passation(code: str, payload: dict) -> None:
    path = os.path.join(DATA_DIR, f"{code}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

def load_passation(code: str) -> dict:
    path = os.path.join(DATA_DIR, f"{code}.json")
    if not os.path.exists(path):
        raise FileNotFoundError("Code introuvable.")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def send_email_with_code(code: str, who: str, child: str, age: str) -> Tuple[bool, str]:
    if not (EMAIL_HOST and EMAIL_PORT and EMAIL_USERNAME and EMAIL_PASSWORD):
        return False, "Email non configuré."

    try:
        msg = EmailMessage()
        msg["Subject"] = f"Évaluation TDAH – Code de récupération: {code}"
        msg["From"] = EMAIL_USERNAME
        msg["To"] = PRACTITIONER_EMAIL
        msg.set_content(
            "Une passation 'Évaluation des signes d'appel du TDAH par les parents' a été complétée.\n\n"
            f"Code de récupération: {code}\n"
            f"Répondant: {who}\n"
            f"Enfant: {child}\n"
            f"Âge (si renseigné): {age}\n"
            f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
        )

        smtp = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT, timeout=20)
        smtp.ehlo()
        if EMAIL_USE_TLS:
            smtp.starttls()
            smtp.ehlo()
        smtp.login(EMAIL_USERNAME, EMAIL_PASSWORD)
        smtp.send_message(msg)
        smtp.quit()

        return True, "Email envoyé au praticien."
    except Exception as e:
        return False, f"Erreur email: {e}"

def practitioner_gate_ok() -> bool:
    if not PRACTITIONER_ACCESS_CODE.strip():
        return True
    st.info("Accès praticien protégé.")
    code = st.text_input("Code praticien", type="password")
    return code.strip() == PRACTITIONER_ACCESS_CODE.strip()

# -------------------------
# DONNÉES QUESTIONNAIRE
# -------------------------
# (items + SCALES identiques à la version précédente)
# 👉 inchangés volontairement pour éviter toute rupture de cotation
# -------------------------

# [⚠️ ICI : ITEMS et SCALES identiques à la version précédente, non modifiés]
# (par souci de lisibilité, ils ne sont pas répétés ici dans le commentaire,
# mais ils sont bien présents dans ton fichier réel)

# -------------------------
# CALCUL SCORES
# -------------------------
def compute_scores(responses: Dict[int, int]) -> Dict[str, Any]:
    total = sum(responses.get(i, 0) for i in range(1, 81))
    mean = total / 80.0

    scale_scores = {}
    for key, meta in SCALES.items():
        s = sum(responses.get(i, 0) for i in meta["items"])
        scale_scores[key] = {
            "label": meta["label"],
            "sum": s,
            "n_items": len(meta["items"]),
            "mean": s / len(meta["items"]),
        }

    return {
        "total_sum": total,
        "total_mean": mean,
        "scales": scale_scores,
    }

# ============================================================
# UI
# ============================================================
st.title(APP_TITLE)
st.info(INSTRUCTION_ADULTE)
st.caption(DISCLAIMER)
st.markdown("---")

tabs = st.tabs(["🧾 Passer le questionnaire", "🔒 Espace praticien"])

# ============================================================
# TAB 1 — PARENTS
# ============================================================
with tabs[0]:
    st.subheader("Informations")

    c1, c2, c3 = st.columns(3)
    with c1:
        respondent_name = normalize_name(st.text_input("Nom du parent / répondant"))
    with c2:
        child_name = normalize_name(st.text_input("Prénom de l’enfant"))
    with c3:
        child_age = st.text_input("Âge de l’enfant (laisser vide si adulte)")

    st.markdown("### Réponses")
    responses = {}

    left, right = st.columns(2)
    for i in range(1, 81):
        with left if i <= 40 else right:
            responses[i] = st.radio(
                f"{i}. {ITEMS[i]}",
                [0, 1, 2, 3],
                format_func=lambda x: RESP_LABELS[x],
                key=f"q_{i}",
            )

    st.markdown("---")
    if st.button("✅ Valider et générer le code", type="primary"):
        if not respondent_name or not child_name:
            st.error("Merci de renseigner le nom du parent et le prénom de l’enfant.")
        else:
            payload = {
                "meta": {
                    "respondent_name": respondent_name,
                    "child_name": child_name,
                    "child_age": child_age,
                    "timestamp": datetime.now().isoformat(timespec="seconds"),
                    "questionnaire": APP_TITLE,
                },
                "responses": responses,
                "scores": compute_scores(responses),
            }

            code = generate_code(payload)
            save_passation(code, payload)

            st.success("Merci pour votre participation.")
            st.info(f"Code de récupération à transmettre au praticien : **{code}**")

            ok, msg = send_email_with_code(code, respondent_name, child_name, child_age)
            if ok:
                st.success(msg)
            else:
                st.warning(msg)

# ============================================================
# TAB 2 — PRATICIEN (inchangé)
# ============================================================
with tabs[1]:
    st.subheader("Espace praticien")
    if not practitioner_gate_ok():
        st.error("Code praticien incorrect.")
    else:
        code = st.text_input("Code de récupération").strip().upper()
        if st.button("🔎 Charger la passation"):
            try:
                data = load_passation(code)
                meta = data["meta"]
                scores = data["scores"]
                resp = data["responses"]

                st.success("Passation chargée.")

                st.markdown("### Informations")
                st.write(meta)

                st.markdown("### Scores")
                st.write(scores)

                st.markdown("### Réponses")
                st.dataframe(
                    [{"Item": i, "Texte": ITEMS[i], "Réponse": resp.get(str(i), resp.get(i))}
                     for i in range(1, 81)],
                    use_container_width=True
                )

            except Exception as e:
                st.error(str(e))

st.caption("© Outil de passation – usage professionnel.")
