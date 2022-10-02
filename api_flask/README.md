# API Flask  / Projet "Prêt à dépenser"

## Les routes disponibles
Dans ce dossier ce trouve l'API Flask intégrant l'ensemble des routes nécessaires pour le bon fonctionnement de 
l'application.

Les **routes accessibles** via l'API sont les suivantes:

| Méthode | Route                          | Description                                                                                                                                                           |
|---------|--------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| GET     | /customer/<id_>                | Permet de récupérer la liste de tous les clients [id_= -1] ou les données d'un seul client.                                                                           |
| GET     | /predict/<id_>?threshold=0.6   | Permet de prédire le risque sur un client précis avec un seuil de risque.                                                                                             |
| GET     | /interp/<id_>?n_customers=1000 | Permet de de transmettre les données par l'interprétabilité globale [id_= -1] ou locale en donnant l'identifiant d'un client. Un nombre de clients doit être précisé. |

## Précision sur la route concernant l'interprétabilité globale

Actuellement, dans le cadre du projet, lors de l'utilisation de la route **/interp/-1**, il est nécessaire de préciser
 une taille d'échantillon à récupérer pour réaliser l'interprétabilité globale : **?n_customers=1000**. 
 
Ces mêmes données seront utilisées pour comparer le client actuel avec cet échantillon. Cette solution a été mise en 
place afin de **limiter la charge et l'utilisation du serveur** et **accélérer les requêtes** (qui pourraient prendre plusieurs
minutes si on récupérait toutes les données des clients).

## Précision sur les données

Dans le cadre de ce projet et pour le mener à bien facilement, les données seront stockées sur le serveur hébergeant 
l'application et sur github.

En situation réelle dans une phase de mise en production, les données seraient bien entendu **stockées dans 
une base de données ou sous forme de fichier crypté** dans un endroit sécurisé pour être **conforme
à la RGPD** et garantir la **protection** des données des clients.

## Lancement de l'API en local

- Ouvrir un terminal et se placer dans le dossier du projet
- Lancer l'API avec la commande `python run.py`

## Déployer l'API sur Heroku

- Suivre les étapes d'installation de l'application
- Mettre les fichiers de l'application sur votre dépôt git

- Créer un compte sur [Heroku](https://signup.heroku.com/)
- Installer [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli)

- Se connecter à Heroku avec la commande `heroku login`
- Créer une nouvelle application avec la commande `heroku create --buildpack https://github.com/infinitly/heroku-
buildpack-git-lfs.git`

- Depuis votre tableau de bord Heroku, dans la section `Settings -> Config Vars` ajoutez les variables d'environnement 
suivantes :
  - `GIT_LFS_REPOSITORY` : l'url https de votre dépôt git
  - `WEB_CONCURRENCY` : La valeur 1

- Depuis votre tableau de bord Heroku, dans la section `Deploy` connecter votre dépôt git à votre application 
Heroku puis activer le déploiement automatique et appuyer sur `Deploy Branch` pour la première fois.

- Retourner dans votre tableau de bord Heroku, dans la section `Resources` ajouter un nouveau dyno de type `worker` 
et démarrer le dyno.

- Votre application est maintenant déployée sur Heroku, vous pouvez la tester en allant sur l'url de votre application.