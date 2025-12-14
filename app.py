import streamlit as st
from datetime import date

# ============================================================
# Conners Parents (L) – App Streamlit
# Items: 80 | Réponses: 0-1-2-3
# Scorings: selon clé fournie (facteurs A-E + forme abrégée 10 items)
# ============================================================

st.set_page_config(
    page_title="Conners Parents – Questionnaire",
    page_icon="🧠",
    layout="wide",
)

st.title("Questionnaire Conners – Parents (version révisée L)")
st.caption("Cotation : 0 (jamais), 1 (légère), 2 (moyenne), 3 (forte).")

with st.expander("Informations (optionnel)", expanded=True):
    col1, col2, col3 = st.columns(3)
    with col1:
        nom_enfant = st.text_input("Nom de l’enfant", value="")
        sexe = st.selectbox("Sexe", ["", "M", "F"])
    with col2:
        date_naissance = st.date_input("Date de naissance", value=None)
        age = st.text_input("Âge", value="")
    with col3:
        degre = st.text_input("Degré académique", value="")
        date_passation = st.date_input("Date de passation", value=date.today())

st.markdown("---")

OPTIONS = {
    0: "0 — Jamais",
    1: "1 — Légère",
    2: "2 — Moyenne",
    3: "3 — Forte",
}

# Items 1..80 (texte issu du fichier fourni)
ITEMS = {
    1:  "Est colérique et rancunier",
    2:  "A des difficultés à faire ou compléter ses devoirs",
    3:  "Bouge tout le temps, comme un appareil motorisé",
    4:  "Est timide, vite effrayé",
    5:  "Se fait très rigide dans ses exigences",
    6:  "N’a pas d’ami(e)s",
    7:  "Souffre de maux d'estomac",
    8:  "Se querelle",
    9:  "Recherche la fuite, hésite, ou n’arrive pas à s’engager dans des tâches demandant un effort mental soutenu",
    10: "A de la difficulté à se concentrer dans ses travaux, ses jeux",
    11: "Argumente avec les adultes",
    12: "Ne réussit pas à terminer ses tâches",
    13: "Devient difficile à contrôler dans les centres d'achat ou les épiceries",
    14: "A peur des gens",
    15: "Ne cesse de vérifier ses affaires",
    16: "Perd rapidement ses camarades",
    17: "Souffre de divers malaises, douleurs",
    18: "Est turbulent ou très actif",
    19: "A de la misère à se concentrer à l'école",
    20: "Ne semble ne pas écouter ce qu'on lui dit",
    21: "Perd le contrôle",
    22: "Doit avoir une surveillance continue pour accomplir ses tâches",
    23: "Se promène à la course ou grimpe partout dans les endroits interdits",
    24: "Craint les nouvelles situations",
    25: "Devient tatillon au niveau propreté",
    26: "Ne sait pas comment se faire des ami(e)s",
    27: "Commence à présenter des malaises, douleurs ou des maux d'estomac avant de partir pour l'école",
    28: "Devient facile à exciter et réagit vite",
    29: "Ne suit pas toutes les consignes et ne réussit pas à terminer ses travaux scolaires/corvées/tâches",
    30: "Organise mal ses travaux et ses activités",
    31: "Est irritable",
    32: "Ne cesse de se tortiller",
    33: "Craint de rester seul",
    34: "Doit faire toujours les choses de la même manière",
    35: "Ne reçoit pas d'invitations d'aller chez les camarades",
    36: "Souffre de maux de tête",
    37: "N’arrive pas à terminer ce qu’il commence",
    38: "Manque de concentration, ou se distrait facilement",
    39: "Parle trop",
    40: "Défie volontiers ou refuse le respect de la consigne de l’adulte",
    41: "Ne se préoccupe pas des détails, ou fait des erreurs d’attention dans ses devoirs/travaux/autres activités",
    42: "Paraît incapable d’attendre en file ou son tour dans les jeux/activités de groupe",
    43: "Présente de nombreuses peurs",
    44: "Se doit d’accomplir certains rituels",
    45: "Se distrait vite, ou ne reste pas longtemps sur une tâche",
    46: "Se plaint de maladies même quand il n'a rien",
    47: "A des explosions de colère",
    48: "Se distrait facilement même quand il reçoit une consigne précise",
    49: "Interrompt ou s’ingère dans les affaires des autres (s’impose dans la conversation ou les jeux)",
    50: "Oublie facilement dans les activités du quotidien",
    51: "Ne peut saisir les mathématiques",
    52: "Se met à courir entre deux bouchées de nourriture",
    53: "A peur de la noirceur, des animaux ou des insectes",
    54: "Se fixe des objectifs très élevés",
    55: "Bouge des mains, des pieds, ou se tortille sur la chaise",
    56: "Ne se concentre pas longtemps",
    57: "Est susceptible ou facilement ennuyé par les autres",
    58: "Néglige son écriture",
    59: "N’arrive pas à poursuivre un jeu agréable ou tranquille",
    60: "Reste lointain, en retrait des autres",
    61: "Blâme les autres, de ses fautes, ou ses comportements inadéquats",
    62: "Ne tient pas en place",
    63: "Est malpropre ou mal organisé à la maison ou l'école",
    64: "S’énerve si les autres le dérangent ses affaires",
    65: "Colle aux parents ou autres adultes",
    66: "Dérange les autres enfants",
    67: "Fait exprès pour ennuyer les gens",
    68: "Exige une réponse immédiate aux demandes, sinon il se frustre",
    69: "Ne porte attention qu’à ce qui l’intéresse",
    70: "Se montre mesquin, rancunier",
    71: "Perd le nécessaire à ses travaux ou activités (devoirs, crayons, livres, outils, jouets)",
    72: "Se sent inférieur aux autres",
    73: "Semble fatigué ou ralenti tout le temps",
    74: "Est faible dans l’épellation des mots",
    75: "Pleure souvent sans raison",
    76: "Quitte son siège en classe, ou ailleurs quand il doit rester assis",
    77: "Change d’humeur de manière subite et radicale",
    78: "Devient facilement exaspéré durant un effort",
    79: "Se distrait facilement par les stimuli externes",
    80: "Répond trop vite, avant même la fin de la question",
}

