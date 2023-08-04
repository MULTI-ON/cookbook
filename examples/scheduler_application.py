import tkinter as tk
from tkinter import *
from tkinter import messagebox
from datetime import datetime
from tkcalendar import Calendar
from langchain import OpenAI
from langchain.agents import initialize_agent, AgentType
from langchain.agents.agent_toolkits import MultionToolkit
import multion
from threading import *
import time
import os

tasks = []
FLAG = "START"
def alert(task):
    global FLAG
    global tasks
    def call_multion(task,tasks):
        global FLAG
        llm = OpenAI(temperature=0)
        toolkit = MultionToolkit()
        tools=toolkit.get_tools()
        agent = initialize_agent(
                tools=toolkit.get_tools(),
                llm=llm,
                agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
                verbose = True
            )
        while True and task.FLAG == "START" and FLAG == "START":
            time.sleep(10)
            # Get current time
            current_time = datetime.now()
            
            if current_time >= task.date_time:
                agent.run(task.description)
                tasks.remove(task)
                break
    t1 = Thread(target=call_multion,args=(task,tasks))
    t1.start()


def multion_login():
    t1 = Thread(target=multion.login)
    t1.start()
    # Wait for the thread to finish, but timeout after 30 seconds
    t1.join(timeout=30)
    # Check if the thread is still alive
    if t1.is_alive():
        print("Thread is still running. Closing the thread.")
        t1.cancel()

class Task:
    def __init__(self, name, date_time,description,FLAG):
        self.name = name
        self.date_time = date_time
        self.description = description
        self.FLAG="START"


class SchedulerApp:
    global tasks
    def __init__(self, root):
        self.root = root
        self.root.title("Scheduler App")
        self.hour_string=StringVar()
        self.min_string=StringVar()     
        self.font_choice = ('Times', 20)
        self.cal = None

        self.create_widgets()

    def create_widgets(self):
        self.label_task_name = tk.Label(self.root, text="Task Name:")
        self.label_task_name.grid(row=0, column=0, padx=10, pady=5)

        self.entry_task_name = tk.Entry(self.root, width=30)
        self.entry_task_name.grid(row=0, column=1, padx=10, pady=5)
        self.cal = Calendar(self.root, selectmode="day", year=2023, month=8,day=4)
        self.cal.grid(row=1, column=0, columnspan=3, padx=5, pady=5)
        time_frame = Frame(self.root)
        hour = Spinbox(time_frame,from_=0,to=23,wrap=True,textvariable=self.hour_string,font=self.font_choice,width=2,justify=CENTER)
        minute = Spinbox(time_frame,from_=0,to=59,wrap=True,textvariable=self.min_string,font=self.font_choice,width=2,justify=CENTER)
        hour.pack(side=LEFT, fill=X, expand=True)
        minute.pack(side=LEFT, fill=X, expand=True)
        time_frame.grid(row=1, column=4, columnspan=3, padx=5, pady=5)


        self.label_description = tk.Label(self.root, text="Description")
        self.label_description.grid(row=2, column=0,columnspan=2, padx=10, pady=5)
        self.text_area_task_description = tk.Text(self.root, width=50, height=10)
        self.text_area_task_description.grid(row=3, column=0, columnspan=2, padx=10, pady=5)


        self.btn_add_task = tk.Button(self.root, text="Add Task", command=self.add_task)
        self.btn_add_task.grid(row=4, column=0, columnspan=2, padx=10, pady=5)
		
		


    def add_task(self):
        multion.login()
        name = self.entry_task_name.get()
        description = self.text_area_task_description.get(1.0,"end")
        date_str = self.cal.get_date()
        h = self.hour_string.get()
        m = self.min_string.get()
        print(f"Schedulting task: {name}")
        self.root.destroy()
        try:
            date_format = "%m/%d/%y %H:%M"
            # Convert the string to a datetime object
            date_time = datetime.strptime(f"{date_str}  {h}:{m}", date_format)
            task = Task(name, date_time,description,"START")
            tasks.append(task)
            alert(task)
            tasks.sort(key=lambda x: x.date_time)
            messagebox.showinfo("Success", "Task added successfully.")
        except ValueError:
            messagebox.showerror("Error", "Invalid date format. Please use YYYY-MM-DD HH:MM.")
        

def show_tasks():
    global tasks
    if not tasks:
        messagebox.showinfo("No tasks", "No tasks scheduled.")
    else:
        task_list = "\n".join([f"{task.name} - {task.date_time.strftime('%Y-%m-%d %H:%M')}" for task in tasks])
        messagebox.showinfo("Scheduled tasks", task_list)


import pystray
from PIL import Image

image = Image.open("icon-34.png")

def login_multion():
    file_path = "multion_token.txt"
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
            print(f"File '{file_path}' removed successfully.")
        except OSError as e:
            print(f"Error occurred while removing the file: {e}")
    multion_login()


def after_click(icon, query):
    global tasks
    global FLAG
    if str(query) == "Add Task":
        root = tk.Tk()
        app = SchedulerApp(root)
        root.mainloop()
    elif str(query)== "Show Tasks":
        show_tasks()
    elif str(query)== "Login to MultiOn":
        login_multion()
    elif str(query) == "Exit":
        FLAG = "END"
        icon.stop()


icon = pystray.Icon("MultiOn Scheduler", image, "MultiOnScheduler",
					menu=pystray.Menu(
	pystray.MenuItem("Add Task",
					after_click),
	pystray.MenuItem("Show Tasks",
					after_click),
    pystray.MenuItem("Login to MultiOn",after_click),
	pystray.MenuItem("Exit", after_click)))

icon.run()



