import streamlit as st
from streamlit_shap import st_shap

import pandas as pd
import numpy as np
import time
import shap


from utils import *
from api_functions import *

# Première action à réaliser dans le fichier de l'application Steamlit
st.set_page_config(page_title="Prêt à dépenser !", page_icon="💳", layout="wide")

# Ce placeholder va permettre d'afficher toujours au même endroit les messages renvoyés par l'API
placeholder = st.sidebar.empty()

# Cette instruction va permettre de s'assurer que les graphiques SHAP apparaitront correctement sur le dashboard
shap.initjs()


def create_session_key(k, v):
    """
    Permet d'initialiser une clé dans le session_state avec une valeur
    :param k: str Nom de la clé à initialiser
    :param v: any Valeur de la clé à l'initialaisation
    :return:
    """
    if k not in st.session_state:
        st.session_state[k] = v


def display_message(message, type_, wait=3):
    """
    Permet d'afficher un message provenant d'une réponse de l'API
    Le message sera différent selon le "type_" fourni (success, warning, error...)
    Le paramètre "wait" permet de s'assurer que le message soit visible quelques secondes avant de disparaître.
    :param message: str
    :param type_: str
    :param wait: int (durée en secondes)
    """
    global placeholder
    placeholder.__getattribute__(type_)(message)
    time.sleep(wait)
    placeholder.empty()


def display_customer_selectbox():
    """
    Cette fonction permet d'afficher la boîte de sélection des clients après avoir récupéré la liste de leurs
    identifiants.
    :return:
    """

    st.sidebar.text_input("Saisir l'identifiant d'un client", value=st.session_state['customer_id'],
                          key='customer_id',
                          help="Correspond à l'identifiant <SK_ID_CURR>.")


def display_threshold_slider():
    """
    Cette fonction permet d'afficher le slider de sélection du seuil de tolérance avec les options suivantes :
    ['Risque optimal', 'Risque modéré', 'Risque élevé'].
    :return:
    """
    st.sidebar.select_slider(label='Seuil de tolérance', value='Risque optimal',
                             options=['Risque optimal', 'Risque modéré', 'Risque élevé'],
                             key='threshold',
                             help="ATTENTION: Changer ce paramètre diminuera le bénéfice potentiel.")


def display_feature_selectbox():
    """
    Cette fonction permet d'afficher la boîte de sélection des variables disponibles pour visualiser le positionnement
    du client par rapport à cette variable.
    :return:
    """
    features = pd.DataFrame.from_dict(st.session_state['customer_data']).index.tolist()
    st.sidebar.selectbox("Choisir une variable", features, key='selected_feature',
                         help='Visualiser le positionnement du client par rapport à cette variable.')


def display_customer_data(element):
    """
    Cette fonction va permettre d'afficher les données du client demandé.

    :param element: Un élément Streamlit dans lequel ajouter d'autres éléments.
    :return: boolean Les données ont-elles été correctement récupérées ?
    """

    customer_id = int(st.session_state['customer_id'])

    if 'used_customer_id' not in st.session_state:
        create_session_key('used_customer_id', 0)  # Aucun client n'a été demandé précédement

    used_customer_id = int(st.session_state['used_customer_id'])

    if 'customer_data' in st.session_state and used_customer_id == customer_id:  # Les données d'un client sont déjà
        # stockées et il n'y a pas eu de changement de client
        element.subheader(f"Voici les données et les résultats du client #{customer_id}")
        element.dataframe(pd.DataFrame.from_dict(st.session_state['customer_data']))
        return True
    else:  # un nouveau client a été selectionné
        with st.spinner(f'Récupération des données du client #{customer_id} en cours...'):
            r = get_data_from_customer(int(customer_id))  # on fait appel à l'API
            if r[0]:
                element.subheader(f"Voici les données et les résultats du client #{customer_id}")
                element.dataframe(pd.DataFrame.from_dict(r[0]))  # on affiche les données du client
                st.session_state['customer_data'] = r[0]  # on stocke les données du client
            display_message(message=r[2], type_=r[1])  # on affiche le message de réponse provenant de l'API
        if r[1] == 'error':
            return False
        else:
            return True


