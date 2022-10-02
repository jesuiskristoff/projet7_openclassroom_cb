import streamlit as st
import requests


# Les fonctions faisant appel à l'API ont été mise dans un fichier séparé pour plus de clarté !

API_BASE_URL = st.secrets['API_BASE_URL']
DEF_N_CUSTOMERS = st.secrets['DEF_N_CUSTOMERS']


@st.cache(show_spinner=False)
def get_customers():
    """
    Fonction utilisant la route /customer/-1 pour récupérer la liste des clients.
    """
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
    """
    Fonction utilisant la route /customer/<id_> pour récupérer les données d'un client.
    """
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
    """
    Fonction utilisant la route /predict/<id_> pour récupérer la prédiction du modèle pour un client.

    :param id_: Identifiant d'un client.
    :param threshold: Seuil de tolérance choisi.
    """
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
    """
    Fonction utilisant la route /interp/-1 pour récupérer les données nécessaires à l'interprétabilité globale.
    """
    try:

        response = requests.get(f"{API_BASE_URL}/interp/-1",
                                params={"n_customers": DEF_N_CUSTOMERS}).json()

        if 'erreur' in response:
            return {}, 'error', f"Erreur: {response['erreur']}"
        else:
            return response['data'], 'success', response['message']

    except Exception as e:
        return {}, 'error', f"Erreur: {e}"


@st.cache(show_spinner=False)
def interp_local(id_):
    """
    Fonction utilisant la route /interp/<id_> pour récupérer les données nécessaires à l'interprétabilité locale.

    :param id_: Identifiant d'un client.
    """
    try:

        response = requests.get(f"{API_BASE_URL}/interp/{id_}").json()

        if 'erreur' in response:
            return {}, 'error', f"Erreur: {response['erreur']}"
        else:
            return response['data'], 'success', response['message']

    except Exception as e:
        return {}, 'error', f"Erreur: {e}"
