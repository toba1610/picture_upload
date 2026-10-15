import os
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request
from werkzeug.exceptions import RequestEntityTooLarge

from application.modules.picture import create_picture_filename
from application.modules.storage import save_picture

# from application.api.swagger_ui import swagger_bp
# from application.api.print_api import print_pb
# from application.api.landing import connection
from application.api.upload import upload

def create_app():
    project_root = Path(__file__).resolve().parent.parent
    load_dotenv(project_root / '.env')

    app = Flask(__name__, template_folder='html')
    app.config['MAX_CONTENT_LENGTH'] = 12 * 1024 * 1024
    app.config['UPLOAD_ROOT'] = os.getenv('UPLOAD_ROOT')
    app.config['NETWORK_USERNAME'] = os.getenv('NETWORK_USERNAME')
    app.config['NETWORK_PASSWORD'] = os.getenv('NETWORK_PASSWORD')
    app.register_blueprint(upload, url_prefix=upload.url_prefix)

    @app.errorhandler(RequestEntityTooLarge)
    def handle_large_upload(_error):
        return jsonify(error='Das Bild ist zu gross (maximal 12 MB).'), 413

    return app