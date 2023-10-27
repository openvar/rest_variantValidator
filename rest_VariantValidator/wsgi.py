"""
Gunicorn wsgi gateway file
"""
from rest_VariantValidator.app import application

if __name__ == '__main__':
    from configparser import ConfigParser
    from VariantValidator.settings import CONFIG_DIR

    config = ConfigParser()
    config.read(CONFIG_DIR)

    if config["logging"]["log"] == "True":
        application.debug = True
        application.config['PROPAGATE_EXCEPTIONS'] = True
    else:
        application.debug = False
        application.config['PROPAGATE_EXCEPTIONS'] = False

    # Define the Gunicorn entry point
    from gunicorn.app.wsgiapp import WSGIApplication


    class GunicornApp(WSGIApplication):
        def init(self, parser, opts, args):
            return {
                'bind': '0.0.0.0:8000',
                'workers': 3,
                'timeout': 600,
                'chdir': './rest_VariantValidator/'
            }


    if __name__ == '__main__':
        options = {
            'bind': '0.0.0.0:8000',
            'workers': 3,
            'timeout': 600,
            'chdir': './rest_VariantValidator/'
        }
        GunicornApp().run()

    application.run(host="127.0.0.1", port=8000)
