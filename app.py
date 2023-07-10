from flask import Flask,render_template,request, flash, session, redirect, url_for
from flask_mysqldb import MySQL
from flask_bootstrap import Bootstrap
from flask_ckeditor import CKEditor
import yaml
import os
from werkzeug.security import generate_password_hash, check_password_hash
from wtforms import TextAreaField


app = Flask(__name__)
Bootstrap(app)
#Bootstrap İşlemi

db = yaml.load(open('db.yaml'),Loader=yaml.FullLoader)

app.config['MYSQL_HOST'] = db['mysql_host']
app.config['MYSQL_USER'] = db['mysql_user']
app.config['MYSQL_PASSWORD'] = db['mysql_password']
app.config['MYSQL_DB'] = db['mysql_db']
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

app.config['SECRET_KEY'] = os.urandom(24)
mysql = MySQL(app)

CKEditor(app)

@app.route('/', methods=['GET','POST'])
def index():
    cur =  mysql.connection.cursor()
    result = cur.execute("SELECT * FROM flask_test.blog")
    if result > 0:
        blogs = cur.fetchall()
        cur.close()
        return render_template('index.html', blogs=blogs)
    cur.close()
    return render_template('index.html', blogs=None)

@app.route('/about/')
def about():
    return render_template('about.html')

@app.route('/register/',methods=['GET','POST'])
def register():
    if request.method == 'POST':
        userDetails = request.form
        if userDetails['password'] != userDetails['confirm_password']:
            flash('Password do not match! Try again','danger')
            return render_template('register.html')
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO users(firstname,lastname,username,email,password) VALUES(%s,%s,%s,%s,%s)",(userDetails.firstname,userDetails.lastname,userDetails.username,userDetails.email,userDetails.password))
        mysql.connection.commit()
        cur.close()
        flash('Registration successful! Please Login!','success')
        return redirect('/login')
    return render_template('register.html')

@app.route('/login/',methods=['GET','POST'])
def login():
    if request.method == "POST":
        user_form = request.form
        username = user_form['username']
        cur = mysql.connection.cursor()
        result = cur.execute("SELECT * FROM flask_test.users  WHERE username = %s",([username]))
        if result > 0:
            _user = cur.fetchone()
            if check_password_hash(_user['password'],user_form['password']):
                session['login'] = True
                session['firstname'] = _user['firstname']
                session['lastname'] = _user['lastname']
                flash('Welcome '+ session['firstname'] + '! You have been successfull logged in','succcess')
            else:
                cur.close()
                flash('Password does not match','danger')
                return render_template('login.html')
        else:
            cur.close()
            flash('User not found!','danger')
            return render_template('login.html')
        cur.close()
        return redirect('/')
    return render_template('register.html')


@app.route('/blogs/<int:id>/')
def blogs(id):
    cur = mysql.connection.cursor()
    result = cur.execute("SELECT * FROM flask_test.users  WHERE blogid = {}".format(id)) 
    if result > 0:
        blog = cur.fetchone() 
        return  render_template('blogs.html',blog=blog)
    return "Blog not found"


#BLOG : ADD
@app.route('/add-blog/',methods=['GET','POST'])
def add_blog(id):
    if request.method == 'POST':
        blogPost = request.form
        title = blogPost['title']
        body = blogPost['body']
        author = session['firstname'] + ' ' + session['lastname']
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO blogs(title, body, author) VALUES(%s,%s,%s)",(title,body,author))
        mysql.connection.commit()
        cur.close()
        flash("Successfully posted new blog!",'success')
        return redirect('/')
    return render_template('add-blog.html')

# BLOG : LIST
@app.route('/my-blogs/',methods=['GET','POST'])
def my_blogs(id):
    author = session['firstname'] + ' ' + session['lastname']
    cur = mysql.connection.cursor()
    result = cur.execute("SELECT * FROM flask_test.blogs  WHERE author = %s",[author]) 
    if result > 0:
        blogs = cur.fetchall() 
        return  render_template('blogs.html',blogs=blogs)
    else:
        return render_template('my-blogs.html', blog=None)
    

# BLOG : EDIT
@app.route('/edit-blog/<int:id>',methods=['GET','POST'])
def edit_blog(id):
    if request.method == 'POST':
        cur = mysql.connection.cursor()
        blogPost = request.form
        title = blogPost['title']
        body = blogPost['body']
        cur.execute("UPDATE blogs SET title=%s ,body=%s , WHERE id = %s",(title,body,id))
        mysql.connection.commit()
        cur.close()
        flash("Successfully updated blog!",'success')
        return redirect('/blogs/{}'.format(id))
    cur = mysql.connection.cursor()
    result = cur.execute("SELECT * FROM flask_test.blogs  WHERE id = {}".format(id)) 
    if result > 0:
        blog = cur.fetchone() 
        blog_form = {}
        blog_form['title'] = blog['title']
        blog_form['body'] = blog['body']
        return render_template('edit-blog.html', blog_form = blog_form)

# BLOG : DELETE
@app.route('/delete-blog/<int:id>',methods=['POST'])
def delete_blog(id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM blogs WHERE id = {}".format(id))
    mysql.connection.commit()
    flash("Your blog has been deleted.",'success')
    return redirect('/my-blogs')

# LOGOUT
@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.",'info')
    return redirect('/')
if __name__ == '__main__':
    app.run(debug=True)