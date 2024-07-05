from flask import Flask, render_template, request, send_file, redirect, url_for
import os
from werkzeug.utils import secure_filename
from zipfile import ZipFile
from watermark import add_watermark
import logging

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['PROCESSED_FOLDER'] = 'processed/'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB

# Cria os diretórios de upload e processamento se não existirem
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])
if not os.path.exists(app.config['PROCESSED_FOLDER']):
    os.makedirs(app.config['PROCESSED_FOLDER'])

logging.basicConfig(level=logging.DEBUG)

@app.route('/')
def index():
    """
    Renderiza a página inicial com o formulário de upload.

    Returns:
        render_template: Template HTML renderizado.
    """
    return render_template('index.jinja')


@app.route('/upload', methods=['POST'])
def upload_files():
    """
    Rota para lidar com o upload de arquivos.

    Returns:
        send_file: Arquivo ZIP com as imagens processadas para download.
        redirect: Redireciona de volta para a página de upload em caso de falha.
    """
    if 'logo' not in request.files or 'photos' not in request.files:
        return redirect(request.url)

    logo = request.files['logo']
    photos = request.files.getlist('photos')

    if logo.filename == '' or all(photo.filename == '' for photo in photos):
        return redirect(request.url)

    logo_filename = secure_filename(logo.filename)
    logo_path = os.path.join(app.config['UPLOAD_FOLDER'], logo_filename)
    logo.save(logo_path)
    logging.debug(f'Logo salvo em {logo_path}')

    processed_files = []
    for photo in photos:
        photo_filename = secure_filename(photo.filename)
        photo_path = os.path.join(app.config['UPLOAD_FOLDER'], photo_filename)
        photo.save(photo_path)
        logging.debug(f'Foto salva em {photo_path}')

        processed_path = os.path.join(app.config['PROCESSED_FOLDER'], photo_filename)
        add_watermark(photo_path, logo_path, processed_path, opacity=0.4)
        logging.debug(f'Foto processada salva em {processed_path}')
        processed_files.append(processed_path)

    zip_path = os.path.join(app.config['PROCESSED_FOLDER'], 'imagens_processadas.zip')
    with ZipFile(zip_path, 'w') as zipf:
        for file in processed_files:
            zipf.write(file, os.path.basename(file))

    logging.debug(f'Arquivo ZIP criado em {zip_path}')
    return send_file(zip_path, as_attachment=True)


if __name__ == '__main__':
    app.run(debug=True)
