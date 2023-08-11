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
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkcalendar import Calendar
from datetime import datetime

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
                print(task.description)
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
        self.root.geometry("600x650")  # Adjust window dimensions
        self.hour_string = tk.StringVar()
        self.min_string = tk.StringVar()
        self.font_choice = ('Helvetica', 12)
        
        #Set time
        self.current_time = datetime.now()
        self.hour_string.set(self.current_time.hour)
        self.min_string.set(self.current_time.minute)

        #Styling
        self.style = ttk.Style()
        self.style.theme_use("clam")  # Change to "default" for native look
        self.style.configure("TLabel", font=self.font_choice, background="#3498db", foreground="white")
        self.style.configure("TEntry", font=self.font_choice, background="#ecf0f1")
        self.style.configure("TCombobox", font=self.font_choice, width=15)
        self.style.configure("TText", font=self.font_choice, background="#ecf0f1", wrap="word")  # Wrap text

        self.create_widgets()
        self.root.focus_set()
        self.root.grab_set()


    def create_widgets(self):
        ttk.Label(self.root, text="Task Name:", style="TLabel").pack(pady=10)
        self.entry_task_name = ttk.Entry(self.root, font=self.font_choice, style="TEntry")
        self.entry_task_name.pack()

        self.cal = Calendar(self.root, selectmode="day", year=self.current_time.year, month=self.current_time.month, day=self.current_time.day, date_pattern="yyyy-mm-dd")
        self.cal.pack(pady=10)

        time_frame = ttk.Frame(self.root)
        ttk.Label(time_frame, text="Time:", style="TLabel").pack(side=tk.LEFT, padx=5)
        ttk.Spinbox(time_frame, from_=0, to=23, wrap=True, textvariable=self.hour_string, font=self.font_choice, width=2, justify=tk.CENTER, style="TSpinbox").pack(side=tk.LEFT, padx=5)
        ttk.Label(time_frame, text=":", style="TLabel").pack(side=tk.LEFT)
        ttk.Spinbox(time_frame, from_=0, to=59, wrap=True, textvariable=self.min_string, font=self.font_choice, width=2, justify=tk.CENTER, style="TSpinbox").pack(side=tk.LEFT, padx=5)
        time_frame.pack(pady=10)

        ttk.Label(self.root, text="Description", style="TLabel").pack(pady=5)
        self.text_area_task_description = tk.Text(self.root, width=60, height=10, font=self.font_choice, bg="#ecf0f1", wrap=tk.WORD)  # Adjust height and wrap
        self.text_area_task_description.pack(pady=10)

        add_task_button = tk.Button(self.root, text="Add Task", command=self.add_task, relief=tk.FLAT, bg="#e74c3c", fg="white", font=self.font_choice, cursor="hand2")
        add_task_button.pack(pady=10)
        add_task_button.bind("<Enter>", self.on_button_hover)
        add_task_button.bind("<Leave>", self.on_button_leave)

    def on_button_hover(self, event):
        event.widget.config(bg="#d9534f")  # Change color on hover

    def on_button_leave(self, event):
        event.widget.config(bg="#e74c3c")  # Return to original color

    def add_task(self):
        multion.login()
        name = self.entry_task_name.get()
        description = self.text_area_task_description.get(1.0, "end")
        date_str = self.cal.get_date()
        h = self.hour_string.get()
        m = self.min_string.get()

        try:
            date_format = "%Y-%m-%d %H:%M"
            date_time = datetime.strptime(f"{date_str} {h}:{m}", date_format)
            task = Task(name, date_time, description, "START")
            tasks.append(task)
            alert(task)
            tasks.sort(key=lambda x: x.date_time)
            messagebox.showinfo("Success", "Task added successfully.")
        except ValueError:
            messagebox.showerror("Error", "Invalid date format. Please use YYYY-MM-DD HH:MM.")




class TableApp:
    global tasks
    def __init__(self, root):
        self.root = root
        self.root.title("Scheduled Tasks")

        self.create_table()

    def create_table(self):
        if tasks:
            self.tree = ttk.Treeview(self.root, columns=("Name", "Date", "Time"))
            self.tree.heading("#0", text="ID")
            self.tree.heading("Name", text="Name")
            self.tree.heading("Date", text="Age")
            self.tree.heading("Time", text="Country")

            self.tree.column("#0", width=50)
            self.tree.column("Name", width=150)
            self.tree.column("Date", width=50)
            self.tree.column("Time", width=150)
            for i, task in enumerate(tasks):
                self.tree.insert("", "end", iid=i, text=i, values=(task.name,task.date_time.strftime('%Y-%m-%d'), task.date_time.strftime('%H:%M')))

            self.tree.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)
        else:
            no_tasks_label = ttk.Label(self.root, text="No Tasks Scheduled", font=("Helvetica", 18, "bold"))
            no_tasks_label.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")


def login_multion():
    file_path = "multion_token.txt"
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
            print(f"File '{file_path}' removed successfully.")
        except OSError as e:
            print(f"Error occurred while removing the file: {e}")
    multion_login()







import platform

if platform.system() == "Darwin":
    import rumps

    class SchedulerApp(rumps.App):
        def __init__(self):
            super(SchedulerApp, self).__init__("Scheduler App")
            self.menu = [
                rumps.MenuItem("Add Task", callback=self.add_task),
                rumps.MenuItem("Show Tasks", callback=self.show_tasks),
                rumps.MenuItem("Login to MultiOn", callback=self.loginmultion),
                rumps.MenuItem("Exit", callback=rumps.quit_application)]

        def add_task(self, _):
            root = tk.Tk()
            app = SchedulerApp(root)
            root.mainloop()
        

        def show_tasks(self, _):
            root = tk.Tk()
            app = TableApp(root)
            root.mainloop()

        
        def loginmultion(self, _):
            login_multion()
    
    SchedulerApp().run()
else:
    import pystray
    from PIL import Image
    image = Image.open("icon-34.png")
    def after_click(icon, query):
        global tasks
        global FLAG
        if str(query) == "Add Task":
            root = tk.Tk()
            app = SchedulerApp(root)
            root.mainloop()
        elif str(query)== "Show Tasks":
            root = tk.Tk()
            app = TableApp(root)
            root.mainloop()
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



