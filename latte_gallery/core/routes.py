from flask import Blueprint, render_template, jsonify

core = Blueprint('core', __name__)

@core.route('/')
@core.route('/home')
def home():
    return render_template('home.html')

@core.route('/about')
def about():
    return jsonify({'message':'ok'})