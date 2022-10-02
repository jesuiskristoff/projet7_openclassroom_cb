import streamlit as st
from streamlit_shap import st_shap
import requests
import pandas as pd
import numpy as np
import time
import shap

from config import *
from utils import gauge_plot, feature_boxplot, convert_choice_to_threshold, convert_threshold_to_choice, threshold_choices

st.set_page_config(page_title="Prêt à dépenser !", page_icon="💳", layout="wide")


placeholder = st.sidebar.empty()
shap.initjs()


def create_session_key(k, v):
    if k not in st.session_state:
        st.session_state[k] = v


def display_message(message, type_, wait=3):
    global placeholder
    placeholder.__getattribute__(type_)(message)
    time.sleep(wait)
    placeholder.empty()


def display_customer_selectbox():

    if 'customers' not in st.session_state:
        with st.spinner('Récupération de la liste des clients en cours...'):
            r = get_customers()
            if r[0]:
                create_session_key('customer_id', r[0][0])
            st.sidebar.selectbox("Choisir un client", r[0],
                                 key='customer_id',
                                 help='SK_ID_CURR')
            display_message(message=r[2], type_=r[1])
            create_session_key('customers', r[0])

    else:
        st.sidebar.selectbox("Choisir un client",
                             st.session_state['customers'],
                             key='customer_id',
                             help="Correspond à l'identifiant <SK_ID_CURR>.")


def display_threshold_slider():

    st.sidebar.select_slider(label='Seuil de tolérance', value='Risque optimal',
                             options=['Risque optimal', 'Risque modéré', 'Risque élevé'],
                             key='threshold',
                             help="ATTENTION: Changer ce paramètre diminuera le bénéfice potentiel.")


def display_feature_selectbox():

    features = pd.DataFrame.from_dict(st.session_state['customer_data']).index.tolist()
    st.sidebar.selectbox("Choisir une variable", features, key='selected_feature',
                         help='Visualiser le positionnement du client par rapport à cette variable.')


@st.cache(show_spinner=False)
def get_customers():
    try:
        response = requests.get(f"{API_BASE_URL}/customer/-1").json()

        if 'erreur' in response:
            return [], 'error', f"Erreur: {response['erreur']}"
        else:
            return response['data'], 'success', response['message']

    except Exception as e:
        return [], 'error', f"Erreur: {e}"


@st.cache(show_spinner=False)
def get_data_from_customer(id_):
    try:
        response = requests.get(f"{API_BASE_URL}/customer/{id_}").json()

        if 'erreur' in response:
            return {}, 'error', f"Erreur: {response['erreur']}"
        else:
            return response['data'], 'success', response['message']

    except Exception as e:
        return {}, 'error', f"Erreur: {e}"


@st.cache(show_spinner=False)
def predict_customer(id_, threshold):
    try:

        response = requests.get(f"{API_BASE_URL}/predict/{id_}", params={"threshold": threshold}).json()

        if 'erreur' in response:
            return {}, 'error', f"Erreur: {response['erreur']}"
        else:
            return response['data'], 'success', response['message']

    except Exception as e:
        return {}, 'error', f"Erreur: {e}"


@st.cache(show_spinner=False)
def interp_global():
    try:

        response = requests.get(f"{API_BASE_URL}/interp/-1", params={"n_customers": DEF_N_CUSTOMERS}).json()

        if 'erreur' in response:
            return {}, 'error', f"Erreur: {response['erreur']}"
        else:
            return response['data'], 'success', response['message']

    except Exception as e:
        return {}, 'error', f"Erreur: {e}"


@st.cache(show_spinner=False)
def interp_local(id_):
    try:

        response = requests.get(f"{API_BASE_URL}/interp/{id_}").json()

        if 'erreur' in response:
            return {}, 'error', f"Erreur: {response['erreur']}"
        else:
            return response['data'], 'success', response['message']

    except Exception as e:
        return {}, 'error', f"Erreur: {e}"


