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
# "Evaluation des signes d'appel du TDAH par les parents"
# - Passation répondant : 80 items (0-3)
# - Calcul sous-échelles / indices selon mapping (A→N)
# - Génère un code de récupération + sauvegarde JSON
# - Espace praticien : code -> affichage résultats + export
#
# Email: lit la configuration dans st.secrets["email"] comme tes autres apps
# secrets.toml:
# [email]
# host="smtp.gmail.com"
# port=587
# username="beatricemilletre@gmail.com"
# password="xxxx xxxx xxxx xxxx"
# use_tls=true
#
# Optionnel:
# PRACTITIONER_EMAIL="beatricemilletre@gmail.com"
# PRACTITIONER_ACCESS_CODE="TON_CODE_PRATICIEN"
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

def save_passation(code: str, payload: dict) -> str:
    path = os.path.join(DATA_DIR, f"{code}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    return path

def load_passation(code: str) -> dict:
    path = os.path.join(DATA_DIR, f"{code}.json")
    if not os.path.exists(path):
        raise FileNotFoundError("Code introuvable.")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def send_email_with_code(code: str, who: str, child: str, age: str) -> Tuple[bool, str]:
    # Vérifie configuration
    if not (EMAIL_HOST and EMAIL_PORT and EMAIL_USERNAME and EMAIL_PASSWORD and PRACTITIONER_EMAIL):
        return False, "Email non configuré (secrets manquants)."

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
        try:
            smtp.ehlo()
            if EMAIL_USE_TLS:
                smtp.starttls()
                smtp.ehlo()
            smtp.login(EMAIL_USERNAME, EMAIL_PASSWORD)
            smtp.send_message(msg)
        finally:
            try:
                smtp.quit()
            except Exception:
                pass

        return True, "Email envoyé au praticien."
    except Exception as e:
        return False, f"Erreur email: {e}"

def practitioner_gate_ok() -> bool:
    # Si aucun code praticien configuré, accès libre à l’espace praticien.
    if not PRACTITIONER_ACCESS_CODE.strip():
        return True
    st.info("Accès praticien protégé.")
    code = st.text_input("Code praticien", type="password")
    return code.strip() == PRACTITIONER_ACCESS_CODE.strip()

# -------------------------
# DONNÉES DU QUESTIONNAIRE
# -------------------------
# Items 1..80 (texte) — tels que présents dans ton fichier (ou une version équivalente)
ITEMS: Dict[int, str] = {
    1: "A des accès de colère ou de méchanceté.",
    2: "S’active ou s’agite sans cesse.",
    3: "Argumente avec les adultes.",
    4: "A de la difficulté à attendre son tour dans les jeux ou les activités de groupe.",
    5: "Perturbe ou dérange les autres enfants.",
    6: "A une colère explosive.",
    7: "S’emporte facilement et perd rapidement son sang-froid.",
    8: "Ne parvient pas à rester assis (déplace ses mains, se tortille, bouge sur sa chaise).",
    9: "S’oppose à ce qu’on lui demande.",
    10: "Fait exprès de contrarier les gens.",
    11: "Fait des crises, des colères.",
    12: "Son humeur change soudainement et rapidement.",
    13: "Semble distrait, a de la difficulté à se concentrer ou à maintenir son attention.",
    14: "Se laisse facilement distraire par des stimulations extérieures.",
    15: "A de la difficulté à terminer ce qu’il/elle commence.",
    16: "A de la difficulté à suivre les consignes.",
    17: "A de la difficulté à écouter.",
    18: "N’est pas à l’écoute, n’entend pas ce qu’on lui dit.",
    19: "A de la difficulté à se concentrer, fait des erreurs d’inattention.",
    20: "A de la difficulté à s’organiser.",
    21: "Oublie des choses.",
    22: "A de la difficulté à rester concentré sur ses devoirs ou tâches.",
    23: "A du mal à rester en place lors des activités calmes (repas, devoirs, etc.).",
    24: "Fait des choses sans réfléchir aux conséquences.",
    25: "Interrompt les autres, a de la difficulté à attendre que ce soit son tour pour parler.",
    26: "Parle trop.",
    27: "Se précipite pour répondre avant la fin des questions.",
    28: "A de la difficulté à jouer tranquillement.",
    29: "Semble “survolté”, “comme monté sur ressorts”.",
    30: "Court ou grimpe partout dans des situations inappropriées.",
    31: "N’aime pas perdre; se fâche quand il/elle perd.",
    32: "Dérange délibérément les autres.",
    33: "A de la difficulté à se contrôler.",
    34: "Fait des choses dangereuses sans se rendre compte du danger.",
    35: "A de la difficulté à respecter les règles.",
    36: "Désobéit.",
    37: "N’aime pas qu’on lui dise quoi faire.",
    38: "Boude, fait la tête.",
    39: "Est rancunier/ère.",
    40: "Semble triste ou déprimé(e).",
    41: "A l’air malheureux(se).",
    42: "Pleure facilement.",
    43: "Se sent sans valeur ou inférieur(e).",
    44: "A des pensées ou propos négatifs sur lui/elle-même.",
    45: "S’inquiète beaucoup.",
    46: "Semble anxieux(se), tendu(e).",
    47: "A peur de choses que d’autres enfants n’ont pas peur.",
    48: "A de la difficulté à se faire des amis.",
    49: "A de la difficulté à s’entendre avec les autres enfants.",
    50: "Est rejeté(e) par les autres enfants.",
    51: "Se dispute avec les autres enfants.",
    52: "Taquine, embête les autres enfants.",
    53: "Ment.",
    54: "Vole.",
    55: "Se bagarre.",
    56: "Détruit des choses.",
    57: "Fait du mal aux animaux.",
    58: "Intimide les autres enfants.",
    59: "Est cruel(le) avec les autres.",
    60: "Fait des choses que les autres considèrent comme “bizarres” ou inhabituelles.",
    61: "Répète les mêmes choses ou les mêmes actions.",
    62: "A des habitudes ou routines dont il/elle ne peut pas se défaire.",
    63: "Réagit fortement à certains sons, lumières, textures ou odeurs.",
    64: "A des intérêts très spécifiques, intensifs.",
    65: "Préfère être seul(e) que de jouer avec les autres enfants.",
    66: "Évite le contact visuel.",
    67: "A de la difficulté à comprendre les émotions des autres.",
    68: "A de la difficulté à comprendre les règles sociales implicites.",
    69: "A du mal à comprendre l’humour, l’ironie, les sous-entendus.",
    70: "A des difficultés de sommeil.",
    71: "Se réveille souvent la nuit.",
    72: "A des cauchemars.",
    73: "A des douleurs physiques fréquentes (maux de tête, maux de ventre) sans cause médicale claire.",
    74: "A des tics (moteurs ou vocaux).",
    75: "A des comportements répétitifs (se balancer, taper, etc.).",
    76: "Semble “dans la lune”, déconnecté(e).",
    77: "A de la difficulté à gérer la frustration.",
    78: "A des difficultés à passer d’une activité à une autre.",
    79: "A des difficultés à s’adapter aux changements.",
    80: "Semble hypersensible, réagit intensément aux émotions.",
}

# Sous-échelles / indices (A..N) -> items inclus
# (mapping identique à la version précédente — ajustable si tu veux coller strictement à ton Excel)
SCALES: Dict[str, Dict[str, Any]] = {
    "A": {"label": "Opposition", "items": [3, 9, 10, 32, 35, 36, 37, 39]},
    "B": {"label": "Problèmes cognitifs / Inattention", "items": [13, 14, 15, 16, 17, 18, 19, 20, 21, 22]},
    "C": {"label": "Hyperactivité", "items": [2, 8, 23, 28, 29, 30]},
    "D": {"label": "Anxiété / Timidité", "items": [45, 46, 47, 48]},
    "E": {"label": "Perfectionnisme", "items": [24, 27, 31, 33]},
    "F": {"label": "Problèmes sociaux", "items": [48, 49, 50, 51, 52]},
    "G": {"label": "Symptômes psychosomatiques", "items": [70, 71, 72, 73]},
    "H": {"label": "Index global", "items": [1, 2, 6, 11, 13, 14, 15, 16, 17, 18]},
    "I": {"label": "DSM-IV: Inattention", "items": [13, 14, 15, 16, 17, 18, 19, 20, 21]},
    "J": {"label": "DSM-IV: Hyperactivité/Impulsivité", "items": [2, 8, 24, 25, 26, 27, 28, 29, 30]},
    "K": {"label": "DSM-IV: Troubles des conduites", "items": [53, 54, 55, 56, 57, 58, 59]},
    "L": {"label": "DSM-IV: Opposition", "items": [3, 9, 10, 35, 36, 37, 39]},
    "M": {"label": "Éléments émotionnels", "items": [40, 41, 42, 43, 44, 45, 46]},
    "N": {"label": "Indice élargi (clinique)", "items": [1, 2, 6, 7, 8, 11, 12, 13, 14, 15]},
}

def compute_scores(responses: Dict[int, int]) -> Dict[str, Any]:
    vals = [responses.get(i, 0) for i in range(1, 81)]
    total = sum(vals)
    mean = total / 80.0

    scale_scores = {}
    for key, meta in SCALES.items():
        items = meta["items"]
        s = sum(responses.get(i, 0) for i in items)
        scale_scores[key] = {
            "label": meta["label"],
            "sum": s,
            "n_items": len(items),
            "mean": (s / len(items)) if items else 0.0,
            "items": items,
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
# TAB 1: PASSATION
# ============================================================
with tabs[0]:
    st.subheader("Informations")
    col1, col2, col3 = st.columns(3)
    with col1:
        respondent_name = st.text_input("Nom du parent / répondant", value="")
    with col2:
        child_name = st.text_input("Prénom de l’enfant", value="")
    with col3:
        child_age = st.text_input("Âge de l’enfant (laisser vide si adulte)", value="")

    respondent_name = normalize_name(respondent_name)
    child_name = normalize_name(child_name)

    st.markdown("### Réponses (0 à 3)")
    st.write("Choisissez la réponse la plus juste pour chaque affirmation.")

    responses: Dict[int, int] = {}

    left, right = st.columns(2)
    for i in range(1, 81):
        target = left if i <= 40 else right
        with target:
            responses[i] = st.radio(
                f"{i}. {ITEMS[i]}",
                options=[0, 1, 2, 3],
                format_func=lambda x: RESP_LABELS[x],
                horizontal=False,
                key=f"q_{i}",
            )

    st.markdown("---")
    if st.button("✅ Valider et générer le code", type="primary"):
        if not respondent_name or not child_name:
            st.error("Merci de renseigner au minimum le nom du répondant et le prénom de l’enfant.")
        else:
            scores = compute_scores(responses)
            payload = {
                "meta": {
                    "respondent_name": respondent_name,
                    "child_name": child_name,
                    "child_age": child_age,
                    "timestamp": datetime.now().isoformat(timespec="seconds"),
                    "questionnaire": APP_TITLE,
                    "version_app": "1.0",
                },
                "responses": responses,
                "scores": scores,
            }

            code = generate_code(payload)
            save_passation(code, payload)

            st.success(f"Passation enregistrée. Code de récupération : **{code}**")
            st.info("Conservez ce code. Il permettra au praticien de récupérer les résultats dans l’espace praticien.")

            ok, msg = send_email_with_code(code, respondent_name, child_name, child_age)
            if ok:
                st.success(msg)
            else:
                st.warning(msg)

            with st.expander("Voir un résumé des scores (pour vérification)", expanded=False):
                st.write(f"Score total: **{scores['total_sum']}** / 240")
                st.write(f"Score moyen: **{scores['total_mean']:.2f}** / 3")
                st.markdown("**Sous-échelles (sommes)**")
                for k in sorted(scores["scales"].keys()):
                    sc = scores["scales"][k]
                    st.write(f"- {k} — {sc['label']}: **{sc['sum']}** (n={sc['n_items']})")

# ============================================================
# TAB 2: PRATICIEN
# ============================================================
with tabs[1]:
    st.subheader("Espace praticien")
    if not practitioner_gate_ok():
        st.error("Code praticien incorrect.")
    else:
        code = st.text_input("Entrer le code de récupération", value="").strip().upper()
        if st.button("🔎 Charger la passation"):
            try:
                data = load_passation(code)
                meta = data.get("meta", {})
                scores = data.get("scores", {})
                resp = data.get("responses", {})

                st.success("Passation chargée.")

                st.markdown("### Informations")
                c1, c2, c3 = st.columns(3)
                c1.metric("Répondant", meta.get("respondent_name", ""))
                c2.metric("Enfant", meta.get("child_name", ""))
                c3.metric("Âge", meta.get("child_age", ""))

                st.markdown("### Scores")
                st.write(f"Score total: **{scores.get('total_sum', 0)}** / 240")
                st.write(f"Score moyen: **{scores.get('total_mean', 0.0):.2f}** / 3")

                st.markdown("#### Sous-échelles / Indices")
                scales = scores.get("scales", {})
                for k in sorted(scales.keys()):
                    sc = scales[k]
                    st.write(
                        f"**{k} — {sc.get('label','')}** : "
                        f"{sc.get('sum',0)} (n={sc.get('n_items',0)}, moyenne={sc.get('mean',0.0):.2f})"
                    )

                st.markdown("### Réponses (tableau)")
                rows = []
                for i in range(1, 81):
                    # JSON peut contenir les clés en str selon sérialisation
                    v = resp.get(str(i), resp.get(i, 0))
                    rows.append({"Item": i, "Texte": ITEMS[i], "Réponse": int(v)})
                st.dataframe(rows, use_container_width=True, hide_index=True)

                st.markdown("### Export JSON")
                json_str = json.dumps(data, ensure_ascii=False, indent=2)
                st.download_button(
                    label="⬇️ Télécharger le JSON",
                    data=json_str.encode("utf-8"),
                    file_name=f"tdah_parents_{code}.json",
                    mime="application/json",
                )

            except Exception as e:
                st.error(f"Impossible de charger la passation : {e}")

st.markdown("---")
st.caption("© Outil de passation – usage professionnel. Les scores calculés suivent le mapping configuré dans l’application.")