def display_customer_predict(element):
    """
    Cette fonction va permettre d'afficher les résultats de la prédiction pour le client demandé.

    :param element: Un élément Streamlit dans lequel ajouter d'autres éléments.
    :returns new_threshold, new_customer_id: Le nouveau seuil et le nouvel identifiant client.
    """
    def add_elements(element_, predict_, probability_, threshold_):
        """
        :param element_: Un élément Streamlit dans lequel ajouter d'autres éléments.
        :param predict_: int 0 ou 1 / Décision de prêt.
        :param probability_: float Probabilité de non-remboursement
        :param threshold_: float Seuil de tolérance
        """
        data = ('refusé', "rgb(135, 10, 36)") if predict_ == 1 else ('accordé', "rgb(14, 67, 123)")
        predict_html = f'<h2>Décision : Le prêt est <span style="color:{data[1]};">{data[0]}</span> !</h2>'
        predict_html += f'<p>La probabilité de non-remboursement du prêt est de {round(probability_ * 100)}%.</p>'
        fig = gauge_plot(probability=probability_, threshold=threshold_)
        element_.markdown(predict_html, unsafe_allow_html=True)
        element_.plotly_chart(figure_or_data=fig, use_container_width=True)

    threshold_value = float(convert_choice_to_threshold(st.session_state['threshold']))

    if 'used_threshold' not in st.session_state:
        create_session_key('used_threshold', '')  # Aucun seuil n'a été demandé précédement

    used_threshold = st.session_state['used_threshold']
    used_customer_id = int(st.session_state['used_customer_id'])

    new_threshold = st.session_state['threshold']
    new_customer_id = int(st.session_state['customer_id'])
    if used_customer_id == new_customer_id and used_threshold == new_threshold:  # On n'a demandé ni un nouveau
        # client ni un nouveau seuil
        add_elements(element, int(st.session_state['predict']), float(st.session_state['probability']), threshold_value)
    else:  # un nouveau client ou un nouveau seuil a été sélectionné
        with st.spinner(f'Prédiction pour le client #{new_customer_id} en cours...'):
            r = predict_customer(new_customer_id, threshold_value)  # on fait appel à l'API
            if r[1] == 'success':
                add_elements(element, int(r[0]['predict']), float(r[0]['probability']), threshold_value)
                new_threshold = convert_threshold_to_choice(round(float(r[0]['threshold']), 2))
                new_customer_id = int(r[0]['id_'])
                st.session_state['predict'] = int(r[0]['predict'])  # on stocke la décision renvoyée par l'API
                st.session_state['probability'] = float(r[0]['probability'])   # on stocke la proba renvoyée par l'API

            display_message(message=r[2], type_=r[1])  # on affiche le message de réponse provenant de l'API
    return new_threshold, new_customer_id


def display_interp_global(element):
    """
    Cette fonction va permettre d'afficher l'interprétabilité globale.

    :param element: Un élément Streamlit dans lequel ajouter d'autres éléments.
    """
    if 'shap_global_values' not in st.session_state:  # On n'a pas encore récupéré les valeurs de Shapely
        with st.spinner('Interprétabilité globale en cours...'):
            r = interp_global()   # on fait appel à l'API
            if r[1] == 'success':
                # on récupère les données et on les stocke
                shap_values = r[0]['shap_values']
                interp_data = r[0]['interp_data']

                st.session_state['shap_global_values'] = shap_values
                st.session_state['interp_data_global'] = interp_data

            display_message(message=r[2], type_=r[1])  # on affiche le message de réponse provenant de l'API

    else:  # On n'a déjà stocké les valeurs de Shapely auparavant
        shap_values = st.session_state['shap_global_values']
        interp_data = st.session_state['interp_data_global']

    with element:
        # Utilisation de la librairie streamlit-shap qui gère très bien l'affichage des graphiques SHAP
        st_shap(shap.summary_plot(np.array(shap_values), pd.DataFrame.from_dict(interp_data)))

    texts_info = [('#FF0051', 'élevée'), ('#008BFB', 'faible')]

    for color, value in texts_info:
        element.write(f'<span style="color:{color};">Cette couleur correspond à une valeur {value} pour la '
                      f'variable.</span>',
                      unsafe_allow_html=True)


