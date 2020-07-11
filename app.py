##################################################
## Author: {Sayantan Biswas}
## Maintainer: {Sayantan Biswas}
## Email: {sayantanbiswas1002@gmail.com}
##################################################


#!/usr/bin/python3.8
import json, tempfile
import os
from functools import wraps
import ast
import pandas as pd
from flask import Flask, jsonify, render_template, request, session, url_for, redirect
from flask_simplelogin import SimpleLogin, login_required
from werkzeug.security import check_password_hash, generate_password_hash
from flask_assets import Environment, Bundle
import util
# import assets
import sql, sql_ex
import click
import numpy as np
import pandas as pd
from werkzeug.exceptions import HTTPException


# [ -- Utils -- ]

def validate_login(user):
    db_users = json.load(open('users.json'))
    if not db_users.get(user['username']):
        return False
    stored_password = db_users[user['username']]['password']
    if check_password_hash(stored_password, user['password']):
        return True
    return False

def create_user(**data):
    """Creates user with encrypted password"""
    if 'username' not in data or 'password' not in data:
        raise ValueError('username and password are required.')

    """Hash the user password"""
    data['password'] = generate_password_hash(
        data.pop('password'),
        method='pbkdf2:sha256'
    )
    db_users = json.load(open('users.json'))
    db_users[data['username']] = data
    json.dump(db_users, open('users.json', 'w'))
    return data



# [--- Flask Factories  ---]

def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "361ea895-4bae-43a8-b0a5-c8c35bf6a920"

    return app

def load_users(username):
    if username.is_authenticated():
        user = username.get_id() # return username in get_id()
    else:
        user = None
    return username

def configure_extensions(app):
    SimpleLogin(app, login_checker=validate_login)
    if not os.path.exists('users.json'):
        with open('users.json', 'a') as json_file:
            json.dump({'username': '', 'password': ''}, json_file)

# @app.route('/')
# def index():
#     return redirect(url_for('home'))

def configure_views(app):

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        error = None
        if request.method == 'POST':
            if request.form['username'] != 'admin' or request.form['password'] != 'admin':
                error = 'Invalid Credentials. Please try again.'
            else:
                return redirect(url_for('home'))
        return render_template('login.html', message=error)

    @app.route('/')
    def index():
        return redirect(url_for('home'))

    @app.route('/home/')
    def home():
        return render_template('home.html')

    @app.route('/addevent', methods=['GET', 'POST'])
    @login_required()
    def addevent():
        email = []
        if request.method == 'POST':
            render_template('addevent.html')
            summary = request.form['summary']
            date = request.form['date']
            start_time = request.form['start']
            end_time = request.form['end']
            #num = request.form['num']
            email.append(request.form['invite1'])
            email.append(request.form['invite2'])
            email.append(request.form['invite3'])
            email.append(request.form['invite4'])
            email.append(request.form['invite5'])
            email.append(request.form['invite6'])
            description = request.form['description']
            location = request.form['location']
            email_list=[]
            for i in email:
                if(i != ""):
                    email_list.append({'email':i})
            email_db=[]
            for i in email:
                if(i != ""):
                    email_db.append((i))
            response = (util.addevent(summary,date,start_time,end_time,email_list,description,location))
            sql.maintain(summary,date,start_time,end_time,email_db,description,location,response)
            return render_template('addevent.html', result_text=response)
        if request.method == 'GET':
            return render_template('addevent.html')

    @app.route('/api', methods=['POST'])
    @login_required(basic=True)
    def api():
        return jsonify(data='You are logged in with basic auth')

    # @login_required(basic=True)
    # @app.route('/history')
    # @login_required(username)

    @login_required(basic=True)
    @app.route('/history')
    @login_required(username=['admin'])
    def history():
        # user = load_users(username)
        # if user == 'admin':
            if os.path.exists('records.sqlite'):
                df = sql_ex.extract()
                return render_template('history.html', tables=[df.to_html(border="0",justify="match-parent")], titles=[df.columns.values])
            else:
                return render_template('error_admin.html')
        # else: 
            # return render_template('error_admin.html')
        

# [--- Error Protocols ---]

    @app.errorhandler(404)
    def pagenot_found(e):
        """Bad request."""
        return render_template("error.html", message=e)

    @app.errorhandler(400)
    def bad_request(e):
        """Internal server error."""
        return render_template("error.html", message=e)

    @app.errorhandler(500)
    def server_error(e):
        """Internal server error."""
        return render_template("error.html", message=e)


# [--- Command line functions ---]

def with_app(f):
    """Calls function passing app as first argument"""
    @wraps(f)
    def decorator(*args, **kwargs):
        app = create_app()
        configure_extensions(app)
        configure_views(app)
        return f(app=app, *args, **kwargs)
    return decorator


@click.group()
def main():
    """Flask Calendar Task Scheduling App"""
    # home()

@main.command()
@click.option('--username', required=True, prompt=True)
@click.option('--password', required=True, prompt=True, hide_input=True, confirmation_prompt=True)
@with_app
def adduser(app, username, password):
    """Add new user with admin access"""
    with app.app_context():
        create_user(username=username, password=password)
        click.echo('user created!')

@main.command()
@click.option('--reloader/--no-reloader', default=None)
@click.option('--debug/--no-debug', default=True)
@click.option('--host', default=None)
@click.option('--port', default=None)
@with_app
def main(app=None, reloader=None, debug=None, host=None, port=None):
    """Run the Flask development server i.e. app.run()"""
    debug = debug or app.config.get('DEBUG', True)
    reloader = reloader or app.config.get('RELOADER', True)
    host = host or app.config.get('HOST', '127.0.0.1')
    port = port or app.config.get('PORT', 5000)
    app.run(
        use_reloader=reloader,
        debug=debug,
        host=host,
        port=port
    )


# [--- Entry point ---]

if __name__ == "__main__":
    main()
    # app.run(use_reloader=True,debug=True,host='127.0.0.1',port=5000,)