def display_customer_data(element):

    customer_id = int(st.session_state['customer_id'])

    if 'used_customer_id' not in st.session_state:
        create_session_key('used_customer_id', 0)

    used_customer_id = int(st.session_state['used_customer_id'])

    if 'customer_data' in st.session_state and used_customer_id == customer_id:
        element.dataframe(pd.DataFrame.from_dict(st.session_state['customer_data']))
    else:
        with st.spinner(f'Récupération des données du client #{customer_id} en cours...'):
            r = get_data_from_customer(int(customer_id))
            element.dataframe(pd.DataFrame.from_dict(r[0]))
            st.session_state['customer_data'] = r[0]
            display_message(message=r[2], type_=r[1])


def display_customer_predict(element):

    def add_elements(element_, predict_, probability_, threshold_):
        predict_data = ('refusé', "rgb(135, 10, 36)") if predict_ == 1 else ('accordé', "rgb(14, 67, 123)")
        predict_html = f'<h2>Résultat : Le prêt est <span style="color:{predict_data[1]};">{predict_data[0]}</span> !</h2>'
        predict_html += f'<p>La probabilité de non-remboursement du prêt est de {round(probability_ * 100)}%.</p>'
        fig = gauge_plot(probability=probability_, threshold=threshold_)
        element_.markdown(predict_html, unsafe_allow_html=True)
        element_.plotly_chart(figure_or_data=fig, use_container_width=True)

    threshold_value = float(convert_choice_to_threshold(st.session_state['threshold']))

    if 'used_threshold' not in st.session_state:
        create_session_key('used_threshold', '')
    
    used_threshold = st.session_state['used_threshold']
    used_customer_id = int(st.session_state['used_customer_id'])

    new_threshold = st.session_state['threshold']
    new_customer_id = int(st.session_state['customer_id'])
    if used_customer_id == new_customer_id and used_threshold == new_threshold:
        add_elements(element, int(st.session_state['predict']), float(st.session_state['probability']), threshold_value)
    else:
        with st.spinner(f'Prédiction pour le client #{new_customer_id} en cours...'):
            r = predict_customer(new_customer_id, threshold_value)
            if r[1] == 'success':
                add_elements(element, int(r[0]['predict']), float(r[0]['probability']), threshold_value)
                new_threshold = convert_threshold_to_choice(round(float(r[0]['threshold']),2))
                new_customer_id = int(r[0]['id_'])
                st.session_state['predict'] = int(r[0]['predict'])
                st.session_state['probability'] = float(r[0]['probability'])

            display_message(message=r[2], type_=r[1])
    return new_threshold, new_customer_id


def display_interp_global(element):
    if 'shap_global_values' not in st.session_state:
        with st.spinner('Interprétabilité globale en cours...'):
            r = interp_global()
            if r[1] == 'success':
                shap_values = r[0]['shap_values']
                interp_data = r[0]['interp_data']

                st.session_state['shap_global_values'] = shap_values
                st.session_state['interp_data_global'] = interp_data

            display_message(message=r[2], type_=r[1])

    else:
        shap_values = st.session_state['shap_global_values']
        interp_data = st.session_state['interp_data_global']

    with element:
        st_shap(shap.summary_plot(np.array(shap_values), pd.DataFrame.from_dict(interp_data)))

    texts_info = [('#FF0051', 'élevée'), ('#008BFB', 'faible')]

    for color, value in texts_info:
        element.write(f'<span style="color:{color};">Cette couleur correspond à une valeur {value}.</span>',
                      unsafe_allow_html=True)


