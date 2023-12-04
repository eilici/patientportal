from flask import Flask
from flask_cors import CORS
from flask import render_template
from flask import request
import sqlite3
import pandas as pd
from pathlib import Path

app = Flask(__name__)

CORS(app)

Path('patientportal.db').touch()

conn = sqlite3.connect('patientportal.db',check_same_thread=False)
c = conn.cursor()

doctor = pd.read_sql_query("SELECT * FROM doctor", conn)
patient = pd.read_sql_query("SELECT * FROM patient", conn)
patient_billing = pd.read_sql_query("SELECT * FROM patient_billing", conn)
test = pd.read_sql_query("SELECT * FROM test", conn)
test_details = pd.read_sql_query("SELECT * FROM test_details", conn)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/views', methods =['GET', 'POST'])
def views():
    return render_template('views.html')

@app.route('/inserts', methods =['GET', 'POST'])
def inserts():
    return render_template('inserts.html')

@app.route('/getAllDoctors', methods=['GET', 'POST'])
def get_doctors():
    c.execute("SELECT * FROM doctor")
    results = c.fetchall()
    return(results)

@app.route('/getPatientsOnly', methods=['GET', 'POST'])
def get_patients_only():
    c.execute("SELECT * FROM patient")
    results = c.fetchall()
    return(results)

@app.route('/getAllPatients', methods=['GET', 'POST'])
def get_patients():
    c.execute("SELECT * FROM patient JOIN patient_billing using (patient_id)")
    results = c.fetchall()
    return(results)

@app.route('/getAllTestResults', methods=['GET', 'POST'])
def get_test_results():
    c.execute("SELECT * FROM test JOIN test_details using (test_id) WHERE test.processed = 1")
    results = c.fetchall()
    return(results)

@app.route('/getTestStatus', methods=['GET', 'POST'])
def get_test_status():
    c.execute("SELECT test.test_id, test.processed FROM test")
    results = c.fetchall()
    return(results)

@app.route('/getAllTests', methods=['GET', 'POST'])
def get_test_all():
    c.execute("SELECT * FROM test")
    results = c.fetchall()
    return(results)

@app.route('/getPatientTests', methods = ['GET','POST'])
def get_patient_tests():
    patient_id = request.args.get("patient_id", None)
    
    if (patient_id == "patient_id"):
        return []

    c.execute("SELECT * FROM test WHERE test.patient_id = " + patient_id)
    results = c.fetchall()
    return (results)

#/<string:patient_id>/<string:name>/<string:gender>/<string:email>/<string:billing_address>/<string:zipcode>/<string:state>/<string:city>
#patient_id, name, gender, email, billing_address, zipcode, state, city
@app.route('/addNewPatient', methods = ['PATCH','GET'])
def add_new_patient():
    patient_id = request.args.get("patient_id", None)
    name = request.args.get("name", None)
    gender = request.args.get("gender", None)
    email = request.args.get("email", None)
    billing_address = request.args.get("billing_address", None)
    zipcode = request.args.get("zipcode", None)
    state = request.args.get("state", None)
    city = request.args.get("city", None)

    sql_statement_p = "INSERT INTO patient(patient_id, name, gender, email) values("  + patient_id +",'"+name+"','"+gender+"','"+email+"')"
    sql_statement_pb = "INSERT INTO patient_billing(patient_id, billing_address, zipcode, state, city) values("  + patient_id +",'"+billing_address+"',"+zipcode+",'"+state+"','"+city+"')"

    try:
        c.execute(sql_statement_p)
        c.execute(sql_statement_pb)
        #conn.commit()
    except sqlite3.Error as er:
        c.execute("SELECT * FROM patient JOIN patient_billing using (patient_id) where patient.patient_id = " + patient_id )
        check_mistake = c.fetchall()
        # if error happens in execution, revert creation
        if (check_mistake == []):
            c.execute("DELETE FROM patient WHERE patient_id = " + patient_id)
            c.execute("DELETE FROM patient_billing WHERE patient_id = " + patient_id)
        return('SQLite error: %s' % (' '.join(er.args)))

   # c.execute(sql_statement_p)
   # c.execute(sql_statement_pb)
    conn.commit()
    return "success"

#/<string:doctor_id>/<string:phone_number>/<string:work_address>/<string:work_zipcode>/<string:work_state>/<string:work_city>
# doctor_id, phone_number, work_address, work_zipcode, work_state, work_city
@app.route('/addNewDoctor', methods = ['PATCH','GET'])
def add_new_doctor():
    doctor_id = request.args.get("doctor_id", None)
    phone_number = request.args.get("phone_number", None)
    work_address = request.args.get("work_address", None)
    work_zipcode = request.args.get("work_zipcode", None)
    work_state = request.args.get("work_state", None)
    work_city = request.args.get("work_city", None)

    sql_statement_d = "INSERT INTO doctor(doctor_id, phone_number, work_address, work_zipcode, work_state, work_city) values(" + doctor_id + "," + phone_number + ",'" + work_address +"'," + work_zipcode +",'" + work_state + "','" + work_city +"')"
   
    try:
        c.execute(sql_statement_d)
       # conn.commit()
    except sqlite3.Error as er:
        return('SQLite error: %s' % (' '.join(er.args)))

    #c.execute(sql_statement_d)
    conn.commit()
    return "success"

# <string:test_id>/<string:patient_id>/<string:doctor_id>/<string:order_date>
#test_id, patient_id, doctor_id, order_date
@app.route('/addTest', methods=['GET', 'POST'])
def add_new_test():
    test_id = request.args.get("test_id", None)
    patient_id = request.args.get("patient_id", None)
    doctor_id = request.args.get("doctor_id", None)
    order_date = request.args.get("order_date", None)

    sql_statement_t = "INSERT INTO test(test_id, patient_id, doctor_id, order_date, processed) values(" + test_id + "," + patient_id + ",'" + doctor_id +"'," + order_date +", 0)"
   
    try:
        c.execute(sql_statement_t)
       # conn.commit()
    except sqlite3.Error as er:
        return('SQLite error: %s' % (' '.join(er.args)))

    # processed is automatically false
    #c.execute(sql_statement_t)
    conn.commit()
    return "success"

#/<string:test_id>/<test_type>/<string:test_results>
#test_id, test_type, test_results
@app.route('/addTestResults', methods=['GET', 'POST'])
def add_test_results():
    test_id = request.args.get("test_id", None)
    test_type = request.args.get("test_type", None)
    test_results = request.args.get("test_results", None)

    sql_statement_tr = "INSERT INTO test_details(test_id, test_type, test_results) values (" + test_id + ",'" + test_type + "'," + test_results +")"
    sql_statement_tu = "UPDATE test SET processed = 1 WHERE test_id = "+ test_id

    try:
        c.execute(sql_statement_tr)
        c.execute(sql_statement_tu)
        #conn.commit()
    except sqlite3.Error as er:
        return('SQLite error: %s' % (' '.join(er.args)))

   
    #c.execute(sql_statement_t)
    conn.commit()
    return "success"

if __name__ == '__main__':
    with app.app_context():
        print(doctor)
        print(patient)
        print(patient_billing)
        print(test)
        print(test_details)

        app.run()