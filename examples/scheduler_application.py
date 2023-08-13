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
import platform
from multiprocessing import Process, Manager

#tasks = []
FLAG = "START"


def alert(task, tasks):
    def call_multion(task,tasks):
        global FLAG
        llm = OpenAI(temperature=0, openai_api_key="Your_OpenAI_Api_Key")
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
                if tasks:
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
    def __init__(self, root, tasks):
        self.tasks = tasks
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
        # Background and foreground colors
        bg_color = "#f5f5f5" # soft gray
        fg_color = "#333333" # almost black
        primary_color = "#3498db" # blue tone for primary actions
        hover_color = "#2980b9"  # darker blue tone for hover

        # Update styles
        self.style.configure("TLabel", font=self.font_choice, background=bg_color, foreground=fg_color)
        self.style.configure("TEntry", font=self.font_choice, background="#ffffff", foreground=fg_color)
        self.style.configure("TCombobox", font=self.font_choice, background="#ffffff", foreground=fg_color, width=15)
        self.style.configure("TSpinbox", font=self.font_choice, background="#ffffff", foreground=fg_color, width=2)
        self.style.configure("TText", font=self.font_choice, background="#ffffff", foreground=fg_color, wrap="word")

        # Create widgets
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
        self.text_area_task_description = tk.Text(self.root, width=60, height=10, font=self.font_choice, bg="#ffffff", wrap=tk.WORD)
        self.text_area_task_description.pack(pady=10)

        add_task_button = tk.Button(self.root, text="Add Task", command=self.add_task, relief=tk.FLAT, bg=primary_color, fg=fg_color, font=self.font_choice, cursor="hand2")
        add_task_button.pack(pady=10)
        add_task_button.bind("<Enter>", lambda e: add_task_button.config(bg=hover_color))
        add_task_button.bind("<Leave>", lambda e: add_task_button.config(bg=primary_color))


    def on_button_hover(self, event):
        event.widget.config(bg="#d9534f")  # Change color on hover

    def on_button_leave(self, event):
        event.widget.config(bg="#e74c3c")  # Return to original color
    
    def sort_tasks(self, task):
        return task.date_time

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

            # Add task to the Manager list
            self.tasks.append(task)
            
            # Convert Manager list to regular list, sort it, and then update the Manager list
            temp_tasks = list(self.tasks)
            temp_tasks.sort(key=self.sort_tasks)
            self.tasks[:] = temp_tasks  # Update the Manager list with sorted data
            
            alert(task, self.tasks)
            messagebox.showinfo("Success", "Task added successfully.")
        except ValueError:
            messagebox.showerror("Error", "Invalid date format. Please use YYYY-MM-DD HH:MM.")




class TableApp:
    def __init__(self, root, tasks):
        self.root = root
        self.root.title("Scheduled Tasks")
        self.tasks = tasks
        self.create_table()

    def create_table(self):
        if not self.tasks:
            no_tasks_label = ttk.Label(self.root, text="No Tasks Scheduled", font=("Helvetica", 18, "bold"))
            no_tasks_label.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
            return
        if self.tasks:
            self.tree = ttk.Treeview(self.root, columns=("Name", "Date", "Time"))
            self.tree.heading("#0", text="ID")
            self.tree.heading("Name", text="Name")
            self.tree.heading("Date", text="Date")
            self.tree.heading("Time", text="Time")

            self.tree.column("#0", width=50)
            self.tree.column("Name", width=150)
            self.tree.column("Date", width=50)
            self.tree.column("Time", width=150)
            for i in range(len(list(self.tasks))):
                task = list(self.tasks)[i]
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


if platform.system() == "Darwin":
    import rumps

    def start_scheduler_app(tasks):
        root = tk.Tk()
        app = SchedulerApp(root, tasks)  # This is your tkinter-based SchedulerApp
        root.mainloop()

    def start_table_app(tasks):
        root = tk.Tk()
        app = TableApp(root, tasks)
        root.mainloop()

    class RumpsSchedulerApp(rumps.App):
        def __init__(self, tasks):
            super(RumpsSchedulerApp, self).__init__("Scheduler App",
            icon="icon-34.png")
            self.tasks = tasks
            self.menu = [
                rumps.MenuItem("Add Task", callback=self.add_task),
                rumps.MenuItem("Show Tasks", callback=self.show_tasks),
                rumps.MenuItem("Login to MultiOn", callback=self.loginmultion),
                rumps.MenuItem("Exit", callback=rumps.quit_application)
            ]

        def add_task(self, _):
            p = Process(target=start_scheduler_app, args=(self.tasks,))
            p.start()

        def show_tasks(self, _):
            p = Process(target=start_table_app,  args=(self.tasks,))
            p.start()

        def loginmultion(self, _):
            login_multion()

    if __name__ == '__main__':
        manager = Manager()
        tasks = manager.list()
        RumpsSchedulerApp(tasks).run()
else:
    tasks = []
    import pystray
    from PIL import Image
    image = Image.open("icon-34.png")
    def after_click(icon, query):
        global tasks
        global FLAG
        if str(query) == "Add Task":
            root = tk.Tk()
            app = SchedulerApp(root, tasks)
            root.mainloop()
        elif str(query)== "Show Tasks":
            root = tk.Tk()
            app = TableApp(root, tasks)
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



