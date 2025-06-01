# utils.py 

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

def get_color(val, nature):
    if nature == "risque impact":
        colors = {
            # très fortee , we choose dark orange for very high risk
            # risque impact doivent etre violets
            "Très forte": "#8A2BE2",
            "Forte": "#9370DB",
            "Moyenne": "#BA55D3",
            "Faible": "#DDA0DD",
            "Très faible": "#E6E6FA"
        }
           
    if nature == "négatif":
        colors = {
            "Très forte": "#8B0000",
            "Forte": "#FF4500",
            "Moyenne": "#FFA500",
            "Faible": "#FFFF66",
            "Très faible": "#F0E68C"
        }
    if nature == "positif":
        colors = {
            "Très forte": "#006400",
            "Forte": "#228B22",
            "Moyenne": "#7CFC00",
            "Faible": "#ADFF2F",
            "Très faible": "#E0FFE0"
        }
    return f'background-color: {colors.get(val, "white")}; color: black;'

def toggle_icon(is_open: bool) -> str:
    """Retourne ▶️ si fermé, ▼ si ouvert."""
    return "▼" if is_open else "▶️"