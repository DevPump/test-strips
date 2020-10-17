#!/usr/bin/env python
from datetime import date
from os import path
import os.path
import json
from flask import Flask, render_template, request, redirect
from dotenv import load_dotenv
from waitress import serve
from flask_wtf.csrf import CSRFProtect
load_dotenv()

if os.getenv('PYTHON_SENTRY_DSN') is not None:
    import sentry_sdk
    sentry_sdk.init(
        os.getenv('PYTHON_SENTRY_DSN'),
        traces_sample_rate=1.0
    )

app = Flask(__name__, template_folder='./static')

chart_items = ['NO3', 'NO2', 'PH', 'KH', 'GH']
strip_options = {'NO3': [0, 20, 40, 80, 160, 200],
                 'NO2': [0, 0.5, 1, 3, 5, 10],
                 "PH": [6.0, 6.5, 7.0, 7.5, 8.0, 8.5, 9.0],
                 "KH": [0, 40, 80, 120, 180, 240],
                 "GH": [0, 30, 60, 120, 180],
                 "NH3/NH+4": [0, 0.25, 0.50, 1.0, 2.0, 4.0, 8.0]
                 }
appData = 'data/'


def create_missing_data_folder():
    if not path.isdir(appData):
        os.mkdir(appData)
    return True


@app.route("/")
def index():
    return render_template('index.html', strip_options=strip_options, recorded_data=get_data())


def get_data():
    data = {}
    for chart_item in chart_items:
        if path.isfile(appData + chart_item + '.txt'):
            dates = []
            data_points = []
            row_count = 0
            chart_file = open(appData + chart_item + ".txt", "r")
            for line in chart_file:
                row_count += 1
                if row_count % 2:
                    dates.append(line.rstrip('\n'))
                else:
                    data_points.append(line.rstrip('\n'))
            # Add
            data[chart_item] = {"dates": dates,
                                "dataPoint": data_points}
            chart_file.close()
    data = json.dumps(data)
    return data


@ app.route("/api/writedata", methods=['POST'])
def write_data():
    create_missing_data_folder()
    data_to_write = request.form
    for chart_item in chart_items:
        if chart_item in data_to_write:
            file_path = appData + chart_item + '.txt'
            write_method = 'a'
            leading_new_line = ""
            if not path.isfile(file_path):
                write_method = 'w+'
            else:
                leading_new_line = "\n"
            chart_file = open(file_path, write_method)
            chart_file.writelines(leading_new_line + str(date.today()) +
                                  "\n" + data_to_write[chart_item])
            chart_file.close()
    return redirect('/')


def setup_csrf():
    csrf = CSRFProtect()
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    csrf.init_app(app)
    return True


if __name__ == "__main__":
    create_missing_data_folder()
    setup_csrf()
    if os.getenv('DEBUG_STATUS') == 'True':
        app.run()
    else:
        serve(app, host="0.0.0.0", port=9004)
