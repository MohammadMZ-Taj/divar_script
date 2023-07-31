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
        return render_template('home.html', records=main())
    else:
        return render_template('home.html', records=read_records(get_all=True))


if __name__ == "__main__":
    app.run(debug=True)
