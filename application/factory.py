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

def create_app():
    project_root = Path(__file__).resolve().parent.parent
    load_dotenv(project_root / '.env')

    app = Flask(__name__, template_folder='html')
    app.config['MAX_CONTENT_LENGTH'] = 12 * 1024 * 1024
    app.config['UPLOAD_ROOT'] = os.getenv('UPLOAD_ROOT')
    app.config['NETWORK_USERNAME'] = os.getenv('NETWORK_USERNAME')
    app.config['NETWORK_PASSWORD'] = os.getenv('NETWORK_PASSWORD')
    # app.register_blueprint(connection)
    # app.register_blueprint(print_pb, url_prefix=print_pb.url_prefix)
    # app.register_blueprint(swagger_bp)

    @app.get('/')
    def landing_page():
        return render_template('input.html')

    @app.post('/upload')
    def upload_picture():
        picture = request.files.get('picture')
        folder_name = request.form.get('folder_name', '')

        if picture is None or not picture.filename:
            return jsonify(error='Bitte zuerst ein Bild aufnehmen.'), 400
        if not folder_name.strip():
            return jsonify(error='Bitte einen Ordnernamen eingeben.'), 400
        if not app.config['UPLOAD_ROOT']:
            return jsonify(error='Der Speicherpfad ist nicht konfiguriert.'), 500

        try:
            filename = create_picture_filename(picture.filename)
            saved_path = save_picture(
                picture,
                folder_name,
                filename,
                app.config['UPLOAD_ROOT'],
                app.config['NETWORK_USERNAME'],
                app.config['NETWORK_PASSWORD'],
            )
        except ValueError as error:
            return jsonify(error=str(error)), 400
        except OSError:
            app.logger.exception('Could not save uploaded picture')
            return jsonify(error='Das Bild konnte nicht gespeichert werden.'), 500

        relative_path = f'{saved_path.parent.name}/{saved_path.name}'
        return jsonify(message=f'Bild gespeichert: {relative_path}', filename=saved_path.name), 201

    @app.errorhandler(RequestEntityTooLarge)
    def handle_large_upload(_error):
        return jsonify(error='Das Bild ist zu gross (maximal 12 MB).'), 413

    return app