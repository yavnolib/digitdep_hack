from flask import Flask, send_from_directory, jsonify, request, Response
import os
import pandas as pd
import time
import sys
import base64
from io import BytesIO
import json

sys.path.insert(1, '/mnt/')
dataf = pd.DataFrame()
from clustering_logic import Clustering

def plug(file):
    return {"112":{"unique_mats":26,
                   "unique_buyers":1,
                   "n_members":26,
                   "description": 
                       {"Труба №1" : "200 шт",
                        "Труба №3": "100 шт",
                        "Кабель длинный": "300м",
                        "Кабель короткий": "2см",
                        "Бур сильный": "12 кг",
                        "Одежда теплая": "52 комплекта",
                        "Носки спортивные Adidas": "1 пара",
                        "Мотор №112": "3 шт",
                        "Фанера 3мм": "42 листа",
                        "Фанера 5мм": "12 листов"
                       },
                   "lot_sum":31724852.0899999999,
                   "is_top":False},
            "113":{"unique_mats":1,
                   "unique_buyers":1,
                   "n_members":1,
                   "description": 
                       {"Труба №1" : "200 шт",
                        "Труба №3": "100 шт",
                        "Кабель длинный": "300м",
                        "Кабель короткий": "2см",
                        "Бур сильный": "12 кг",
                        "Одежда теплая": "52 комплекта",
                        "Носки спортивные Adidas": "1 пара",
                        "Мотор №112": "3 шт",
                        "Фанера 3мм": "42 листа",
                        "Фанера 5мм": "12 листов"
                       },
                   "lot_sum":82116.0,
                   "is_top":False},
            "114":{"unique_mats":2,
                   "unique_buyers":1,
                   "n_members":2,
                   "description": 
                       {"Труба №1" : "200 шт",
                        "Труба №3": "100 шт",
                        "Кабель длинный": "300м",
                        "Кабель короткий": "2см",
                        "Бур сильный": "12 кг",
                        "Одежда теплая": "52 комплекта",
                        "Носки спортивные Adidas": "1 пара",
                        "Мотор №112": "3 шт",
                        "Фанера 3мм": "42 листа",
                        "Фанера 5мм": "12 листов"
                       },
                   "lot_sum":1077500.1799999999,
                   "is_top": True},
            "115":{"unique_mats":2,
                   "unique_buyers":1,
                   "n_members":7,
                   "description": 
                       {"Труба №1" : "200 шт",
                        "Труба №3": "100 шт",
                        "Кабель длинный": "300м",
                        "Кабель короткий": "2см",
                        "Бур сильный": "12 кг",
                        "Одежда теплая": "52 комплекта",
                        "Носки спортивные Adidas": "1 пара",
                        "Мотор №112": "3 шт",
                        "Фанера 3мм": "42 листа",
                        "Фанера 5мм": "12 листов"
                       },
                   "lot_sum":6707769.9100000001,
                   "is_top": False}}
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
    # time.sleep(0.5)
    cl = Clustering(file, data_folder='/mnt/data', use_postgre=False)
    df, result_json = cl.transform()
    global dataf
    dataf = df
    excel_buffer = BytesIO()
    with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False)
    excel_buffer.seek(0)
    encoded_excel = base64.b64encode(excel_buffer.read()).decode('utf-8')
    json_df = {"file": encoded_excel, "json": result_json}
    json_data = json.dumps({
        "json": json.loads(result_json),
        "file": df.to_json()
    })
    return json_data

@app.route("/uploaded", methods=["POST", "GET"])
def after_upload():
    # print(request.get_json())
    df = pd.read_json(request.get_json())
    # print(file_name)
    csv_data = df.to_csv(index=False)
    
    # Возвращаем CSV-данные как вложение для скачивания
    return Response(
        csv_data,
        mimetype='text/csv',
        headers={
            "Content-Disposition": "attachment; filename=data.csv"
        }
    )

@app.route("/")
def default_page():
    return send_from_directory(app.static_folder, "index.html")
@app.route("/manifest.json")
def manifest():
    with open("./build/manifest.json") as manifest:
        return manifest
if __name__ == '__main__':
    app.run(debug=True, port=8080)
