from flask import Flask, render_template, request
from flask_socketio import SocketIO, send, emit, join_room, leave_room
import time
import json
import random

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'

socketio = SocketIO(app)

# Dictionary to store users and their assigned rooms
users = {}


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/test')
def test():
    return render_template('test.html')


@app.route('/test_1')
def test_1():
    return render_template('test_1.html')


# Handle new user joining
# for test
@socketio.on('join')
def handle_join(username):
    users[request.sid] = username  # Store username by session ID
    join_room(username)  # Each user gets their own "room"
    emit("message", f"{username} joined the chat", room=username)


# Handle user messages
# for test
@socketio.on('message')
def handle_message(data):
    username = users.get(request.sid, "Anonymous")  # Get the user's name
    emit("message", f"{username}: {data}", broadcast=True)  # Send to everyone


# Handle disconnects
# for test
@socketio.on('disconnect')
def handle_disconnect():
    username = users.pop(request.sid, "Anonymous")
    emit("message", f"{username} left the chat", broadcast=True)


@socketio.on('oram_join')
def handle_oram_join():
    left_nodes = []
    right_nodes = []
    for i in range(8):
        left_nodes.append({'id': f'L{i}', 'label': f'Node {i}'})
        right_nodes.append({'id': f'R{i}', 'label': f'Node {i}'})
    data = {'left_nodes': left_nodes, 'right_nodes': right_nodes}

    emit("oram_data", data)

    data = {'time':9, 'node':8,'edges': get_all_edges()}

    emit("oram_all_edges", data)


def get_all_edges():
    res = []

    for time in range(10):
        tmp = get_msg(time)
        for i in tmp:
            i['from'] = i['from'].replace('L', f'{time}_')
            i['to'] = i['to'].replace('R', f'{time+1}_')
        res.extend(tmp)
    return res


def get_msg(time):
    res = []
    for num in range(8):
        with open(f'../../multi_node_datas/topic_{num}.txt', 'r') as f:
            for line in f:
                line = line.strip('\n')
                datas = line.split(' ')
                if datas[0] == str(time):
                    res.append({'from':f'L{datas[-1]}','to':f'R{num}','color':'red' if datas[1]=='fake' else 'green'})

    return res


@socketio.on('oram_update_edges')
def handle_oram_update_edges(time):
    print(f"Received time: {time}")
    if time < 0 or time > 9:
        emit("oram_update_edges", {'error': 'Invalid topic number'})
        return

    res = get_msg(time)
    emit('oram_update_edges', res)

left_nodes_list = ['L1', 'L2', 'L3', 'L4', 'L5', 'L6', 'L7', 'L8']
right_nodes_list = ['R1', 'R2', 'R3', 'R4', 'R5', 'R6', 'R7', 'R8']


@socketio.on('oram_add_edge')
def handle_oram_add_edge(color):
    l_node = random.choice(left_nodes_list)
    r_node = random.choice(right_nodes_list)

    emit("oram_add_edge", {'from': l_node, 'to': r_node, 'color': color})


if __name__ == '__main__':
    socketio.run(app, debug=True, allow_unsafe_werkzeug=True)