# Clé de correction (Parents) – image fournie
FACTEURS = {
    "A — Difficultés de comportement": [2, 8, 14, 19, 20, 27, 35, 39],
    "B — Difficultés d’apprentissage": [10, 25, 31, 37],
    "C — Somatisation": [32, 41, 43, 44],
    "D — Impulsivité / hyperactivité": [4, 5, 11, 13],
    "E — Anxiété": [12, 16, 24, 47],
}

# Forme abrégée – 10 énoncés (échelle d’hyperactivité) selon la clé fournie
ABREGE_10 = [4, 7, 11, 13, 14, 25, 31, 33, 37, 38]

# ---- UI réponses ----
st.subheader("Réponses")
st.write("Répondez à chaque item. Vous pouvez revenir modifier vos choix avant le calcul.")

responses = {}

# Deux colonnes pour rendre la saisie plus fluide
left, right = st.columns(2)
items_sorted = sorted(ITEMS.keys())

for idx, item_num in enumerate(items_sorted):
    target_col = left if idx % 2 == 0 else right
    with target_col:
        label = f"{item_num}. {ITEMS[item_num]}"
        val = st.radio(
            label,
            options=list(OPTIONS.keys()),
            format_func=lambda x: OPTIONS[x],
            horizontal=True,
            key=f"q_{item_num}",
        )
        responses[item_num] = int(val)

st.markdown("---")

def sum_items(item_list: list[int]) -> int:
    return sum(responses.get(i, 0) for i in item_list)

def mean_items(item_list: list[int]) -> float:
    if not item_list:
        return 0.0
    return sum_items(item_list) / len(item_list)

# ---- Calcul ----
st.subheader("Résultats")

if st.button("Calculer les scores", type="primary"):
    # Score total 80 items
    total = sum_items(items_sorted)

    # Scores par facteur
    facteur_scores = {k: sum_items(v) for k, v in FACTEURS.items()}

    # Forme abrégée
    abrege_total = sum_items(ABREGE_10)
    abrege_moy = mean_items(ABREGE_10)
    suggestion_hyper = abrege_moy >= 1.5  # règle indiquée dans la clé fournie

    colA, colB = st.columns(2)
    with colA:
        st.metric("Total (80 items)", total)
        st.write("**Facteurs (somme des items)**")
        for k, sc in facteur_scores.items():
            st.write(f"- {k} : **{sc}** (items {FACTEURS[k]})")

    with colB:
        st.write("**Forme abrégée (10 items)**")
        st.write(f"- Items : {ABREGE_10}")
        st.write(f"- Total : **{abrege_total}** (sur 30)")
        st.write(f"- Moyenne : **{abrege_moy:.2f}** (0 à 3)")
        if suggestion_hyper:
            st.warning("Moyenne ≥ 1,5 : suggère des indices d’hyperactivité (selon la clé fournie).")
        else:
            st.info("Moyenne < 1,5 : ne suggère pas d’indices d’hyperactivité selon ce seuil.")

    st.markdown("---")
    st.caption(
        "Note : ce questionnaire est un outil d’évaluation. L’interprétation clinique doit tenir compte du contexte, "
        "des autres sources (entretiens, observation, école), et des objectifs de l’évaluation."
    )
