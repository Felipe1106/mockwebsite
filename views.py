from flask import Blueprint, render_template, request, flash, jsonify, url_for, redirect
from flask_login import login_required, current_user
from .forms import UpdateAccountForm
from .models import Note, db, User
import json
import secrets
import os
from __init__ import app
from PIL import Image

view = Blueprint('views', __name__)

@view.route('/', methods = ['GET','POST'])
@login_required
def home():
    if request.method == "POST":
        note = request.form.get('note')
        if len(note) < 1:
            flash('Messaage is too short!', category='error')
        else:
            new_note = Note(data = note, user_id = current_user.id)
            db.session.add(new_note)
            db.session.commit()
            flash('Note added', category='success')
    return render_template("home.html", user=current_user)

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/builtin', picture_fn)
    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    return picture_fn


@view.route('/account', methods=['GET', 'POST'])
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file


        current_user.username = form.username.data
        current_user.email = form.email .data
        db.session.commit()
        flash('Your account has been updated', 'success')
        return redirect(url_for('views.account'))
    elif request.method == "GET":
        form.username.data = current_user.username
        form.email.data = current_user.email


    image_file = url_for('static', filename='builtin/' + current_user.image_file)
    return render_template('account.html', user=current_user, image_file=image_file, form=form)




@view.route('/delete-note', methods = ["POST"])
def delete_note():
    note = json.loads(request.data)
    noteId = note['noteId']
    note = Note.query.get(noteId)
    if note:
        if note.user_id == current_user.id:
            db.session.delete(note)
            db.session.commit()
    return jsonify({})