def display_interp_local(element):

    used_customer_id = int(st.session_state['used_customer_id'])
    new_customer_id = int(st.session_state['customer_id'])

    if used_customer_id == new_customer_id and 'shap_local_values' in st.session_state:
        interp_data = st.session_state['interp_data_local']
        shap_values = st.session_state['shap_local_values']
        expected_value = st.session_state['expected_value']

    else:
        with st.spinner(f'Interprétabilité locale pour le client #{new_customer_id} en cours...'):
            r = interp_local(new_customer_id)
            if r[1] == 'success':
                interp_data = r[0]['interp_data']
                shap_values = r[0]['shap_values']
                expected_value = float(r[0]['expected_value'])
                new_customer_id = int(r[0]['id_'])
                st.session_state['shap_local_values'] = shap_values
                st.session_state['interp_data_local'] = interp_data
                st.session_state['expected_value'] = expected_value

            display_message(message=r[2], type_=r[1])

    df_interp_data = pd.DataFrame.from_dict(interp_data)

    interp = shap.Explanation(np.array(shap_values)[0],
                              base_values=expected_value,
                              feature_names=df_interp_data.columns,
                              data=df_interp_data.values[0])

    with element:
        st_shap(shap.plots.waterfall(interp))

    texts_info = [('#FF0051', 'augmente'), ('#008BFB', 'diminue')]

    for color, value in texts_info:
        element.write(f'<span style="color:{color};">Cette couleur correspond à un risque de prêt qui {value}.</span>',
                      unsafe_allow_html=True)

    return new_customer_id


def display_interp_feature(element):

    global_data = pd.DataFrame.from_dict(st.session_state['interp_data_global'])
    local_data = pd.DataFrame.from_dict(st.session_state['interp_data_local'])
    selected_feature = st.session_state['selected_feature']

    fig = feature_boxplot(data=global_data,
                          feature=selected_feature,
                          value=local_data[selected_feature].values[0],
                          customer_id=st.session_state['customer_id'])
    element.plotly_chart(figure_or_data=fig, use_container_width=True)


def create_header_section(element):
    element.write("""
            <head>
                <meta charset="utf-8">
                <meta name="author" content="Christophe Barras">
                <meta name="viewport" content="width=device-width, initial-scale=1">
            </head>
    """, unsafe_allow_html=True)

    col1, col2 = element.columns((3, 1))

    col2.image("./assets/logo.png", width=200)
    container1 = col1.container()

    container1.title("Tableau de bord / Évaluation client")
    container1.markdown(
        "L'objectif de ce dashboard interactif, à destination des chargés de relation client, est qu'ils "
        "puissent à la fois **expliquer de façon la plus transparente possible** les décisions d’octroi de "
        "crédit, mais également permettre à leurs clients de **disposer de leurs informations "
        "personnelles** et de les explorer facilement.")


def create_predict_section(element):

    main_container = element.container()
    if "customer_id" in st.session_state:
        main_container.subheader(f"Voici les données et les résultats du client #{int(st.session_state['customer_id'])}")
    else:
        main_container.subheader(f"Voici les données et les résultats du client demandé.")

    col1, col2 = main_container.columns((3, 5))

    container_data = col1.container()
    container_predict = col2.container()

    return container_data, container_predict


def create_interp_section(element):

    main_container = element.container()
    if "customer_id" in st.session_state:
        main_container.subheader(f"Quelles sont les données influentes globalement et pour le"
                                 f" client #{int(st.session_state['customer_id'])} ?")
    else:
        main_container.empty()

    expander_local = main_container.expander('Interprétabilité locale', expanded=True)
    expander_global = main_container.expander('Interprétabilité globale', expanded=True)
    expander_feat = main_container.expander(f"Positionnement du client / Feature :"
                                            f"  {st.session_state['selected_feature']}", expanded=True)
    return expander_local, expander_global, expander_feat


def dashboard_layout():
    
    header_section = st.empty()
    predict_section = st.empty()
    interp_section = st.empty()
    st.markdown(
        """<style>
        .streamlit-expanderContent {background:white;}
        </style>""",
        unsafe_allow_html=True,
    )
    create_header_section(header_section)
    container_data, container_predict = create_predict_section(predict_section)
    display_customer_selectbox()
    display_threshold_slider()
    display_customer_data(container_data)
    display_feature_selectbox()
    new_threshold, new_customer_id = display_customer_predict(container_predict)
    expander_local, expander_global, expander_feat = create_interp_section(interp_section)
    new_customer_id = display_interp_local(expander_local)
    display_interp_global(expander_global)
    display_interp_feature(expander_feat)
    st.session_state['used_customer_id'] = new_customer_id
    st.session_state['used_threshold'] = new_threshold


dashboard_layout()
