import streamlit as st
import plotly.graph_objects as go
import plotly.express as px


# Dictionnaire contenant les choix possibles concernant le seuil de tolérance pour le chargé de relations clients
threshold_choices = {
    'Risque optimal': round(st.secrets["DEF_THRESHOLD"], 2),
    'Risque modéré': round(st.secrets["DEF_THRESHOLD"] + 0.1, 2),
    'Risque élevé': round(st.secrets["DEF_THRESHOLD"] + 0.2, 2),
    '': 0
}


def gauge_plot(probability, threshold):
    """
    Fonction permettant de générer un graphique de type jauge paramétré avec la probabilité d'un client de ne pas
    rembourser un prêt et le seuil de tolérance à considérer
    :param probability: float Probabilité d'un client de ne pas rembourser un prêt
    :param threshold: float Seuil de tolérance
    :return: fig: go.Figure Une figure de type jauge
    """
    value = round(probability, 2) * 100
    percent = 0.2
    # On défini les différents paramètres des sections de la jauge (bornes inf et sup et couleur)
    steps = [([0, max(0, threshold - percent)], (14, 67, 123)),
             ([threshold - percent, max(threshold - percent, threshold)], (71, 149, 196)),
             ([threshold, max(threshold, threshold + percent)], (224, 120, 95)),
             ([threshold + percent, max(threshold + percent, 1)], (135, 10, 36))]

    # On utilise la librairie plotly qui propose des graphiques ultra-paramétrables
    fig = go.Figure(go.Indicator(
        domain={'x': [0, 1], 'y': [0, 1]},
        value=value,
        mode="gauge+number+delta",
        title={'text': f""},
        delta={'reference': threshold * 100,
               'increasing': {'color': "rgb(135, 10, 36)"},
               'decreasing': {'color': "rgb(14, 67, 123)"}},
        gauge={'axis': {'range': [0, 100]},
               'bar': {'color': "forestgreen"},
               'steps': [{'range': [step[0][0] * 100, step[0][1] * 100], 'color': f'rgb{str(step[1])}'}
                         for step in steps if step[0][0] != step[0][1]],
               'threshold': {'line': {'color': "black", 'width': 8}, 'thickness': 0.75, 'value': threshold * 100}}))

    return fig


def feature_boxplot(data, feature, value, customer_id):
    """
    Fonction permettant de générer une figure de type boxplot pour situer le client par un échantillon de l'ensemble des
    clients
    :param data: pd.DataFrame Données de l'échantillon de clients
    :param feature: str Nom de la variable
    :param value: float Valeur de la variable pour le client à situer
    :param customer_id: int/str Identifiant du client à situer
    :return: fig
    """
    fig = px.box(data, x=feature)
    fig.add_vline(x=value,
                  line_color="rgb(135, 10, 36)",
                  line_width=4,
                  annotation_text=f'Client #{customer_id}',
                  annotation_bgcolor="rgb(135, 10, 36)")

    fig.update_layout({
        'plot_bgcolor': 'rgba(0, 0, 0, 0)',
        'paper_bgcolor': 'rgba(0, 0, 0, 0)'
    })
    fig.layout.yaxis.color = 'black'
    fig.layout.xaxis.color = 'black'
    fig.update_xaxes(color='black')
    fig.update_yaxes(color='black')

    return fig


# Les fonctions ci-dessous permettent de convertir le choix du risque (en format texte) en un seuil numérique et
# inversement
def convert_choice_to_threshold(choice):
    
    return threshold_choices[choice]
        

def convert_threshold_to_choice(threshold):
    
    return {v: k for k, v in threshold_choices.items()}[threshold]

