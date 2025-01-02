from flask import request
from models.user import User
from extension import db

def register_form():
    if request.method == "POST":
        username = request.form['username']
        email = request.form.get('email')  # Use get to avoid KeyError
        password = request.form['password']
        role = request.form['role']
        
        user = User(username=username, email=email, role=role)
        user.set_password(password)  # Store plain text password
        db.session.add(user)
        db.session.commit()
        return user