from flask import Blueprint, request, current_app, render_template, jsonify
from typing import TYPE_CHECKING, cast

from application.modules.picture import create_picture_filename
from application.modules.storage import save_picture
from application.api.api_response import ApiResponse

upload = Blueprint('picture', __name__)
upload.url_prefix = '/picture'

@upload.route('/', methods=['GET'])
def landing_page():
    return render_template('input.html')

@upload.route('/upload', methods=['POST'])
def upload_picture():
    picture = request.files.get('picture')
    folder_name = request.form.get('folder_name', '')

    if picture is None or not picture.filename:
        return jsonify(error='Bitte zuerst ein Bild aufnehmen.'), 400
    if not folder_name.strip():
        return jsonify(error='Bitte einen Ordnernamen eingeben.'), 400
    if not current_app.config['UPLOAD_ROOT']:
        return jsonify(error='Der Speicherpfad ist nicht konfiguriert.'), 500

    try:
        filename = create_picture_filename(picture.filename)
        saved_path = save_picture(
            picture,
            folder_name,
            filename,
            current_app.config['UPLOAD_ROOT'],
            current_app.config['NETWORK_USERNAME'],
            current_app.config['NETWORK_PASSWORD'],
        )
    except ValueError as error:
        return jsonify(error=str(error)), 400
    except OSError:
        current_app.logger.exception('Could not save uploaded picture')
        return jsonify(error='Das Bild konnte nicht gespeichert werden.'), 500

    relative_path = f'{saved_path.parent.name}/{saved_path.name}'
    return jsonify(message=f'Bild gespeichert: {relative_path}', filename=saved_path.name), 201

