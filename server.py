from flask import Flask, request, jsonify, redirect, url_for, render_template
from main import CONFIG, main

from db_crud import read_records

app = Flask(__name__)


@app.route("/", methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        CONFIG['house_config']['credit']['max'] = request.form['credit_max']
        CONFIG['house_config']['credit']['min'] = request.form['credit_min']
        CONFIG['house_config']['rent']['max'] = request.form['rent_max']
        CONFIG['house_config']['rent']['min'] = request.form['rent_min']
        CONFIG['house_config']['rooms'] = request.form['rooms']
        CONFIG['house_config']['size']['max'] = request.form['size_max']
        CONFIG['house_config']['size']['min'] = request.form['size_min']
        records = main()
        return render_template('home.html', records=records, record_count=len(records))
    else:
        records = read_records(get_all=True)
        return render_template('home.html', records=records, record_count=len(records))


if __name__ == "__main__":
    app.run(debug=True)
