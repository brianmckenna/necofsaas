import flask
import json

app = flask.Flask(__name__)

@app.route('/<id>')
def dataset(id):
    '''
    returns the JSON data associated with this run. eventually this data is created per request
    '''
    try:
        with open('%s.json' % id, 'r') as f:
            d = json.load(f)
            return flask.jsonify(**d)
    except:
        return '', 204

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7000, debug=True)
