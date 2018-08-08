from flask import Flask, request, make_response, redirect, url_for, abort 
from flask_script import Manager
app = Flask(__name__)
manager = Manager(app)


@app.route('/')
def index():
    res = make_response('<h1>this response carries a cookie!<h1>')
    res.set_cookie('answer', '42')
    user_agent = request.headers.get('User-Agent')
    return redirect(url_for('user',name='a'))


@app.route('/user/<name>')
def user(name):
    abort(404)
    return '<h1>hello world! %s<h1>' % name


if __name__ == '__main__':
    manager.run()