#!/usr/bin/env python


from sklearn.externals import joblib

# load the trained model
rfmodel =joblib.load('model.joblib')



#### HElper functions for hashing password
import hashlib, binascii, os

def hash_password(password):
    """Hash a password for storing."""
    salt = hashlib.sha256(os.urandom(60)).hexdigest().encode('ascii')
    pwdhash = hashlib.pbkdf2_hmac('sha512', password.encode('utf-8'), 
                                salt, 100000)
    pwdhash = binascii.hexlify(pwdhash)
    return (salt + pwdhash).decode('ascii')

def verify_password(stored_password, provided_password):
    """Verify a stored password against one provided by user"""
    salt = stored_password[:64]
    stored_password = stored_password[64:]
    pwdhash = hashlib.pbkdf2_hmac('sha512', 
                                  provided_password.encode('utf-8'), 
                                  salt.encode('ascii'), 
                                  100000)
    pwdhash = binascii.hexlify(pwdhash).decode('ascii')
    return pwdhash == stored_password
#### End of helper functions



from datetime import datetime

# predict garna input array ko size (31)


# 21 columns of input hunu parxa 
# Index(['id', 'loan_amnt', 'funded_amnt', 'funded_amnt_inv', 'term', 'int_rate',
#        'installment', 'dti', 'delinq_2yrs', 'inq_last_6mths', 'pub_rec',
#        'revol_bal', 'revol_util', 'total_pymnt', 'total_rec_prncp',
#        'total_rec_int', 'total_rec_late_fee', 'recoveries',
#        'collection_recovery_fee', 'loan_status', 'purpose'],
#       dtype='object')


# after processing the categorical data the no of column increases
# Index(['loan_amnt', 'funded_amnt', 'funded_amnt_inv', 'term', 'int_rate',
#        'installment', 'dti', 'delinq_2yrs', 'inq_last_6mths', 'pub_rec',
#        'revol_bal', 'revol_util', 'total_pymnt', 'total_rec_prncp',
#        'total_rec_int', 'total_rec_late_fee', 'recoveries',
#        'collection_recovery_fee', 'loan_status', 'purpose_car',
#        'purpose_credit_card', 'purpose_debt_consolidation',
#        'purpose_home_improvement', 'purpose_house', 'purpose_major_purchase',
#        'purpose_medical', 'purpose_moving', 'purpose_other',
#        'purpose_renewable_energy', 'purpose_small_business',
#        'purpose_vacation', 'purpose_wedding'],
#       dtype='object')

inputData = {
    'loan_amt': 0,
    'funded_amt': 0,
    'funded_amt_inv': 0,
    'term': 0,
    'interest_rate': 0,
    'installment': 0,
    'dti': 0,
    'delinq_2yrs': 0,
    'inq_last_6mths': 0,
    'pub_rec': 0,
    'revol_bal': 0,
    'revol_util': 0,
    'total_payment': 0,
    'total_rec_prncp': 0,
    'total_rec_int': 0,
    'total_rec_late_fee': 0,
    'recoveries': 0,
    'collection_recovery_fee': 0,
    'purpose_car': 0,
    'purpose_credit_card': 0,
    'purpose_debt_consolidation': 0,
    'purpose_home_improvement': 0,
    'purpose_house': 0,
    'purpose_major_purchase': 0,
    'purpose_medical': 0,
    'purpose_moving': 0,
    'purpose_other': 0,
    'purpose_renewable_energy': 0,
    'purpose_small_business': 0,
    'purpose_vacation': 0,
    'purpose_wedding': 0,
}


len(inputData)



import numpy as np
inputArray = np.fromiter(inputData.values(), dtype=float)
inputArray.shape


prediction = rfmodel.predict([inputArray])
probabs = rfmodel.predict_proba([inputArray])
rfmodel.classes_



if prediction=='Charged Off':
    print ('tirdaina mula sag le')



