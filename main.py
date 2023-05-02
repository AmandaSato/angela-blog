from flask import Flask, render_template, redirect, url_for, flash, request, abort
from flask_bootstrap import Bootstrap
from flask_ckeditor import CKEditor
from datetime import date
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from forms import CreatePostForm, RegisterForm, LoginForm, CommentForm
from flask_gravatar import Gravatar
from functools import wraps

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
ckeditor = CKEditor(app)
Bootstrap(app)
login_manager = LoginManager()
login_manager.init_app(app)
gravatar = Gravatar(app,
                    size=100,
                    rating='g',
                    default='retro',
                    force_default=False,
                    force_lower=False,
                    use_ssl=False,
                    base_url=None)

##CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


##CONFIGURE TABLES
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))
    posts = relationship("BlogPost", back_populates="author")
    comments = relationship("Comment", back_populates="author")


class BlogPost(db.Model):
    __tablename__ = "blog_posts"
    id = db.Column(db.Integer, primary_key=True)
    author = relationship("User", back_populates="posts")
    title = db.Column(db.String(250), unique=True, nullable=False)
    subtitle = db.Column(db.String(250), nullable=False)
    date = db.Column(db.String(250), nullable=False)
    body = db.Column(db.Text, nullable=False)
    img_url = db.Column(db.String(250), nullable=False)
    writer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    comments = relationship("Comment")


class Comment(db.Model):
    __tablename__ = "comments"
    id = db.Column(db.Integer, primary_key=True)
    author = relationship("User", back_populates="comments")
    date = db.Column(db.String(250), nullable=False)
    comment = db.Column(db.Text, nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('blog_posts.id'), nullable=False)
    writer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)


with app.app_context():
    db.create_all()


# Create admin-only decorator
def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # If id is not 1 then return abort with 403 error
        if current_user.id != 1:
            return abort(403)
        # Otherwise continue with the route function
        return f(*args, **kwargs)

    return decorated_function


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


@app.route('/')
def get_all_posts():
    posts = BlogPost.query.all()
    return render_template("index.html", all_posts=posts)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if request.method == 'GET':
        return render_template("register.html", form=form)

    elif request.method == 'POST':
        email = form.email.data
        existing_user = db.session.query(User).filter(User.email == email).first()

        if existing_user == None:
            name = form.name.data
            password = generate_password_hash(form.password.data, method='pbkdf2:sha256', salt_length=8)
            new_user = User(name=name, email=email, password=password)
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('get_all_posts'))
        else:
            flash('Email already registered. Please login.')
            return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if request.method == 'GET':
        return render_template("login.html", form=form)

    if request.method == 'POST':
        email_ = form.email.data
        password_ = form.password.data
        user = db.session.query(User).filter(User.email == email_).first()
        print(user)

        if user != None:
            if check_password_hash(user.password, password_):
                print("User logged in")
                login_user(user)
                return redirect(url_for('get_all_posts'))
            else:
                flash('Wrong password.')
                return render_template("login.html", form=form)
        else:
            flash('This email is not registered.')
            return render_template("login.html", form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('get_all_posts'))


@app.route("/post/<int:post_id>", methods=['GET', 'POST'])
def show_post(post_id):
    form = CommentForm()
    requested_post = BlogPost.query.get(post_id)
    comments = db.session.query(Comment).filter(Comment.post_id == post_id).all()
    if request.method == 'GET':
        return render_template("post.html", post=requested_post, form=form, comments=comments)

    if request.method == 'POST' and form.validate_on_submit():
        if current_user.is_authenticated:
            new_comment = Comment(comment=form.comment.data,
                                  post_id=requested_post.id,
                                  writer_id=current_user.id,
                                  author=current_user,
                                  date=date.today().strftime("%B %d, %Y")
                                  )
            db.session.add(new_comment)
            db.session.commit()
            return render_template("post.html", post=requested_post, form=form, comments=comments)

        elif not current_user.is_authenticated:
            flash("You need to login to leave a comment.")
            return redirect(url_for('login'))


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


@app.route("/new-post", methods=['GET', 'POST'])
@admin_only
def add_new_post():
    form = CreatePostForm(
        title='Elderly pets healthcare',
        subtitle='How to offer the best care for your old friend',
        img_url='https://images.ctfassets.net/sfnkq8lmu5d7/6xGAA5NZivPBTH9dydz23H/96d8926b66512922c66f6642abc7338a/The_Bark_Help__My_Senior_Dog_Is_Bored__hero_Stocksy_txp83086b3b8DW300_Medium_2367263.jpg?w=1000&h=750&q=70&fm=webp',
        body='body'
    )
    print(request.method)
    if request.method == 'POST' and form.validate_on_submit():
        new_post = BlogPost(
            title=form.title.data,
            subtitle=form.subtitle.data,
            body=form.body.data,
            img_url=form.img_url.data,
            author=current_user,
            writer_id=current_user.id,
            date=date.today().strftime("%B %d, %Y")
        )
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for("get_all_posts"))

    if request.method == 'GET':
        return render_template("make-post.html", form=form, is_edit=False)


@app.route("/edit-post/<int:post_id>", methods=['GET', 'POST'])
@admin_only
def edit_post(post_id):
    post = BlogPost.query.get(post_id)
    edit_form = CreatePostForm(
        title=post.title,
        subtitle=post.subtitle,
        img_url=post.img_url,
        body=post.body
    )
    if request.method == 'POST' and edit_form.validate_on_submit():
        post.title = edit_form.title.data
        post.subtitle = edit_form.subtitle.data
        post.img_url = edit_form.img_url.data
        post.body = edit_form.body.data
        db.session.commit()
        return redirect(url_for("show_post", post_id=post.id))

    if request.method == 'GET':
        return render_template("make-post.html", form=edit_form)


@app.route("/delete/<int:post_id>")
@admin_only
def delete_post(post_id):
    post_to_delete = BlogPost.query.get(post_id)
    db.session.delete(post_to_delete)
    db.session.commit()
    return redirect(url_for('get_all_posts'))


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
