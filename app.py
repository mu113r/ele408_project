from flask import Flask, render_template
from flask_socketio import SocketIO, emit
#from flask_ngrok import run_with_ngrok

app = Flask(__name__)

app.config['SECRET_KEY'] = 'mysecretkey'
socketio = SocketIO(app)

@app.route('/')
def index():
    return render_template(r'templates/index.html')

@socketio.on('my event')
def handle_my_custom_event(myjson):
    print('recived something: ' + str(myjson))
    socketio.emit('my response', myjson)

if __name__ == '__main__':
    socketio.run(app, debug=True)