def display_interp_local(element):
    """
    Cette fonction va permettre d'afficher l'interprétabilité locale pour un client.

    :param element: Un élément Streamlit dans lequel ajouter d'autres éléments.
    :return new_customer_id: Le nouvel identifiant client.
    """
    used_customer_id = int(st.session_state['used_customer_id'])
    new_customer_id = int(st.session_state['customer_id'])

    if used_customer_id == new_customer_id and 'shap_local_values' in st.session_state:  # Les shap values d'un client
        # sont déjà stockées et il n'y a pas eu de changement de client
        interp_data = st.session_state['interp_data_local']
        shap_values = st.session_state['shap_local_values']
        expected_value = st.session_state['expected_value']

    else:  # un nouveau client a été demandé
        with st.spinner(f'Interprétabilité locale pour le client #{new_customer_id} en cours...'):
            r = interp_local(new_customer_id)   # on fait appel à l'API
            if r[1] == 'success':
                # on récupère les données et on les stocke
                interp_data = r[0]['interp_data']
                shap_values = r[0]['shap_values']
                expected_value = float(r[0]['expected_value'])
                new_customer_id = int(r[0]['id_'])
                st.session_state['shap_local_values'] = shap_values
                st.session_state['interp_data_local'] = interp_data
                st.session_state['expected_value'] = expected_value

            display_message(message=r[2], type_=r[1])  # on affiche le message de réponse provenant de l'API

    df_interp_data = pd.DataFrame.from_dict(interp_data)

    interp = shap.Explanation(np.array(shap_values)[0],
                              base_values=expected_value,
                              feature_names=df_interp_data.columns,
                              data=df_interp_data.values[0])

    with element:
        # Utilisation de la librairie streamlit-shap qui gère très bien l'affichage des graphiques SHAP
        st_shap(shap.plots.waterfall(interp))

    texts_info = [('#FF0051', 'augmente'), ('#008BFB', 'diminue')]

    for color, value in texts_info:
        element.write(f'<span style="color:{color};">Cette couleur correspond à un risque de prêt qui {value}.</span>',
                      unsafe_allow_html=True)

    return new_customer_id


def display_interp_feature(element):
    """
    Cette fonction va permettre d'afficher le positionnement du client par rapport à une variable choisie avec un
    graphique boxplot.

    :param element: Un élément Streamlit dans lequel ajouter d'autres éléments.
    """
    global_data = pd.DataFrame.from_dict(st.session_state['interp_data_global'])
    local_data = pd.DataFrame.from_dict(st.session_state['interp_data_local'])
    selected_feature = st.session_state['selected_feature']

    fig = feature_boxplot(data=global_data,
                          feature=selected_feature,
                          value=local_data[selected_feature].values[0],
                          customer_id=st.session_state['customer_id'])
    element.plotly_chart(figure_or_data=fig, use_container_width=True)


