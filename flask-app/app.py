from flask import Flask, send_from_directory, jsonify, request
import os
import pandas as pd
import os
import time

def plug(file):
    return {"1": {"description": "чета про первый лот",
                  "start_date": "25.05.2004",
                  "end_date": "28.09.2024"},
            "2": {"description": "чета про втооой лот",
                  "start_date": "25.05.2004",
                  "end_date": "28.09.2024"},
            "3": {"description": "чета про третий лот",
                  "start_date": "25.05.2004",
                  "end_date": "28.09.2024"},
            "4": {"description": "чета про четвертый лот",
                  "start_date": "25.05.2004",
                  "end_date": "28.09.2024"}}
app = Flask(__name__, static_folder='build', template_folder='build')

# file_counter = 0
@app.route('/static/<path:path>')
def static_files(path):
    return send_from_directory(os.path.join(app.static_folder, 'static'), path)

@app.route('/api/upload', methods=["POST"])
def get_data():
    global file_counter
    # request.files
    # req = request.files["file"]
    file_name = [key for key in request.files.keys()][0]
    file = pd.read_excel(request.files[file_name])

    # print(req)
    # os.makedirs("uploaded_files")
    file.to_csv("./uploaded_files/" + ".".join(file_name.split(".")[:-1]) + ".csv")
    # file_counter += 1
    time.sleep(0.5)
    return jsonify(plug(file))
# @app.route("/uploaded")
# def after_upload():
#     return send_form_directory(app.static_folder, )
@app.route("/")
def default_page():
    return send_from_directory(app.static_folder, "index.html")
@app.route("/manifest.json")
def manifest():
    with open("./build/manifest.json") as manifest:
        return manifest
if __name__ == '__main__':
    app.run(debug=True, port=8080)
