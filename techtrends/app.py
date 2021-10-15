import logging
import sys
import sqlite3
from sqlite3.dbapi2 import Connection

from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash
from werkzeug.exceptions import abort


from logging.config import dictConfig

logFormat = '%(levelname)s:%(module)s:%(asctime)s,  %(message)s'
logging.basicConfig(format=logFormat, datefmt="%M-%D-%Y %H:%M:%S", level=logging.DEBUG)
logging.Formatter("%(asctime)s;%(levelname)s;%(message)s","%m-%d-%Y %H:%M:%S")
logService = logging.getLogger()
errStream = logging.StreamHandler(sys.stderr)
outStream = logging.StreamHandler(sys.stdout)
logService.addHandler(errStream)
logService.addHandler(outStream)
# We define a global variable to keep count of connections so far.
connectionCount = 0

# Function to get a database connection.
# This function connects to database with the name `database.db`
def get_db_connection():
    global connectionCount
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    connectionCount += 1
    return connection

# Function to get a post using its ID
def get_post(post_id):
    connection = get_db_connection()
    post = connection.execute('SELECT * FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
    connection.close()
    return post

# Define the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'

# Route that shouws the application health
@app.route('/healthz')
def healthCheck():
    return app.response_class(
        response=json.dumps({"result": "OK - healthy"}),
        status=200,
        mimetype="application/json"
    )

@app.route('/metrics')
def metrics():
    global connectionCount
    connection = get_db_connection()
    postCount = connection.execute('SELECT COUNT(*) FROM posts').fetchone()
    connection.close()
    return app.response_class(
        response=json.dumps({
            "db_connection_count" : connectionCount,
            "post_count" : postCount[0]
        }),
        status=200,
        mimetype="application/json"
    )

# Define the main route of the web application 
@app.route('/')
def index():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    return render_template('index.html', posts=posts)

# Define how each individual article is rendered 
# If the post ID is not found a 404 page is shown
@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    if post is None:
      logging.info("Nonexistent post tried to be accessed | %s"%post_id)
      return render_template('404.html'), 404
    else:
      logging.info('Article %s retrieved!'%post['title'])
      return render_template('post.html', post=post)

# Define the About Us page
@app.route('/about')
def about():
    return render_template('about.html')

# Define the post creation functionality 
@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            connection = get_db_connection()
            connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                         (title, content))
            connection.commit()
            connection.close()

            return redirect(url_for('index'))

    return render_template('create.html')

# start the application on port 3111
if __name__ == "__main__":
   app.run(host='0.0.0.0', port='3111')
