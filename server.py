from flask import Flask, request, render_template
from main import CONFIG, main

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
        return render_template('home.html', records=records, record_count=len(records), my_config=CONFIG['house_config'])
    else:

        return render_template('home.html', my_config=CONFIG['house_config'])


if __name__ == "__main__":
    app.run(debug=True)
