import os
from werkzeug.utils import secure_filename
from flask import Flask, jsonify, request
from flask_cors import CORS
import ML_code


app = Flask(__name__)
CORS(app, resources={r"/analize": {"origins": "*"}})

@app.route('/analize', methods=['POST'])
def analize():
    file = None
    if request.files:
        file = request.files['file']
        fileName, fileExtension = os.path.splitext(file.filename)
        if(fileExtension == '.csv'):
            print('Received: ' + str(fileName) + str(fileExtension))
            file.save(os.path.join('temporary_saved_files', secure_filename(file.filename)))
            jsonResult = ML_code.analize(file.filename)
            os.remove(os.path.join('temporary_saved_files', secure_filename(file.filename)))
            return jsonResult
        else:
            print('Wrong extension! Received: ' + str(fileName) + str(fileExtension))
            return jsonify('Wrong extension! Only .csv files accepted! Received: ' + str(fileName) + str(fileExtension))
    else:
        print('No file received')
        return jsonify('No file received')

if __name__ == "__main__":
    app.run(debug=True)