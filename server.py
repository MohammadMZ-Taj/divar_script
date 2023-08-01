from flask import Flask, request, render_template
from main import CONFIG, start_app
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
        records = start_app()
        return render_template('home.html', records=records, record_count=len(records),
                               latest_config=CONFIG['house_config'])
    else:  # GET request
        records = read_records()
        return render_template('home.html', latest_config=CONFIG['house_config'], records=records,
                               record_count=len(records))


if __name__ == "__main__":
    app.run(debug=True)