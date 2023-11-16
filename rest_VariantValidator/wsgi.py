"""
Gunicorn wsgi gateway file
"""
import os
from rest_VariantValidator.app import application as app
from configparser import ConfigParser
from VariantValidator.settings import CONFIG_DIR

config = ConfigParser()
config.read(CONFIG_DIR)

if config["logging"]["log"] == "True":
    app.debug = True
    app.config['PROPAGATE_EXCEPTIONS'] = True
else:
    app.debug = False
    app.config['PROPAGATE_EXCEPTIONS'] = False

if __name__ == '__main__':
    # Read the port from the environment variable, defaulting to 8000 if not set
    port = int(os.environ.get('PORT', 8000))
    app.run(host="127.0.0.1", port=port)
