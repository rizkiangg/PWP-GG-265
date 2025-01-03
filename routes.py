from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import check_password_hash, generate_password_hash
from models.user import User
from controller.user import register_form
from extension import db


main = Blueprint('main', __name__)

@main.route('/', methods=['GET'])
def home():
    data = User.query.all()
    return render_template('index.html', data=data)

@main.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        data = register_form()
        if data is None:
            return render_template('register.html')
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('main.login'))
    return render_template('register.html')

@main.route('/login', methods=['POST', 'GET'])
def login():
    user = None  # Initialize the user variable
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            session['user_id'] = user.id
            session['username'] = user.username
            flash('Login successful!', 'success')
            return redirect(url_for('main.tampil_data'))
        else:
            flash('Invalid username or password', 'danger')
    return render_template('login.html')

@main.route('/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    flash('You have been logged out.', 'success')
    return redirect(url_for('main.login'))

@main.route('/tampil-data', methods=['GET'])
def tampil_data():
    page = request.args.get('page', 1, type=int)
    query = request.args.get('query', '')
    if query:
        users_pagination = User.query.filter(User.username.like(f'%{query}%')).paginate(page=page, per_page=10)
    else:
        users_pagination = User.query.paginate(page=page, per_page=10)
    current_user = User.query.get(session.get('user_id'))
    return render_template('tampil-data.html', users_pagination=users_pagination, current_user=current_user, query=query)


@main.route('/edit/<int:user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
    if not is_admin():
        flash('You do not have permission to perform this action.', 'danger')
        return redirect(url_for('main.tampil_data'))
    
    user = User.query.get_or_404(user_id)
    if request.method == 'POST':
        user.username = request.form['username']
        user.email = request.form['email']
        user.role = request.form['role']
        if 'password' in request.form and request.form['password']:
            user.password_hash = generate_password_hash(request.form['password'])
        db.session.commit()
        flash('User updated successfully!', 'success')
        return redirect(url_for('main.tampil_data'))
    return render_template('edit-user.html', user=user)

@main.route('/delete/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    if not is_admin():
        flash('You do not have permission to perform this action.', 'danger')
        return redirect(url_for('main.tampil_data'))
    
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash('User deleted successfully!', 'success')
    return redirect(url_for('main.tampil_data'))

@main.route('/add-user', methods=['GET', 'POST'])
def add_user():
    if not is_admin():
        flash('You do not have permission to perform this action.', 'danger')
        return redirect(url_for('main.tampil_data'))
    
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        role = request.form['role']
        
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already exists. Please choose a different username.', 'danger')
            return redirect(url_for('main.add_user'))
        
        user = User(username=username, email=email, role=role)
        db.session.add(user)
        db.session.commit()
        flash('User added successfully!', 'success')
        return redirect(url_for('main.tampil_data'))
    return render_template('add-user.html')

def is_admin():
    user_id = session.get('user_id')
    if not user_id:
        return False
    user = User.query.get(user_id)
    return user.role == 'admin'