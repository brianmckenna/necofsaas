import datetime
import flask
import flask.ext.login
import glob
import json
#import necofs.utils
import traceback
import urllib2
import xml.etree.ElementTree

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

def _get_dates():
    dates = []
    tree = xml.etree.ElementTree.ElementTree(file=urllib2.urlopen('http://54.86.86.177/thredds/catalog/necofs/restart/gom/catalog.xml'))
    root = tree.getroot()
    for d in root.iter('{http://www.unidata.ucar.edu/namespaces/thredds/InvCatalog/v1.0}dataset'):
        if 'urlPath' in d.attrib:
            dates.append(datetime.datetime.strptime(d.attrib['name'],'%Y%m%d%H.nc'))
    return dates

# UI
@app.route('/')
def index():
    offerings = _offerings()
    dates = _get_dates()
    return flask.render_template('index.html', offerings=offerings, dates=dates)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7000, debug=True)