def predict_and_prepare_result():
    #convert inputData dictionary into numpy array to send to the model for prediction
    inputArray = np.fromiter(inputData.values(), dtype=float)
    print('Input array',inputArray)
    # make prediction
    prediction = rfmodel.predict([inputArray])
    probabs = rfmodel.predict_proba([inputArray]) # [charge off confidence, fully paid confidence]
    result = {}
    if (prediction=='Charged Off'):
        # our model predicts that person applying will not be able to repay his loan (loan chukta garna sakdaina)
        result['result']='Sorry! You cannot apply for the loan'
        result['confidence'] = probabs[0][0]
    else:
        # our model predicts the persion applying will repay his loan
        result['result'] = 'Congratulations ! You can apply for the loan'
        result['confidenct'] = probabs[1][1]
    return result


#Server ko Kaam


from flask import Flask, jsonify, request, render_template, redirect, url_for, session
from flask_cors import CORS
import os



#import sql python package
from flask_mysqldb import MySQL


app = Flask(__name__)
CORS(app)

app.secret_key = os.urandom(12)

#configure the database
app.config['MYSQL_HOST'] = '127.0.0.1'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'loanprediction'

mysql = MySQL(app)

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login')
def login():
    if session.get('logged_in'):
        return render_template('loanform.html')
    else:
        return render_template('login.html')

@app.route('/login', methods=['POST'])
def loginAccount():
    email = request.form.get('email')
    password = request.form.get('password')

    cur = mysql.connection.cursor()
    #cur.execute("SELECT * FROM users WHERE email = %s AND password = %s",(email, password))
    cur.execute("SELECT * FROM users WHERE email = %s ",(email,))
    mysql.connection.commit()
    myresult = cur.fetchall()

    if(len(myresult)>0):
        # print(myresult[0][4])
        if(verify_password(myresult[0][4], password)):
            global users
            # if email not in users:
            #     users.append(email)
            # print(users)
            #set session variable
            session['logged_in'] = True
            #user registered in the database
            return redirect(url_for('loanform'))

    return render_template("login.html",error="Wrong Username Or Password")
    cur.close()

@app.route("/logout")
def logout():
    session['logged_in'] = False
    return index()

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/register', methods=['POST'])
def registerAccount():
    # register the users
    email = request.form.get('email')
    fullname = request.form.get('fullname')
    phone = request.form.get('phone')
    password = request.form.get('password')

    hashedpassword = hash_password(password)
    #store in database
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO users(account_number, fullname, email, password, phone) VALUES (%s, %s, %s, %s, %s)", (int(datetime.timestamp(datetime.now())), fullname, email, hashedpassword, phone))
    mysql.connection.commit()
    cur.close()
    #user registered in the database
    return redirect(url_for('login'))

@app.route('/loanform',methods=['GET'])
def loanform():
    if not session.get('logged_in'):
        return render_template('login.html') #if not logged in goto login page
    else:
        return render_template('loanform.html')



@app.route('/predict',methods=['POST'])
def makePrediction():
    default_value = 0
    inputData['loan_amt'] = request.form.get('loan_amount',default_value) if (request.form.get('loan_amount',default_value)!='') else 0 
    inputData['funded_amt'] = request.form.get('funded_amount',default_value) if (request.form.get('funded_amount',default_value)!='') else 0 
    inputData['term'] = request.form.get('term',default_value) if (request.form.get('term',default_value)!='') else 0 
    inputData['interest_rate'] = request.form.get('interest_rate',default_value) if (request.form.get('interest_rate',default_value)!='') else 0 
    inputData['installment'] = request.form.get('installment',default_value) if (request.form.get('installment',default_value)!='') else 0 
    inputData['dti'] = request.form.get('dti',default_value) if (request.form.get('dti',default_value)!='') else 0 
    purpose = request.form.get('purpose') if (request.form.get('purpose',default_value)!='') else 0 
    #process the purpose and then set appropriate value
    inputData['purpose_other']=1
    result = predict_and_prepare_result()
    return render_template('result.html',result=result['result'],confidence=result['confidence'])
    #return jsonify(result)
    #print(request.is_json)


# app.run(debug=True)


# if __name__ == '__main__':
#      #lrmodel=joblib.load('model.joblib')
#      app.run(port=8080)


