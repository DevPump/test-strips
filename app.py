from datetime import date
from os import path
import os.path
import json
from flask import Flask, render_template, request, redirect
from dotenv import load_dotenv
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
                 "GH": [0, 30, 60, 120, 180]
                 }
appData = 'data/'
# Create missing data directory.
if not path.isdir(appData):
    os.mkdir(appData)


@app.route("/")
def index():
    return render_template('index.html', strip_options=strip_options)


@app.route('/api/getdata')
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


if __name__ == "__main__":
    app.run()
