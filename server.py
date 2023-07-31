from flask import Flask, request, jsonify, redirect, url_for, render_template
from main import CONFIG, main

from db_crud import read_records

app = Flask(__name__)


@app.route("/", methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        CONFIG['house_config']['credit']['max'] = int(request.form['credit_max'])
        CONFIG['house_config']['credit']['min'] = int(request.form['credit_min'])
        CONFIG['house_config']['rent']['max'] = int(request.form['rent_max'])
        CONFIG['house_config']['rent']['min'] = int(request.form['rent_min'])
        CONFIG['house_config']['rooms'] = request.form['rooms']
        CONFIG['house_config']['size']['max'] = int(request.form['size_max'])
        CONFIG['house_config']['size']['min'] = int(request.form['size_min'])
        records = main()
        latest_config = {
            'credit_max':CONFIG['house_config']['credit']['max'],
            'credit_min': CONFIG['house_config']['credit']['max'],
            'rent_max': CONFIG['house_config']['rent']['max'],
            'rent_min': CONFIG['house_config']['rent']['min'],
            'rooms': CONFIG['house_config']['rooms'],
        }
        return render_template('home.html', records=records, record_count=len(records), my_config=CONFIG['house_config'])
    else:

        return render_template('home.html', my_config=CONFIG['house_config'])


if __name__ == "__main__":
    app.run(debug=True)
