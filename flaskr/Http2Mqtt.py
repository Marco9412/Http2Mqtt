from flask import Flask, request, Response
from functools import wraps
import ssl
from flaskr import mqttlib
import json.decoder
import fileinput

app = Flask(__name__)

global conn
VALID_USERS = dict()
VALID_TOPICS = set()
MASTER_TOPICS = dict()

SUBSCRIBED_TOPICS = dict()


def mqtt_message_callback(msg_topic, msg_payload):
    if msg_topic in SUBSCRIBED_TOPICS:
        SUBSCRIBED_TOPICS[msg_topic] = msg_payload


# ----------------------------------------------------------------------------------------------------------------------
def check_auth(username, password):
    """This function is called to check if a username /
    password combination is valid.
    """
    return username in VALID_USERS and password == VALID_USERS[username]


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if request.method == 'POST':
            if check_auth(request.form['username'], request.form['password']):
                return f(*args, **kwargs)
        elif request.method == 'GET':
            if check_auth(request.args.get('username', ''), request.args.get('password', '')):
                return f(*args, **kwargs)
        return Response(
            'Could not verify your access level for that URL.\n'
            'You have to login with proper credentials', 401)

    return decorated


# ----------------------------------------------------------------------------------------------------------------------

@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/get/<path:topic>')
@requires_auth
def read_topic(topic):
    if topic not in SUBSCRIBED_TOPICS:
        app.logger.warn('Tried to read a non-subscribed topic %s' % topic)
        return "Err"

    return SUBSCRIBED_TOPICS.get(topic).decode('utf-8') if SUBSCRIBED_TOPICS.get(topic) else "Err"


@app.route('/<path:topic>')
@requires_auth
def publish(topic):
    if topic not in VALID_TOPICS:
        app.logger.warn('Cannot publish on invalid topic %s' % topic)
        return "Err"

    payload = None
    if request.method == 'GET' and 'payload' in request.args:
        payload = request.args['payload']
    elif request.method == 'POST' and 'payload' in request.form:
        payload = request.form['payload']

    if topic in MASTER_TOPICS:
        for sub_topic in MASTER_TOPICS[topic]:
            conn.publish(sub_topic, payload)
        return "Ok"
    else:
        return "Ok" if conn.publish(topic, payload) else "Err"


def run_app():
    # parse input
    data = str()
    for line in fileinput.input():
        data = data + line

    settings = None

    try:
        settings = json.loads(data)

        # users
        for user in settings["http"]["valid_users"]:
            VALID_USERS[user] = settings["http"]["valid_users"][user]

        # topics
        for topic in settings["mqtt"]["valid_topics"]:
            VALID_TOPICS.add(topic)
        for master_topic in settings["mqtt"]["master_topics"]:
            MASTER_TOPICS[master_topic] = settings["mqtt"]["master_topics"][master_topic]
            VALID_TOPICS.add(master_topic)
        for subscribed_topic in settings["mqtt"]["subscribed_topics"]:
            SUBSCRIBED_TOPICS[subscribed_topic] = b''
    except json.decoder.JSONDecodeError as e:
        print('Invalid json file! Please check your settings!')
        print(e)
        exit(1)

    context = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
    context.load_cert_chain(settings["http"]["certfilepath"], settings["http"]["keyfilepath"])

    conn = mqttlib.MqttConnection(settings["mqtt"], mqtt_message_callback)

    conn.connect()
    app.run(ssl_context=context, port=settings["http"]["port"], host='0.0.0.0')
    conn.disconnect()


if __name__ == '__main__':
    run_app()