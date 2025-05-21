import streamlit as st
import pandas as pd

st.set_page_config(page_title="Matrice de Leopold", layout="wide")

st.title("📊 Générateur automatique de Matrice de Leopold")
st.write("Remplis les critères pour chaque action et composante, et génère une matrice colorée des impacts.")

# Actions du projet (colonnes)
actions = st.multiselect("Sélectionner les actions du projet", [
    "Déboisement", "Terrassement", "Dépôt de matériaux", "Utilisation de machinerie", "Extraction d'eau"
], default=["Déboisement", "Terrassement"])

# Composantes du milieu (lignes)
composantes = st.multiselect("Sélectionner les composantes environnementales", [
    "Sol", "Eau", "Air", "Faune", "Flore", "Paysage", "Santé humaine", "Population"
], default=["Sol", "Eau", "Faune"])

st.markdown("---")

# Fonction de score corrigée
def evaluer_impact(frequence, etendue, duree, nature):
    score = 0
    score += {"ponctuelle": 1, "répétée": 2, "continue": 3}[frequence]
    score += {"locale": 1, "régionale": 2, "étendue": 3}[etendue]
    score += {"faible": 0, "moyenne": 1, "forte": 2}[duree]
    return score if nature == "positif" else -score

# Collecter les données
resultats = []
for composante in composantes:
    st.subheader(f"⚙️ Impacts sur : {composante}")
    for action in actions:
        with st.expander(f"Action : {action}"):
            duree = st.selectbox(f"Durée ({action} - {composante})", ["faible", "moyenne", "forte"], key=f"{action}-{composante}-duree")
            frequence = st.selectbox("Fréquence", ["ponctuelle", "répétée", "continue"], key=f"{action}-{composante}-freq")
            etendue = st.selectbox("Étendue", ["locale", "régionale", "étendue"], key=f"{action}-{composante}-etendue")
            nature = st.selectbox("Nature de l’impact", ["négatif", "positif"], key=f"{action}-{composante}-nature")

            score = evaluer_impact(frequence, etendue, duree, nature)
            resultats.append({
                "Composante": composante,
                "Action": action,
                "Score": score
            })

# Créer la matrice
df = pd.DataFrame(resultats)
matrice = df.pivot(index="Composante", columns="Action", values="Score").fillna(0)

# Appliquer des couleurs
def coloriser(val):
    if val > 4:
        return 'background-color: green; color: white'
    elif val > 0:
        return 'background-color: lightgreen'
    elif val < -4:
        return 'background-color: red; color: white'
    elif val < 0:
        return 'background-color: orange'
    else:
        return ''

st.markdown("### 🖼️ Matrice générée")
st.dataframe(matrice.style.applymap(coloriser))





