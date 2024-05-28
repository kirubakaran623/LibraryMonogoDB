from flask import Flask, request, session, render_template, redirect, flash, url_for
from pymongo import MongoClient 
from bson.objectid import ObjectId
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length
from werkzeug.security import generate_password_hash, check_password_hash
import re

app=Flask(__name__)

app.secret_key='Karan@11'

mongo_url='mongodb://localhost:27017/'

client=MongoClient(mongo_url)

db=client.Library
collection=db.details
collection_signup=db.signup

def isloggedin():
    
    return 'user_name' in session

def is_password_storng(Password):
    if len(Password)<8 :
        return False
    if not re.search(r"[a-z]", Password) or not re.search(r"[A-Z]", Password) or not re.search(r"\d",Password):
        return False
    if not re.search(r"[!@#$%^&*()-+{}|\"<>]?", Password):
        return False
 
    return True

class User:
    def __init__(self, username, password):
        self.username=username
        self.password=password
        
class signup_form(FlaskForm):
    username=StringField("username",validators=[InputRequired(), Length(min=4, max=20)])
    password=PasswordField('password',validators=[InputRequired(), Length(min=8, max=50)])
    submit=SubmitField('Signup')
    
class login_form(FlaskForm):
    username=StringField("username",validators=[InputRequired(), Length(min=4, max=20)])
    password=PasswordField('password',validators=[InputRequired(), Length(min=8, max=50)])
    submit=SubmitField('Login')

@app.route('/',methods=['GET','POST'])
def signup():
    
    form=signup_form()
    if form.validate_on_submit():
        username=form.username.data
        password=form.password.data
         
        if not is_password_storng(password):
            flash('password should be must be long')
            
            return redirect(url_for('signup'))
        
        hashed_password=generate_password_hash(password)
        
        old_user=collection_signup.find_one({'Name':username})
        
        if old_user:
            flash('username already taken. please choose a different one.','danger')
            
            return render_template('signup.html',form=form)
        
        signup_data=collection_signup.insert_one({'username':username,'password':hashed_password})
        print(signup_data)
        flash('signup successful')
        
        return redirect(url_for('login'))
    return render_template('signup.html',form=form)

@app.route('/login',methods=['GET','POST'])
def login():
    
    form=login_form()
    if form.validate_on_submit():
        username=form.username.data
        password=form.password.data
        
        record=collection_signup.find_one({'username':username})
        
        if record and check_password_hash(record['password'],password):
                user=User(username=record['username'], password=record['password'])
                session['user_name']=user.username
                
                flash('Login successful')
                return redirect(url_for('dashbord'))
        else:
            flash('invalid credential','danger')
         
    return render_template('login.html',form=form)


@app.route('/dashbord')
def dashbord():
    if isloggedin():
        user_id=session['user_name']
        
        data=collection.find({'user_name':user_id})
        return render_template('dashbord.html',data=data)

@app.route('/add',methods=['GET','POST'])
def add():
    if request.method=='POST':
        book_name=request.form['Book_name']
        book_id=request.form['Book_id']
        auther_name=request.form['Author_name']
        status=request.form['Status']

        Name=session['user_name']

        library={'user_name':Name,
                 'Book_name':book_name,
                 'Book_id': book_id,
                 'Author_name':auther_name,
                 'Status':status}
    
        collection.insert_one(library)
        
        return redirect(url_for('dashbord'))
    return render_template('add.html')

@app.route('/edit/<string:id>',methods=['GET','POST'])
def edit(id):
    empty={}
    if request.method=='POST':
        book_id=request.form['Book id']
        book_name=request.form['Book name']
        author_name=request.form['Author name']
        status=request.form['Status']

        empty.update({'Book_id': book_id})
        empty.update({'Book_name':book_name})
        empty.update({'Author_name':author_name})
        empty.update({'Status':status})
        
        collection.update_one({"_id":ObjectId(id)},{"$set":{"Book_id":book_id,"Book_name":book_name,"Author_name":author_name,"Status":status}})
        return redirect(url_for("dashbord"))
    data=collection.find_one({"_id":ObjectId(id)})
    return render_template("edit.html",data=data)

@app.route('/delete/<string:id>')
def delete(id):
    collection.delete_one({"_id":ObjectId(id)})
    return redirect(url_for("dashbord"))  

@app.route('/logout')
def logout():
    session.pop('user',None)
    flash('logged out successful')
    return redirect(url_for('login'))

if __name__=='__main__':
    app.run(debug=True)