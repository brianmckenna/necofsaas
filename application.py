import datetime
import flask
import flask.ext.login
import glob
import json
#import necofs.utils
import traceback

app = flask.Flask(__name__)
app.secret_key = 'fb32e85e-f645-430e-bc15-8d1dedec5cb9'

# Flask-Login
login_manager = flask.ext.login.LoginManager()
login_manager.init_app(app)


# get the offerings/configurations
def _offerings():
    offerings = []
    jsons = glob.glob('*.json')
    for j in jsons:
        print j
        with open(j, 'r') as fp:
            offering = json.load(fp)
            offerings.append(offering)
    return offerings



# REST
@app.route('/offering/<id>', methods=['GET'])
def offering(id):
    try:
        with open('%s.json' % id, 'r') as f:
            d = json.load(f)
            return flask.jsonify(**d)
    except:
        return '', 204

@app.route('/documentation')
def documentation():
    return 'documentation', 200

@app.route('/logout')
def logout():
    return 'logout', 200

@app.route('/execute')
def execute():
    requester = '@brianmckenna' # TODO: use Flask-Login for this
    necofs.utils.create_master(id, requester) # TODO: async
    return 'executing ' + id, 200

@app.route('/logs')
def logs():
    return 'logs', 200




# UI
@app.route('/')
def index():
    offerings = _offerings()
    dates = [datetime.datetime(2006, 11, 21, 16, 30), datetime.datetime(2009, 7, 21, 16, 30)] #TODO
    return flask.render_template('index.html', offerings=offerings, dates=dates)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7000, debug=True)
