# P7 / Implémentez un modèle de scoring

Il s'agit du Projet 7 de la formation Data Scientist de Openclassrooms. - Christophe Barras

## Introduction au projet

Je suis Data Scientist au sein d'une **société financière**, nommée "Prêt à dépenser",  qui propose des **crédits à la consommation** pour des personnes ayant peu ou pas du tout d'historique de prêt.

<img src=https://user.oc-static.com/upload/2019/02/25/15510866018677_logo%20projet%20fintech.png>

## Objectifs / Données / Mission

Les **objectifs** à atteindre dans le cadre de ce projet centré sur le domaine bancaire de la datascience sont nombreux.

1. Mettre en œuvre un outil de **“scoring crédit”** pour calculer la probabilité qu’un client rembourse son crédit, puis classifie la demande en crédit accordé ou refusé. Elle souhaite donc **développer un algorithme de classification** en s’appuyant sur des sources de données variées.
2. Être totalement **transparent** vis-à-vis des décisions d’octroi de crédit en développant notament un **dashboard interactif** pour que les chargés de relation client puissent expliquer leurs décisions.

Voici les [données](https://s3-eu-west-1.amazonaws.com/static.oc-static.com/prod/courses/files/Parcours_data_scientist/Projet+-+Impl%C3%A9menter+un+mod%C3%A8le+de+scoring/Projet+Mise+en+prod+-+home-credit-default-risk.zip) nécessaire pour réaliser le dashboard et pour utiliser les différents éléments de ce repository.

Ma **mission** dans ce cadre bien précis sera de :
* Construire un **modèle de scoring** qui donnera une prédiction sur la **probabilité de faillite d'un client** de façon automatique.
* Construire un **dashboard interactif** à destination des gestionnaires de la relation client permettant d'interpréter les prédictions faites par le modèle, et d’améliorer la connaissance client des chargés de relation client.

## Structure du repository

Ce repository a pour objectif de centraliser les différents rendus attendus dans le cadre du projet. Ainsi, les éléments suivants sont accessibles:

* Un dossier concernant la **Préparation des données** et le travail de **Modélisation** : `cleaning_filtering_modelisation`
    > Il sera nécessaire de créer un dossier `home-credit-default-risk` dans ce dossier dans lequel dézipper le contenu des données récupérées via le lien ci-dessus.
* Un dossier contenant la partie API Flask : `api_flask`
* Un dossier contenant la partie Dashboard : `dashboard_streamlit`
