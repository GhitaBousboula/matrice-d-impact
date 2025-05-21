import streamlit as st
import pandas as pd

st.set_page_config(page_title="Matrice de Leopold", layout="wide")

st.title("📊 Matrice de Leopold avec intensité, étendue, durée et nature")
st.write("Sélectionnez les paramètres pour chaque action et composante, et obtenez une matrice textuelle colorée basée sur l'importance et la nature de l'impact.")

# Actions du projet (colonnes)
actions = st.multiselect(
    "Actions du projet", 
    ["Installation de chantier", "Terrassement", "Dépôt de matériaux", "Utilisation de machinerie", "Travaux de construction"],
    default=["Installation de chantier", "Terrassement"]
)

# Composantes environnementales (lignes)
composantes = st.multiselect(
    "Composantes environnementales", 
    ["Sol", "Eau", "Air", "Topographie", "Ressources géologiques", "Bruit", "Faune", "Flore", "Paysage", "Exploitations agricoles", "Sécurité humaine", "Infrastructures existantes", "Déchets", "Eaux usées", "Circulation routière"],
    default=["Sol", "Eau", "Faune"]
)

# Table de correspondance simulée (simplifiée)
def evaluer_importance(intensite, etendue, duree):
    table = {
        ("très forte", "régionale", "long terme"): "Très forte",
        ("très forte", "régionale", "moyen terme"): "Très forte",
        ("très forte", "régionale", "court terme"): "Forte",
        ("très forte", "locale", "long terme"): "Forte",
        ("très forte", "locale", "moyen terme"): "Moyenne",
        ("très forte", "locale", "court terme"): "Moyenne",
        ("très forte", "ponctuelle", "long terme"): "Moyenne",
        ("très forte", "ponctuelle", "moyen terme"): "Faible",
        ("très forte", "ponctuelle", "court terme"): "Faible",
        ("forte", "régionale", "long terme"): "Très forte",
        ("forte", "régionale", "moyen terme"): "Forte",
        ("forte", "régionale", "court terme"): "Moyenne",
        ("forte", "locale", "long terme"): "Forte",
        ("forte", "locale", "moyen terme"): "Moyenne",
        ("forte", "locale", "court terme"): "Faible",
        ("forte", "ponctuelle", "long terme"): "Moyenne",
        ("forte", "ponctuelle", "moyen terme"): "Faible",
        ("forte", "ponctuelle", "court terme"): "Très faible",
        ("moyenne", "régionale", "long terme"): "Forte",
        ("moyenne", "régionale", "moyen terme"): "Moyenne",
        ("moyenne", "régionale", "court terme"): "Faible",
        ("moyenne", "locale", "long terme"): "Moyenne",
        ("moyenne", "locale", "moyen terme"): "Faible",
        ("moyenne", "locale", "court terme"): "Très faible",
        ("moyenne", "ponctuelle", "long terme"): "Faible",
        ("moyenne", "ponctuelle", "moyen terme"): "Faible",
        ("moyenne", "ponctuelle", "court terme"): "Faibe",
        ("faible", "régionale", "long terme"): "Moyenne",
        ("faible", "régionale", "moyen terme"): "Moyenne",
        ("faible", "régionale", "court terme"): "Faible",
        ("faible", "locale", "long terme"): "Moyenne",
        ("faible", "locale", "moyen terme"): "Faible",
        ("faible", "locale", "court terme"): "Faible",
        ("faible", "ponctuelle", "long terme"): "Faible",
        ("faible", "ponctuelle", "moyen terme"): "Très faible",
        ("faible", "ponctuelle", "court terme"): "Très faible",
    }
    cle = (intensite.lower(), etendue.lower(), duree.lower())
    return table.get(cle, "Faible")

# Couleurs combinées nature + importance
def get_color_class(val, nature):
    if nature == "neutre":
        return 'background-color: white; color: black;'
    if nature == "négatif":
        colors = {
            "Très forte": "#8B0000",  # Rouge foncé
            "Forte": "#FF4500",      # Orange foncé
            "Moyenne": "#FFA500",    # Orange
            "Faible": "#FFFF66",     # Jaune clair
            "Très faible": "#F0E68C"   # Jaune pâle
        }
    else:
        colors = {
            "Très forte": "#006400",   # Vert foncé
            "Forte": "#228B22",       # Vert moyen
            "Moyenne": "#7CFC00",     # Vert vif
            "Faible": "#ADFF2F",      # Vert clair
            "Très faible": "#E0FFE0"    # Vert très pâle
        }
    color = colors.get(val, "#FFFFFF")
    text_color = "black"
    return f'background-color: {color}; color: {text_color};'

# Collecte des résultats
resultats = []
if actions and composantes:
    for composante in composantes:
        st.subheader(f"⚙️ {composante}")
        for action in actions:
            with st.expander(f"Action : {action}"):
                nature = st.selectbox("Nature de l’impact", ["négatif", "positif", "neutre"], key=f"nature-{action}-{composante}")

                if nature != "neutre":
                    intensite = st.selectbox("Intensité", ["très forte", "forte", "moyenne", "faible"], key=f"intensite-{action}-{composante}")
                    etendue = st.selectbox("Étendue", ["régionale", "locale", "ponctuelle"], key=f"etendue-{action}-{composante}")
                    duree = st.selectbox("Durée", ["long terme", "moyen terme", "court terme"], key=f"duree-{action}-{composante}")
                    importance = evaluer_importance(intensite, etendue, duree)
                else:
                    importance = "Neutre"

                resultats.append({"Composante": composante, "Action": action, "Importance": importance, "Nature": nature})

    # Création de la matrice enrichie
    df = pd.DataFrame(resultats)
    pivot = df.pivot(index="Composante", columns="Action", values="Importance").fillna("")
    nature_dict = df.pivot(index="Composante", columns="Action", values="Nature").fillna("")

    html = """
    <style>
    .leopold-table {border-collapse: collapse; width: 100%; margin-bottom: 20px;}
    .leopold-table th, .leopold-table td {border: 1px solid #ddd; padding: 8px; text-align: center;}
    .leopold-table th.vertical {height: 140px; white-space: nowrap; position: relative; padding: 0;}
    .leopold-table th.vertical > div {transform: rotate(-90deg); position: absolute; left: 0; right: 0; bottom: 0; top: 0; margin: auto; height: 20px; width: 100%; transform-origin: center center;}
    </style>
    <table class="leopold-table">
        <thead><tr><th>Composantes</th>
    """
    for col in pivot.columns:
        html += f'<th class="vertical"><div>{col}</div></th>'
    html += "</tr></thead><tbody>"
    for idx in pivot.index:
        html += f'<tr><td><strong>{idx}</strong></td>'
        for col in pivot.columns:
            val = pivot.loc[idx, col]
            nature = nature_dict.loc[idx, col]
            style = get_color_class(val, nature)
            html += f'<td style="{style}">{val}</td>'
        html += '</tr>'
    html += "</tbody></table>"

    st.markdown("### 🖼️ Matrice générée")
    st.markdown(html, unsafe_allow_html=True)
    



