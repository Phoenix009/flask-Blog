import secrets
import os
from PIL import Image

from flask_blog.models import User, Post
from flask import render_template, flash, redirect, request, url_for, abort
from flask_blog.forms import RegistrationForm, LoginForm, UpdateAccountForm, PostForm
from flask_blog import app, db, bcrypt
from flask_login import login_user, current_user, logout_user, login_required



@app.route('/home')
@app.route("/")
def home():
    page = request.args.get("page", 1, type=int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
    return render_template("home.html", posts=posts)


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect("home")

    form = RegistrationForm()

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode("utf-8")
        
        newUser = User(
            username = form.username.data,
            email = form.email.data,
            password = hashed_password
        )
        
        db.session.add(newUser)
        db.session.commit()

        flash("Account Created Successfully", "success")
        return redirect('login')

    return render_template("register.html", form = form)


@app.route("/login", methods=['POST', 'GET'])
def login():

    if current_user.is_authenticated:
        return redirect("home")
    
    
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if not user:
            flash("User does not exist", "danger")
        else:
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user, remember = form.remember.data)
                flash('Login Successful', "success")
                next_page = request.args.get("next")
                return redirect(next_page) if next_page else redirect("home")
            else:
                flash("Incorrect Password", "danger")

    return render_template("login.html", form = form)



@app.route("/logout")
def logout():
    logout_user()
    return redirect("home")



def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, ext = os.path.splitext(form_picture.filename)
    picture_fname = random_hex + ext
    picture_path = os.path.join(app.root_path, "static/profile_pic", picture_fname)
    
    size = (125, 125)
    image = Image.open(form_picture)
    image.thumbnail(size)
    image.save(picture_path)
    return picture_fname




@app.route("/account", methods=["GET", "POST"])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            filename = save_picture(form.picture.data)
            current_user.image_file = filename

        current_user.username = form.username.data
        current_user.email = form.email.data

        db.session.commit()
        flash("Account Updated Successfully", "success")
        return redirect("account")

    elif request.method == "GET":
        form.username.data = current_user.username
        form.email.data = current_user.email

    image_file = url_for("static", filename = f"profile_pic/{current_user.image_file}")
    return render_template("account.html", image_file = image_file, form=form)



@app.route("/post/new", methods=["GET", "POST"])
@login_required
def new_post():
    form = PostForm()

    if form.validate_on_submit():
        post = Post(
            title = form.title.data,
            content = form.content.data,
            author_id = current_user.id
        )

        db.session.add(post)
        db.session.commit()

        flash("Post Created Successfully", "success")
        return redirect(url_for("home"))
    return render_template("create_post.html", form=form)



@app.route("/post/<int:post_id>")
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template("post.html", post=post)


@app.route("/post/<int:post_id>/update", methods=["GET", "POST"])
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    else:
        form = PostForm()
        if form.validate_on_submit():
            post.title = form.title.data
            post.content = form.content.data
            db.session.commit()
            flash("Post Updated Successfully", "success")
            return redirect(url_for("post", post_id=post.id))
        elif request.method=="GET":
            form.title.data = post.title
            form.content.data = post.content
            return render_template("create_post.html", form=form)


@app.route("/delete_post/<int:post_id>", methods=["POST"])
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash("Post Deleted Successfully", "success")
    return redirect(url_for("home"))



@app.route("/user/<string:username>")
def user_posts(username):
    page = request.args.get("page", 1, type=int)
    user = User.query.filter_by(username = username).first_or_404()
    posts = Post.query.filter_by(author=user)\
        .order_by(Post.date_posted.desc())\
        .paginate(page=page, per_page=5)
    return render_template("user_post.html", posts=posts, user=user)