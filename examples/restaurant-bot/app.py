from flask import Flask, render_template, request, session, redirect, url_for
from flask_socketio import join_room, leave_room, send, SocketIO

import random
from string import ascii_uppercase
from agents import *
app = Flask(__name__)
app.config["SECRET_KEY"] = "SECRET123"
socketio = SocketIO(app)

messages= []
room="room1"



STATE = 0
llm_chain= None
@app.route("/room")
def room():
    global messages
    return render_template("room.html", messages=messages)

@socketio.on("message")
def message(data):
    global llm_chain
    global room
    global messages
    global STATE
    data = data["data"]
    content = {
        "name": data["name"],
        "message": data["message"]
    }
    content1 =  {}
    if("@Mion Book" in content["message"]):
        STATE=1
    if(STATE==0):
        add_only_input(content["name"]+": "+content["message"])
    elif(STATE==1):
        llm_chain = create_agent()
        content1["message"]=talk_to_human(llm_chain,content["name"]+": "+content["message"])
        STATE=2
    elif(STATE==2):
         content1["message"]=talk_to_human(llm_chain,content["name"]+": "+content["message"])
         if("Confirmed" in content1["message"]):
            use_multion(content1["message"])
            STATE=0
            content1["message"]+="Trigger '@Mion Book' to use agent again. Have a good day!"
    send(content, to=room)
    messages.append(content)
    if("message" in content1.keys()):
        content1["name"]="Mion"
        send(content1, to=room)
        messages.append(content1)
    

@socketio.on("connect")
def connect(auth):
    global room
    join_room(room)

@socketio.on("disconnect")
def disconnect():
    leave_room(room)


if __name__ == "__main__":
    socketio.run(app, debug=True)