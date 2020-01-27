from flask import *

from flask_bootstrap import Bootstrap

from flask_pymongo import PyMongo

from flask_moment import Moment

from datetime import datetime

from passlib.hash import sha256_crypt

app= Flask('the-login-system')

app.config['SECRET_KEY']='ThE_lOgIn_sYsTeM'

app.config['MONGO_URI'] = 'mongodb://localhost:27017/my-digital-diary-db'
monent=Moment(app)

Bootstrap(app)
mongo = PyMongo(app)


@app.route('/',methods =['GET','POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    elif request.method == 'POST':
        doc = {}
        '''for item in request.form:
            doc[item] = request.form[item]
        '''
        doc = {'email': request.form['email']}
        found = mongo.db.users.find_one(doc)
        if found is None:
            doc['firstname']=request.form['firstname']
            doc['lastname'] = request.form['lastname']
            doc['password'] = sha256_crypt.encrypt(request.form['password'])
            mongo.db.users.insert_one(doc)
            flash('Account created successfully!')
            return redirect('/login')
        else:
            flash('user name is taken, try another.')
            return redirect('/')


@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    elif request.method == 'POST':
        doc = {'email':request.form['email']}
        found = mongo.db.users.find_one(doc)
        passcode = found['password']
        # if the combination is incorrect
        if found is None and len(passcode) < 50:
            flash ('Here is no such user, Please sign up right now.')
            return redirect('/')
        else:
            try:

                if sha256_crypt.verify(request.form['password'], found['password']):
                    session['user-info'] = {'firstname': found['firstname'], 'lastname': found['lastname'],'email': found['email'], 'loginTime': datetime.utcnow()}
                    return redirect('/home')
                else:
                    flash('The email and password you entered did not match our record. Please double check and try again.')
                    return redirect('/login')
            except ValueError:
                flash('please sign up ')
                return redirect('/')

@app.route('/home',methods=['GET','POST'])
def home():
    if 'user-info' in session:
        if request.method == 'GET':
            savedEntries = mongo.db.entries.find({'user':session['user-info']['email']})
            return render_template('home.html',entry=savedEntries)
        elif request.method == 'POST':
            print('hi')
            print(datetime.utcnow())
            entry = {'user': session['user-info']['email'],'content':request.form['content'],'time':datetime.utcnow()}
            mongo.db.entries.insert_one(entry)
            return redirect('/home')
    else:
        flash('You need to login first!')
        return redirect('/login')

@app.route('/logout')
def logout():
    # removing user information from the session
        session.pop('user-info')
        return redirect('/login')

@app.errorhandler(404)
def page_not_found(e):
	return render_template('error.html',error=e),404

@app.errorhandler(400)
def page_not_found(e):
	return render_template('error.html',error=e),400

@app.errorhandler(500)
def page_not_found(e):
	return render_template('error.html',error=e),500

app.run(debug = True)
