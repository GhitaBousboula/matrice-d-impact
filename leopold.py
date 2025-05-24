import streamlit as st
import pandas as pd

st.set_page_config(page_title="Matrice d'Impact Environnemental", layout="wide")
st.title("🌍 Générateur de Matrice d'Impact Environnemental par Phase")

st.markdown("""
Cette application vous permet de :
- Sélectionner les phases du projet (préconstruction, construction, exploitation, démantèlement)
- Définir les activités pour chaque phase
- Définir les composantes et milieux concernés pour chaque activité
- Évaluer les impacts (intensité, étendue, durée, nature)
- Ajouter des mesures d’atténuation pour les impacts négatifs
""")

# --- Table de correspondance simulée pour importance ---
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
        ("moyenne", "ponctuelle", "court terme"): "Très faible",
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
def get_color(val, nature):
    if nature == "neutre":
        return 'background-color: white; color: black;'
    if nature == "négatif":
        colors = {
            "Très forte": "#8B0000",
            "Forte": "#FF4500",
            "Moyenne": "#FFA500",
            "Faible": "#FFFF66",
            "Très faible": "#F0E68C"
        }
    else:
        colors = {
            "Très forte": "#006400",
            "Forte": "#228B22",
            "Moyenne": "#7CFC00",
            "Faible": "#ADFF2F",
            "Très faible": "#E0FFE0"
        }
    return f'background-color: {colors.get(val, "white")}; color: black;'

st.markdown("## 📋 Définir les impacts par phase, activité et milieu")
phases = st.multiselect("Phases du projet", ["Préconstruction", "Construction", "Exploitation/Entretien", "Démantèlement"])

resultats = []
for phase in phases:
    st.subheader(f"Phase : {phase}")
    nb_activites = st.number_input(f"Nombre d'activités pour {phase}", min_value=1, step=1, key=f"actnum-{phase}")
    for i in range(nb_activites):
        activite = st.text_input(f"Activité {i+1} ({phase})", key=f"{phase}-act-{i}")
        composantes = st.multiselect(f"Composantes pour {activite}", ["Physique", "Biologique", "Humain"], key=f"{phase}-comp-{i}")
        for composante in composantes:
            milieux = st.text_area(f"Milieux concernés ({activite} - {composante})", key=f"{phase}-milieu-{i}-{composante}", placeholder="Un par ligne")
            for milieu in [m.strip() for m in milieux.split("\n") if m.strip()]:
                with st.expander(f"Impact : {activite} → {milieu} ({composante})"):
                    nature = st.selectbox("Nature de l’impact", ["négatif", "positif", "neutre"], key=f"{phase}-{activite}-{milieu}-nature")
                    impact_apprehende = st.text_area("Impact appréhendé", key=f"{phase}-{activite}-{milieu}-apprehende")
                    if nature != "neutre":
                        intensite = st.selectbox("Intensité", ["très forte", "forte", "moyenne", "faible"], key=f"{phase}-{activite}-{milieu}-intensite")
                        etendue = st.selectbox("Étendue", ["régionale", "locale", "ponctuelle"], key=f"{phase}-{activite}-{milieu}-etendue")
                        duree = st.selectbox("Durée", ["long terme", "moyen terme", "court terme"], key=f"{phase}-{activite}-{milieu}-duree")
                        importance = evaluer_importance(intensite, etendue, duree)
                        attenuation = ""
                        if nature == "négatif":
                            attenuation = st.text_area("Mesures d’atténuation", key=f"{phase}-{activite}-{milieu}-attenuation")
                    else:
                        importance = "Neutre"
                        attenuation = ""
                    resultats.append({
                        "Phase": phase,
                        "Activité": activite,
                        "Composante": composante,
                        "Milieu": milieu,
                        "Nature d’impact": nature,
                        "Importance": importance,
                        "Impact appréhendé": impact_apprehende,
                        "Mesure d’atténuation": attenuation
                    })

if resultats:
    df = pd.DataFrame(resultats)
    st.markdown("##  Matrice des impacts environnementaux")

    def tableau_html_fusion(df):
        expected_cols = ["Phase", "Activité", "Composante", "Milieu", "Nature d’impact", "Importance", "Impact appréhendé", "Mesure d’atténuation"]
        df = df[expected_cols]
        ordre_phases = ["Préconstruction", "Construction", "Exploitation/Entretien", "Démantèlement"]
        df["Phase"] = pd.Categorical(df["Phase"], categories=ordre_phases, ordered=True)

        df = df.sort_values(by=["Phase", "Activité", "Composante", "Milieu"])


        html = """
        <style>
        table {
            border-collapse: collapse;
            width: 100%;
            margin-top: 20px;
        }
        th, td {
            border: 1px solid #ddd;
            padding: 8px;
            text-align: center;
            vertical-align: middle;
        }
        </style>
        <table>
            <thead>
                <tr>
                    <th>Phase</th>
                    <th>Activité</th>
                    <th>Composante</th>
                    <th>Milieu</th>
                    <th>Nature d’impact</th>
                    <th>Importance</th>
                    <th>Impact appréhendé</th>
                    <th>Mesure d’atténuation</th>
                </tr>
            </thead>
            <tbody>
        """

        last_values = {"Phase": None, "Activité": None, "Composante": None}
        counts = df.groupby(["Phase", "Activité", "Composante"]).size().reset_index(name='count')

        for _, row in df.iterrows():
            html += "<tr>"
            for col in ["Phase", "Activité", "Composante"]:
                if row[col] != last_values[col]:
                    rowspan = counts.query(
                        f"Phase == '{row['Phase']}' and Activité == '{row['Activité']}' and Composante == '{row['Composante']}'"
                    )['count'].values[0] if col == "Composante" else \
                    counts[counts[col] == row[col]]['count'].sum()
                    html += f'<td rowspan="{rowspan}">{row[col]}</td>'
                    last_values[col] = row[col]
                else:
                    pass

            html += f"<td>{row['Milieu']}</td>"
            html += f"<td>{row['Nature d’impact']}</td>"
            style = get_color(row["Importance"], row["Nature d’impact"])
            html += f'<td style="{style}">{row["Importance"]}</td>'
            html += f"<td>{row['Impact appréhendé']}</td>"

            if row["Nature d’impact"] == "négatif":
                html += f"<td>{row['Mesure d’atténuation']}</td>"
            else:
                html += "<td>—</td>"

            html += "</tr>"

        html += "</tbody></table>"
        return html

    st.markdown(tableau_html_fusion(df), unsafe_allow_html=True)

else:
    st.info("Remplissez les champs pour générer la matrice.")
