import flask
import json
import utils

app = flask.Flask(__name__)

@app.route('/<id>', methods=['GET'])
def meta(id):
    '''
    returns the JSON data associated with this run. eventually this data is created per request
    '''
    try:
        with open('%s.json' % id, 'r') as f:
            d = json.load(f)
            return flask.jsonify(**d)
    except:
        return '', 204

@app.route('/<id>', methods=['POST'])
def create(id):
    requester = '@brianmckenna'
    utils.master(id, requester)
    return '', 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7000, debug=True)
