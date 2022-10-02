# Importation de l'application Flask depuis le dossier api_flask

from api_flask.app import app
import os

# Lancement de l'application Flask
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(port=port, debug=False)
