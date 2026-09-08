from datetime import date
from flask import Flask, abort, render_template, redirect, url_for, flash,request
from flask_bootstrap import Bootstrap5
from flask_ckeditor import CKEditor
from typing import List
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Text, ForeignKey
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
import os

from forms import CreatePostForm,RegisterUserForm,LoginUserForm,CommentForm

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")
ckeditor = CKEditor(app)
Bootstrap5(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "/login"

# CREATE DATABASE
class Base(DeclarativeBase):
    pass
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DB_URI",'sqlite:///blog.db')
db = SQLAlchemy(model_class=Base)
db.init_app(app)

# Parent Table
class User(db.Model,UserMixin):
    __tablename__ = "users"
    id : Mapped[int] = mapped_column(Integer,primary_key=True)
    name : Mapped[str] = mapped_column(String,nullable=False)
    email : Mapped[str] = mapped_column(String,unique=True,nullable=False)
    hashed_password : Mapped[str] = mapped_column(String,nullable=False)
    blog_posts : Mapped[List["BlogPost"]] = relationship(back_populates = "author")
    blog_comments : Mapped[List["BlogComment"]] = relationship(back_populates = "author")

# Child Table
class BlogPost(db.Model):
    __tablename__ = "blog_posts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    subtitle: Mapped[str] = mapped_column(String(250), nullable=False)
    date: Mapped[str] = mapped_column(String(250), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    img_url: Mapped[str] = mapped_column(String(250), nullable=False)
    author_id : Mapped[int] = mapped_column(ForeignKey("users.id"))
    author : Mapped["User"] = relationship(back_populates="blog_posts")
    blog_comments : Mapped[List["BlogComment"]] = relationship(back_populates = "post")

class BlogComment(db.Model):
    __tablename__ = "comments"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    author_id : Mapped[int] = mapped_column(ForeignKey("users.id"))
    post_id : Mapped[int] = mapped_column(ForeignKey("blog_posts.id"))
    author : Mapped["User"] = relationship(back_populates="blog_comments")
    post : Mapped["BlogPost"] = relationship(back_populates="blog_comments")

with app.app_context():
    db.create_all()

@app.context_processor
def global_injection():
    return {
        "current_year" : date.today().year
    }

@login_manager.user_loader
def user_loader(user_id):
    return db.session.get(User,int(user_id))

def admin_only(func):
    @wraps(func)
    def wrapper(*args,**kwargs):
        if current_user.get_id() != "1":
            return "<h1>Unauthorized Access</h1><p>You need to be an Admin to access this page</p>",401
        else:
            return func(*args,**kwargs)
    return wrapper

@app.route('/register',methods = ["POST","GET"])
def register():
    form = RegisterUserForm()
    if form.validate_on_submit():
        if db.session.scalar(db.select(User).where(User.email == form.email.data)) is not None:
            flash("The Email ID entered is already registered, log in through the same")
            return redirect(url_for("login"))
        hashed_password = generate_password_hash(form.password.data)
        user = User(name = form.name.data,email = form.email.data, hashed_password = hashed_password)
        db.session.add(user)
        db.session.commit()
        login_user(user,remember=True)
        return redirect(url_for('get_all_posts'))
    return render_template("register.html",form = form)


@app.route('/login',methods=["GET","POST"])
def login():
    form = LoginUserForm()
    if form.validate_on_submit():
        user = db.session.scalar(db.select(User).where(User.email == form.email.data))
        if user is None:
            flash("The Email ID entered is not registered")
            return redirect(url_for('login'))
        elif not check_password_hash(user.hashed_password,form.password.data):
            flash("The Password entered is incorrect")
            return redirect(url_for('login'))
        else:
            login_user(user,remember=True)
            return redirect(request.args.get("name") or url_for('get_all_posts'))
    return render_template("login.html",form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('get_all_posts'))


@app.route('/')
def get_all_posts():
    result = db.session.execute(db.select(BlogPost))
    posts = result.scalars().all()
    return render_template("index.html", all_posts=posts)


@app.route("/post/<int:post_id>",methods=["GET","POST"])
def show_post(post_id):
    requested_post = db.get_or_404(BlogPost, post_id)
    form = CommentForm()
    if form.validate_on_submit():
        if not current_user.is_authenticated:
            flash("Log in to comment on posts")
            return redirect(url_for("login",next=request.path))
        else:
            comment = BlogComment(body = form["body"].data,author = current_user,post=requested_post)
            db.session.add(comment)
            db.session.commit()
            return redirect(request.path)

    return render_template("post.html", post=requested_post,form=form,comments = requested_post.blog_comments)


@app.route("/new-post", methods=["GET", "POST"])
@admin_only
def add_new_post():
    form = CreatePostForm()
    if form.validate_on_submit():
        new_post = BlogPost(
            title=form.title.data,
            subtitle=form.subtitle.data,
            body=form.body.data,
            img_url=form.img_url.data,
            author=current_user,
            date=date.today().strftime("%B %d, %Y")
        )
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for("get_all_posts"))
    return render_template("make-post.html", form=form)


@app.route("/edit-post/<int:post_id>", methods=["GET", "POST"])
@admin_only
def edit_post(post_id):
    post = db.get_or_404(BlogPost, post_id)
    edit_form = CreatePostForm(
        title=post.title,
        subtitle=post.subtitle,
        img_url=post.img_url,
        author=post.author,
        body=post.body
    )
    if edit_form.validate_on_submit():
        post.title = edit_form.title.data
        post.subtitle = edit_form.subtitle.data
        post.img_url = edit_form.img_url.data
        post.author = current_user
        post.body = edit_form.body.data
        db.session.commit()
        return redirect(url_for("show_post", post_id=post.id))
    return render_template("make-post.html", form=edit_form, is_edit=True)


@app.route("/delete/<int:post_id>")
@admin_only
def delete_post(post_id):
    post_to_delete = db.get_or_404(BlogPost, post_id)
    db.session.delete(post_to_delete)
    db.session.commit()
    return redirect(url_for('get_all_posts'))


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


if __name__ == "__main__":
    app.run()
