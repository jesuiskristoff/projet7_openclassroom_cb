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

## Précision sur les données

Dans le cadre de ce projet et pour le mener à bien facilement, les données seront stockées sur le serveur hébergeant 
l'application.

En situation réelle dans une phase de mise en production, les données seraient bien entendu **stockées dans 
une base de données ou sous forme de fichier crypté** dans un endroit sécurisé pour être **conforme
à la RGPD** et garantir la **protection** des données des clients.