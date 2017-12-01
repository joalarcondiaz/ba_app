from flask import Flask, request, jsonify, render_template, make_response, session
from random import randint
import time

import db_func
import local_func

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 1
app.config['SECRET_KEY'] = 'WeXiLeDiJo'


@app.route("/test", methods=["GET"])
def html_test():
    #return render_template('test.html')
    session['session_id'], session['questions'] = db_func.db_get_input()
    estimate = randint(1, 3)
    return render_template('results.html', questions=session['questions'], estimate=estimate)


@app.route("/", methods=["GET"])
def html_index():
    session['session_id'],session['questions'] = db_func.db_get_input()
    return render_template('index.html', questions=session['questions'])


@app.route("/results", methods = ["POST"])
def html_index_post():
    # Send logs
    log_affdex = []
    log_xlabs = []
    log_events = []

    if "log_affdex" in request.form: log_affdex = request.form.get("log_affdex", None)
    if "log_xlabs" in request.form: log_xlabs = request.form.get("log_xlabs", None)
    if "log_events" in request.form: log_events = request.form.get("log_events", None)

    log_affdex = log_affdex.split('\r\n')
    log_xlabs = log_xlabs.split('\r\n')
    log_events = log_events.split('\r\n')

    db_func.db_store_results(session['session_id'],log_affdex,log_xlabs,log_events)
    local_func.local_save(session['questions'],log_affdex,log_xlabs,log_events)

    # Wait for results
    time.sleep(3)

    # Get the estimated value from the model
    estimate = randint(1,3)
    db_func.db_store_prediction(session['session_id'],estimate)

    # Show the results page
    #return make_response(jsonify("do nothing for now")), 204
    return render_template('results.html', questions=session['questions'], estimate=estimate)


@app.route("/results_post", methods = ["POST"])
def html_results():
    # Get ground truth from the user
    ground_truth = request.form.get("log_res", None)

    # Store ground truth in the db
    db_func.db_store_truth(session['session_id'],ground_truth)

    # Do nothing else
    return make_response(jsonify("do nothing for now")), 204


if __name__ == "__main__":
    app.run(port=5000, host='0.0.0.0')

