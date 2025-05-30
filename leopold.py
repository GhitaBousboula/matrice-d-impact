import streamlit as st
import pandas as pd
from utils import evaluer_importance, get_color
import html

# Polyfill for Streamlit’s rerun (newer vs older versions)
try:
    _rerun = st.experimental_rerun
except AttributeError:
    from streamlit.runtime.scriptrunner import RerunException
    def _rerun():
        raise RerunException("Rerun requested")

class Impact:
    def __init__(self, composante, milieu, nature, impact_apprehende, intensite=None, etendue=None, duree=None, attenuation=None):
        self.composante = composante
        self.milieu = milieu
        self.nature = nature
        self.impact_apprehende = impact_apprehende
        self.intensite = intensite
        self.etendue = etendue
        self.duree = duree
        self.attenuation = attenuation
        self.importance = self.calculate_importance()

    def calculate_importance(self):
        if self.nature == 'neutre':
            return 'Neutre'
        return evaluer_importance(self.intensite or '', self.etendue or '', self.duree or '')

class Activity:
    def __init__(self, name):
        self.name = name
        self.impacts = []

class Phase:
    def __init__(self, name):
        self.name = name
        self.activities = []

class Project:
    def __init__(self):
        self.phases = []

    def add_phase(self, phase_name):
        if phase_name not in [phase.name for phase in self.phases]:
            self.phases.append(Phase(phase_name))

    def get_phase(self, phase_name):
        for phase in self.phases:
            if phase.name == phase_name:
                return phase
        return None

    def to_dataframe(self):
        data = []
        for phase in self.phases:
            for activity in phase.activities:
                for impact in activity.impacts:
                    data.append({
                        "Phase": phase.name,
                        "Activité": activity.name,
                        "Composante": impact.composante,
                        "Milieu": impact.milieu,
                        "Nature impact": impact.nature,
                        "Importance": impact.importance,
                        "Impact appréhendé": impact.impact_apprehende,
                        "Mesure atténuation": impact.attenuation if impact.nature == 'négatif' else ''
                    })
        return pd.DataFrame(data)


def tableau_html_fusion(df):
    df = df[[
        "Phase", "Activité", "Composante", "Milieu",
        "Nature impact", "Importance", "Impact appréhendé", "Mesure atténuation"
    ]]
    ordre_phases = ["Préconstruction", "Construction", "Exploitation/Entretien", "Démantèlement"]
    df["Phase"] = pd.Categorical(df["Phase"], categories=ordre_phases, ordered=True)
    df = df.sort_values(by=["Phase", "Activité", "Composante", "Milieu"]).reset_index(drop=True)

    # Calcul des rowspans
    rowspan_data = {}
    hierarchy_cols = ["Phase", "Activité", "Composante"]
    for col in hierarchy_cols:
        rowspan_data[col] = {}
        current_group = None
        count = 0
        start_idx = 0
        for i in range(len(df)):
            group_cols = hierarchy_cols[:hierarchy_cols.index(col) + 1]
            group_id = tuple(df.loc[i, group_cols].values)
            if group_id != current_group:
                if current_group is not None:
                    rowspan_data[col][start_idx] = count
                current_group = group_id
                count = 1
                start_idx = i
            else:
                count += 1
        rowspan_data[col][start_idx] = count

    # Génération du tableau HTML
    html_table = """
    <style>
      table { border-collapse: collapse; width: 100%; margin-top: 20px; font-family: Arial, sans-serif; }
      th, td { border: 1px solid #ddd; padding: 10px; text-align: left; vertical-align: top; }
      th { background-color: #f2f2f2; font-weight: bold; }
      .hier-number { font-weight: bold; margin-right: 5px; }
    </style>
    <table>
      <thead>
        <tr>
          <th>Phase</th><th>Activité</th><th>Composante</th><th>Milieu</th>
          <th>Nature impact</th><th>Importance</th><th>Impact appréhendé</th><th>Mesure atténuation</th>
        </tr>
      </thead>
      <tbody>
    """

    # Numérotation hiérarchique
    current_numbers = {col: 0 for col in hierarchy_cols}
    last_values = {col: None for col in hierarchy_cols}

    for i, row in df.iterrows():
        for col in hierarchy_cols:
            if row[col] != last_values[col]:
                current_numbers[col] += 1
                for sub_col in hierarchy_cols[hierarchy_cols.index(col)+1:]:
                    current_numbers[sub_col] = 0
                last_values[col] = row[col]

        html_table += "<tr>"
        for col in hierarchy_cols:
            if i in rowspan_data[col]:
                span = rowspan_data[col][i]
                prefix = ".".join(str(current_numbers[c]) for c in hierarchy_cols[:hierarchy_cols.index(col)+1]) + "."
                text = html.escape(str(row[col]))
                html_table += f'<td rowspan="{span}"><span class="hier-number">{prefix}</span>{text}</td>'

        # Cellules avec préservation des retours à la ligne via <br>
        milieu = html.escape(str(row['Milieu']))
        nature = html.escape(str(row['Nature impact']))
        importance = html.escape(str(row['Importance']))
        impact_desc = html.escape(str(row['Impact appréhendé'])).replace('\n', '<br/>')
        attenuation = html.escape(str(row['Mesure atténuation'])).replace('\n', '<br/>')

        html_table += f"<td>{milieu}</td>"
        html_table += f"<td>{nature}</td>"
        html_table += f'<td style="{get_color(row["Importance"], row["Nature impact"])}">{importance}</td>'
        html_table += f'<td>{impact_desc}</td>'
        html_table += f'<td>{attenuation}</td>'
        html_table += "</tr>"

    html_table += "</tbody></table>"
    return html_table


