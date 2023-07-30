from flask import Flask, request, jsonify, redirect, url_for, render_template
import main

app = Flask(__name__)


@app.route("/", methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        main.CONFIG = main.get_configs()
        main.CONFIG['house_config']['credit']['max'] = request.form['credit_max']
        main.CONFIG['house_config']['credit']['min'] = request.form['credit_min']
        main.CONFIG['house_config']['rent']['max'] = request.form['rent_max']
        main.CONFIG['house_config']['rent']['min'] = request.form['rent_min']
        main.CONFIG['house_config']['rooms'] = request.form['rooms']
        main.CONFIG['house_config']['size']['max'] = request.form['size_max']
        main.CONFIG['house_config']['size']['min'] = request.form['size_min']
    else:
        return render_template('home.html')


if __name__ == "__main__":
    app.run(debug=True)
