from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from models import db, User, Category
from forms import LoginForm, RegistrationForm, ProfileForm

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))

    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            name=form.name.data.strip(),
            email=form.email.data.lower().strip()
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()

        # Seed categories if database is new
        Category.seed_default_categories(db.session)

        login_user(user)
        flash('Welcome to Smart Expense Management! Your account was created successfully.', 'success')
        return redirect(url_for('dashboard.index'))

    return render_template('register.html', form=form)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower().strip()).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            flash(f'Welcome back, {user.name}!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('dashboard.index'))
        else:
            flash('Invalid email or password. Please verify your credentials.', 'danger')

    return render_template('login.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been successfully logged out.', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = ProfileForm(obj=current_user)
    if form.validate_on_submit():
        # Check if email changed and is taken
        if form.email.data.lower().strip() != current_user.email:
            existing = User.query.filter_by(email=form.email.data.lower().strip()).first()
            if existing:
                flash('This email is already in use by another account.', 'danger')
                return render_template('profile.html', form=form)
            current_user.email = form.email.data.lower().strip()

        current_user.name = form.name.data.strip()

        # Password update check
        if form.new_password.data:
            if not form.current_password.data or not current_user.check_password(form.current_password.data):
                flash('Current password is required and must be correct to change password.', 'danger')
                return render_template('profile.html', form=form)
            current_user.set_password(form.new_password.data)
            flash('Password changed successfully.', 'success')

        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('auth.profile'))

    return render_template('profile.html', form=form)