def main():
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

    st.markdown("""
    <style>
    .section { 
        margin-left: 20px; 
        padding: 10px; 
        border-left: 2px solid #ddd;
        margin-bottom: 15px;
    }
    .subsection { 
        margin-left: 40px; 
        padding: 8px;
        border-left: 2px solid #eee;
    }
    .subsubsection { 
        margin-left: 60px; 
        padding: 6px;
    }
    .header { 
        display: flex; 
        align-items: center; 
        cursor: pointer; 
        margin: 5px 0;
    }
    </style>
    """, unsafe_allow_html=True)
    


    if 'project' not in st.session_state:
        st.session_state.project = Project()
        st.session_state.collapsed = {}
        st.session_state.milieu_count = {}
        
    project = st.session_state.project

    # Gestion des phases
    selected_phases = st.multiselect(
        "Phases du projet",
        ["Préconstruction", "Construction", "Exploitation/Entretien", "Démantèlement"],
        default=[p.name for p in project.phases]
    )
    
    # Synchronisation des phases
    current_phases = [p.name for p in project.phases]
    project.phases = [p for p in project.phases if p.name in selected_phases]
    for phase_name in selected_phases:
        if phase_name not in current_phases:
            project.add_phase(phase_name)

    # Affichage hiérarchique
    for phase in project.phases:
        phase_key = f"phase_{phase.name}"
        
        # Header avec flèche interactive
        col1, col2 = st.columns([0.05, 0.95])
        with col1:
            arrow = "▼" if st.session_state.collapsed.get(phase_key, True) else "▶"
            if st.button(arrow, key=f"btn_{phase_key}"):
                st.session_state.collapsed[phase_key] = not st.session_state.collapsed.get(phase_key, True)
        with col2:
            st.subheader(f"Phase: {phase.name}")
        
        if not st.session_state.collapsed.get(phase_key, True):
            continue
            
        with st.container():
            st.markdown('<div class="section">', unsafe_allow_html=True)
            
            # Ajout d'activités
            col1, col2 = st.columns([0.7, 0.3])
            with col1:
                new_activity = st.text_input(
                    "Nom de la nouvelle activité",
                    key=f"new_act_{phase.name}",
                    placeholder="Entrez le nom d'une activité"
                )
            with col2:
                st.write("")
                st.write("")
                if st.button("➕ Ajouter activité", key=f"add_act_{phase.name}"):
                    if new_activity:
                        phase.activities.append(Activity(new_activity))
            
            # Activités existantes
            for activity in phase.activities[:]:
                activity_key = f"activity_{phase.name}_{activity.name}"
                
                # Header d'activité avec flèche et bouton de suppression
                st.markdown('<div class="subsection">', unsafe_allow_html=True)
                col1, col2, col3 = st.columns([0.05, 0.85, 0.1])
                with col1:
                    arrow = "▼" if st.session_state.collapsed.get(activity_key, True) else "▶"
                    if st.button(arrow, key=f"btn_{activity_key}"):
                        st.session_state.collapsed[activity_key] = not st.session_state.collapsed.get(activity_key, True)
                with col2:
                    st.markdown(f"**Activité:** {activity.name}")
                with col3:
                    if st.button("🗑️", key=f"del_act_{activity_key}"):
                        phase.activities.remove(activity)
                        _rerun()
                
                if not st.session_state.collapsed.get(activity_key, True):
                    st.markdown('</div>', unsafe_allow_html=True)
                    continue
                
                with st.container():
                    st.markdown('<div class="subsubsection">', unsafe_allow_html=True)
                    
                    # Composantes environnementales
                    composantes = st.multiselect(
                        "Composantes environnementales concernées",
                        ["Physique", "Biologique", "Humain"],
                        key=f"comp_{phase.name}_{activity.name}",
                        help="Sélectionnez les composantes impactées par cette activité"
                    )
                    
                    for comp in composantes:
                        comp_key = f"comp_{phase.name}_{activity.name}_{comp}"
                        
                        # Header de composante avec flèche
                        col1, col2 = st.columns([0.05, 0.95])
                        with col1:
                            arrow = "▼" if st.session_state.collapsed.get(comp_key, True) else "▶"
                            if st.button(arrow, key=f"btn_{comp_key}"):
                                st.session_state.collapsed[comp_key] = not st.session_state.collapsed.get(comp_key, True)
                        with col2:
                            st.markdown(f"**Composante:** {comp}")
                        
                        if not st.session_state.collapsed.get(comp_key, True):
                            continue
                            
                        with st.container():
                            # Gestion des milieux
                            milieu_count = st.session_state.milieu_count.get(comp_key, 0)
                            
                            # Ajout de milieux
                            if st.button("➕ Ajouter un milieu", key=f"add_mil_{comp_key}"):
                                milieu_count += 1
                                st.session_state.milieu_count[comp_key] = milieu_count
                            
                            # Milieux existants
                            for i in range(1, milieu_count + 1):
                                milieu_key = f"{comp_key}_milieu_{i}"
                                
                                # Suppression de milieu
                                col1, col2 = st.columns([0.9, 0.1])
                                with col1:
                                    # milieu_name = st.text_input(
                                    #     f"Milieu {i}",
                                    #     key=f"name_{milieu_key}",
                                    #     placeholder="Nom du milieu (ex: Eau, Air, Sol...)"
                                    # )

                                    # strip() removes any accidental spaces before/after the name
                                    raw_milieu = st.text_input(
                                        f"Milieu {i}",
                                        key=f"name_{milieu_key}",
                                        placeholder="Nom du milieu (ex: Eau, Air, Sol...)"
                                    )
                                    milieu_name = raw_milieu.strip()

                                with col2:
                                    st.write("")
                                    st.write("")
                                    if st.button("🗑️", key=f"del_{milieu_key}"):
                                        # Supprimer l'impact correspondant
                                        activity.impacts = [imp for imp in activity.impacts 
                                                          if not (imp.composante == comp and imp.milieu == milieu_name)]
                                        _rerun()
                                
                                if not milieu_name:
                                    continue
                                
                                # Paramètres d'impact
                                nature = st.selectbox(
                                    "Nature de l'impact",
                                    ["négatif", "positif", "neutre"],
                                    index=0,
                                    key=f"nat_{milieu_key}"
                                )
                                
                                # Vérifier s'il existe déjà un impact pour ce milieu
                                existing_impact = next(
                                    (imp for imp in activity.impacts 
                                     if imp.composante == comp and imp.milieu == milieu_name), 
                                    None
                                )
                                
                                # Description de l'impact
                                impact_apprehende = st.text_area(
                                    "Description de l'impact",
                                    value=existing_impact.impact_apprehende  if existing_impact else "",
                                    key=f"desc_{milieu_key}",
                                    height=100
                                )
                                
                                # Paramètres supplémentaires pour impacts non neutres
                                intensite = etendue = duree = attenuation = None
                                if nature != 'neutre':
                                    cols = st.columns(3)
                                    with cols[0]:
                                        intensite = st.selectbox(
                                            "Intensité",
                                            ["très forte", "forte", "moyenne", "faible"],
                                            index=0,
                                            key=f"int_{milieu_key}"
                                        )
                                    with cols[1]:
                                        etendue = st.selectbox(
                                            "Étendue",
                                            ["régionale", "locale", "ponctuelle"],
                                            index=1,
                                            key=f"et_{milieu_key}"
                                        )
                                    with cols[2]:
                                        duree = st.selectbox(
                                            "Durée",
                                            ["long terme", "moyen terme", "court terme"],
                                            index=2,
                                            key=f"dur_{milieu_key}"
                                        )
                                    
                                    if nature == 'négatif':
                                        # attenuation = st.text_area(
                                        #     "Mesures d'atténuation",
                                        #     value=existing_impact.attenuation if existing_impact else "",
                                        #     key=f"att_{milieu_key}",
                                        #     height=100
                                        # )

                                        # use the stable loop index `i` in the key rather than the text itself
                                        attenuation = st.text_area(
                                            "Mesures d'atténuation",
                                            value=existing_impact.attenuation if existing_impact else "",
                                            key=f"att_{phase.name}_{activity.name}_{comp}_{i}",
                                            height=100
                                        )                                        
                                
                                # Créer/mettre à jour l'objet Impact
                                new_impact = Impact(
                                    comp, milieu_name, nature, impact_apprehende,
                                    intensite, etendue, duree, attenuation
                                )
                                
                                # Supprimer l'ancien impact s'il existe
                                if existing_impact:
                                    activity.impacts.remove(existing_impact)
                                
                                # Ajouter le nouvel impact
                                activity.impacts.append(new_impact)
                            
                            st.markdown('</div>', unsafe_allow_html=True)  # Fin subsubsection
                        st.markdown('</div>', unsafe_allow_html=True)  # Fin subsubsection container
                    st.markdown('</div>', unsafe_allow_html=True)  # Fin subsection
                st.markdown('</div>', unsafe_allow_html=True)  # Fin section
            st.markdown('</div>', unsafe_allow_html=True)  # Fin section container

    # Affichage de la matrice finale
    df = project.to_dataframe()
    if not df.empty:
        st.markdown("## 📊 Matrice des impacts environnementaux")
        st.markdown("### Synthèse complète des impacts par phase, activité et composante")
        
        # Export CSV
        csv = df.to_csv(index=False, sep=';').encode('utf-8')
        st.download_button(
            "💾 Exporter en CSV", 
            csv, 
            "matrice_impacts.csv", 
            "text/csv",
            key='download-csv'
        )
        
        # Affichage du tableau
        st.markdown(tableau_html_fusion(df), unsafe_allow_html=True)
    else:
        st.info("ℹ️ Commencez par ajouter des phases, activités et composantes pour générer la matrice.")

if __name__ == "__main__":
    main()