def create_header_section(element):
    """
    Cette fonction va permettre de créer la section Header qui contient le titre du dashboard ainsi qu'une description
    et le logo de la société.

    :param element: Un élément Streamlit dans lequel ajouter d'autres éléments.
    :return:
    """
    element.write("""
            <head>
                <meta charset="utf-8">
                <meta name="author" content="Christophe Barras">
                <meta name="viewport" content="width=device-width, initial-scale=1">
            </head>
    """, unsafe_allow_html=True)

    col1, col2 = element.columns((3, 1))
    col2.image("https://user.oc-static.com/upload/2019/02/25/15510866018677_logo%20projet%20fintech.png", width=200)
    container1 = col1.container()

    container1.title("Tableau de bord / Évaluation client")
    container1.markdown(
        "L'objectif de ce dashboard interactif, à destination des chargés de relation client, est qu'ils "
        "puissent à la fois **expliquer de façon la plus transparente possible** les décisions d’octroi de "
        "crédit, mais également permettre à leurs clients de **disposer de leurs informations "
        "personnelles** et de les explorer facilement.")


def create_predict_section(element):
    """
    Cette fonction va permettre de préparer la section Predict qui contient les données et la prédiction
    du modèle concernant le client demandé.

    :param element: Un élément Streamlit dans lequel ajouter d'autres éléments.
    :return: Les éléments "container" qui vont contenir les données et la prédiction du client
    """

    col1, col2 = element.columns((3, 5))

    container_data = col1.container()
    container_predict = col2.container()

    return container_data, container_predict


def create_interp_section(element):
    """
    Cette fonction va permettre de préparer la section Interprétabilité qui contient le positionnement du client
    par rapport à une variable choisie ainsi que l'interprétabilité globale et locale.

    :param element: Un élément Streamlit dans lequel ajouter d'autres éléments.
    :return: Les éléments "expander" qui vont contenir les parties sur l'interprétabilité.
    """
    main_container = element.container()
    if st.session_state['customer_id'] != "":  # Un client a déjà été demandé
        main_container.subheader(f"Quelles sont les données qui expliquent la décision pour le"
                                 f" client #{int(st.session_state['customer_id'])} ?")
    else:
        main_container.empty()

    expander_local = main_container.expander('Interprétabilité locale', expanded=True)
    expander_global = main_container.expander('Interprétabilité globale', expanded=True)
    expander_feat = main_container.expander(f"Positionnement du client / Feature :"
                                            f"  {st.session_state['selected_feature']}", expanded=True)
    return expander_local, expander_global, expander_feat


def dashboard_layout():
    """
    Cette fonction va permettre de construire le tableau de bord en garantissant que les éléments seront toujours
    ajoutés dans le même ordre au rechargement.

    """
    header_section = st.empty()  # Création d'une section vide pour la partie Header
    predict_section = st.empty()  # Création d'une section vide pour la partie Prediction
    interp_section = st.empty()  # Création d'une section vide pour la partie Intreprétabilité
    st.markdown(
        """<style>
        .streamlit-expanderContent {background:white;}
        </style>""",
        unsafe_allow_html=True,
    )  # Un peu de style CSS pour garantir un fond blanc sur les expander (graphiques SHAP mieux intégrés !)
    create_header_section(header_section)

    if 'customer_id' not in st.session_state:
        create_session_key('customer_id', '')

    try:
        display_customer_selectbox()
        display_threshold_slider()
        container_data, container_predict = create_predict_section(predict_section)

        if st.session_state['customer_id'] != "":
            is_data_ok = display_customer_data(container_data)
            if is_data_ok:
                display_feature_selectbox()
                new_threshold, new_customer_id = display_customer_predict(container_predict)
                expander_local, expander_global, expander_feat = create_interp_section(interp_section)
                new_customer_id = display_interp_local(expander_local)
                display_interp_global(expander_global)
                display_interp_feature(expander_feat)
                st.session_state['used_customer_id'] = new_customer_id  # Mise à jour de l'identifiant du client précédent
                st.session_state['used_threshold'] = new_threshold  # Mise à jour du seuil précédent
        else:
            st.subheader("Commencer en saisissant l'identifiant d'un client !")
    except Exception as e:
        display_message(message=f"Quelque chose s'est mal passé. Un problème a pu survenir avec l'API. Erreur : {e}",
                        type_='error', wait=10)


# Appel de la fonction permettant de générer le tableau de bord !
dashboard_layout()
