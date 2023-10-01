import tkinter as tk
from tkinter import *
from tkinter import messagebox, IntVar, StringVar
from datetime import datetime, timedelta
from tkcalendar import Calendar
from langchain import OpenAI
from langchain.agents import initialize_agent, AgentType
from langchain.agents.agent_toolkits.multion.toolkit import MultionToolkit
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
import sv_ttk
import tkinter as tk
from tkinter import simpledialog

# tasks = []
FLAG = "START"
import os

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", None)


def alert(task, tasks):
    global OPENAI_API_KEY

    def call_multion(task, tasks):
        global FLAG
        if OPENAI_API_KEY == None:
            llm = OpenAI(
                temperature=0,
            )
        else:
            llm = OpenAI(
                temperature=0,
                openai_api_key=OPENAI_API_KEY,
            )
        toolkit = MultionToolkit()
        agent = initialize_agent(
            tools=toolkit.get_tools(),
            llm=llm,
            agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
            verbose=True,
        )
        while True and task.FLAG == "START" and FLAG == "START" and task.is_active:
            time.sleep(10)
            # Get current time
            current_time = datetime.now()

            if current_time >= task.date_time:
                print(task.description)
                agent.run(task.description)

                if task.repeat_type == "Daily":
                    task.date_time += timedelta(days=1)
                elif task.repeat_type == "Weekly":
                    task.date_time += timedelta(weeks=1)
                elif task.repeat_type == "Monthly":
                    task.date_time += timedelta(days=30)
                elif task.repeat_type == "Every 30 Seconds":
                    task.date_time += timedelta(seconds=30)
                elif task.repeat_type == "Every 1 Minute":
                    task.date_time += timedelta(minutes=1)
                elif task.repeat_type == "Hourly":
                    task.date_time += timedelta(hours=1)
                elif task.repeat_type == "Custom" and task.custom_repeat_interval:
                    task.date_time += timedelta(days=task.custom_repeat_interval)
                else:
                    task.is_active = False  # Stop repeating if 'None' is selected

                try:
                    if tasks:
                        tasks.remove(task)
                except ValueError:
                    pass  # Task was already removed
                # break

    t1 = Thread(target=call_multion, args=(task, tasks))
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
    def __init__(
        self, name, date_time, description, FLAG, repeat_type, custom_repeat_interval
    ):
        self.name = name
        self.date_time = date_time
        self.description = description
        self.FLAG = "START"
        self.repeat_type = repeat_type
        self.custom_repeat_interval = custom_repeat_interval  # in days
        self.is_active = True  # a flag to check if task is currently active or not

    def stop(self):
        self.is_active = False


class SchedulerApp:
    def __init__(self, root, tasks):
        self.tasks = tasks
        self.root = root
        self.root.title("Scheduler App")
        self.root.geometry("600x750")  # Adjust window dimensions
        self.hour_string = tk.StringVar()
        self.min_string = tk.StringVar()
        self.font_choice = ("Helvetica", 14)
        self.repeat_var = StringVar()  # Variable for Repeat dropdown
        self.repeat_var.set("None")  # Default value
        self.custom_repeat_interval = IntVar()  # Variable for Custom Repeat entry

        # Set time
        self.current_time = datetime.now()
        self.hour_string.set(self.current_time.hour)
        self.min_string.set(self.current_time.minute)

        # This is where the magic happens
        sv_ttk.set_theme("light")

        # Styling
        self.style = ttk.Style()
        # self.style.theme_use("clam")  # Change to "default" for native look
        self.style.configure(
            "TLabel", font=self.font_choice, background="#3498db", foreground="white"
        )
        self.style.configure("TEntry", font=self.font_choice, background="#ecf0f1")
        self.style.configure("TCombobox", font=self.font_choice, width=15)
        self.style.configure(
            "TText", font=self.font_choice, background="#ecf0f1", wrap="word"
        )  # Wrap text

        self.create_widgets()
        self.root.focus_set()
        self.root.grab_set()

    def create_widgets(self):
        # Background and foreground colors
        # Background and foreground colors
        bg_color = "#ffffff"  # Apple-style white background
        fg_color = "#333333"  # Dark text for better readability
        primary_color = "#007AFF"  # Apple-style blue for buttons and active elements
        hover_color = "#0051c7"  # Slightly darker blue tone for hover

        # Update styles
        self.style.configure(
            "TLabel", font=self.font_choice, background=bg_color, foreground=fg_color
        )
        self.style.configure(
            "TEntry", font=self.font_choice, background="#ffffff", foreground=fg_color
        )
        self.style.configure(
            "TCombobox",
            font=self.font_choice,
            background="#ffffff",
            foreground=fg_color,
            width=15,
        )
        self.style.configure(
            "TSpinbox",
            font=self.font_choice,
            background="#ffffff",
            foreground=fg_color,
            width=2,
        )
        self.style.configure(
            "TText",
            font=self.font_choice,
            background="#ffffff",
            foreground=fg_color,
            wrap="word",
        )

        # Create widgets
        ttk.Label(self.root, text="Task Name:", style="TLabel").pack(
            pady=(20, 5), padx=20
        )
        self.entry_task_name = ttk.Entry(
            self.root, font=self.font_choice, style="TEntry"
        )
        self.entry_task_name.pack(pady=(0, 20), padx=20)

        self.cal = Calendar(
            self.root,
            selectmode="day",
            year=self.current_time.year,
            month=self.current_time.month,
            day=self.current_time.day,
            date_pattern="yyyy-mm-dd",
            background="white",  # Background color
            foreground="black",  # Text color
            headersbackground=primary_color,  # Apple-like blue for headers
            headersforeground="white",  # Text color for headers
            weekendbackground="white",  # Background for weekends
            # weekendforeground="red",  # Text color for weekends
            normalbackground="white",  # Normal day background
            normalforeground="black",  # Normal day text color
            selectbackground="#007AFF",  # Selected day background color
            selectforeground="white",  # Selected day text color
            othermonthbackground="white",  # Other month day background color
            othermonthforeground="light gray",  # Other month day text color
            font=("Helvetica", 14),  # Set the larger font
        )
        for i in range(6):
            self.cal._week_nbs[i].destroy()

        self.cal.pack(pady=10)

        time_frame = ttk.Frame(self.root)
        ttk.Label(time_frame, text="Time:", style="TLabel").pack(side=tk.LEFT, padx=5)
        ttk.Spinbox(
            time_frame,
            from_=0,
            to=23,
            wrap=True,
            textvariable=self.hour_string,
            font=self.font_choice,
            width=2,
            justify=tk.CENTER,
            style="TSpinbox",
        ).pack(side=tk.LEFT, padx=5)
        ttk.Label(time_frame, text=":", style="TLabel").pack(side=tk.LEFT)
        ttk.Spinbox(
            time_frame,
            from_=0,
            to=59,
            wrap=True,
            textvariable=self.min_string,
            font=self.font_choice,
            width=2,
            justify=tk.CENTER,
            style="TSpinbox",
        ).pack(side=tk.LEFT, padx=5)
        time_frame.pack(pady=10)

        # Repeat Dropdown Menu
        repeat_label = ttk.Label(self.root, text="Repeat:", style="TLabel")
        repeat_label.pack(pady=5)
        repeat_options = [
            "None",
            "Every 30 Seconds",
            "Every 1 Minute",
            "Hourly",
            "Daily",
            "Weekly",
            "Monthly",
            "Custom",
        ]
        repeat_menu = ttk.OptionMenu(self.root, self.repeat_var, *repeat_options)
        repeat_menu.pack(pady=5)

        # Custom Repeat Entry (hidden by default)
        self.custom_repeat_frame = ttk.Frame(self.root)
        custom_repeat_label = ttk.Label(
            self.custom_repeat_frame, text="Custom Repeat (Days):", style="TLabel"
        )
        custom_repeat_entry = ttk.Entry(
            self.custom_repeat_frame,
            textvariable=self.custom_repeat_interval,
            style="TEntry",
        )
        custom_repeat_label.pack(side=tk.LEFT, padx=5)
        custom_repeat_entry.pack(side=tk.LEFT, padx=5)

        # Check for changes in the "Repeat" dropdown menu
        self.repeat_var.trace("w", self.update_custom_repeat_visibility)

        ttk.Label(self.root, text="Description", style="TLabel").pack(pady=5)
        self.text_area_task_description = tk.Text(
            self.root,
            width=60,
            height=10,
            font=self.font_choice,
            bg="#ffffff",
            highlightthickness=1,
            highlightbackground="#D3D3D3",  # Default light gray color
            highlightcolor=primary_color,  # Blue color when the widget is active or focused
            wrap=tk.WORD,
        )
        self.text_area_task_description.pack(pady=10)

        add_task_button = tk.Button(
            self.root,
            text="Add Task",
            command=self.add_task,
            relief=tk.FLAT,
            bg=primary_color,
            fg=fg_color,
            font=self.font_choice,
            cursor="hand2",
        )
        add_task_button.pack(pady=(10, 20), padx=20)
        add_task_button.bind(
            "<Enter>", lambda e: add_task_button.config(bg=hover_color)
        )
        add_task_button.bind(
            "<Leave>", lambda e: add_task_button.config(bg=primary_color)
        )

    def on_button_hover(self, event):
        event.widget.config(bg="#d9534f")  # Change color on hover

    def on_button_leave(self, event):
        event.widget.config(bg="#e74c3c")  # Return to original color

    def sort_tasks(self, task):
        return task.date_time

    def update_custom_repeat_visibility(self, *args):
        """Show or hide the Custom Repeat entry based on the Repeat dropdown selection."""
        if self.repeat_var.get() == "Custom":
            self.custom_repeat_frame.pack(pady=5)
        else:
            self.custom_repeat_frame.pack_forget()

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
            repeat_type = self.repeat_var.get()
            custom_repeat_interval = (
                self.custom_repeat_interval.get()
                if self.repeat_var.get() == "Custom"
                else None
            )
            task = Task(
                name,
                date_time,
                description,
                "START",
                repeat_type,
                custom_repeat_interval,
            )

            # Add task to the Manager list
            self.tasks.append(task)

            # Convert Manager list to regular list, sort it, and then update the Manager list
            temp_tasks = list(self.tasks)
            temp_tasks.sort(key=self.sort_tasks)
            self.tasks[:] = temp_tasks  # Update the Manager list with sorted data

            alert(task, self.tasks)
            messagebox.showinfo("Success", "Task added successfully.")
        except ValueError:
            messagebox.showerror(
                "Error", "Invalid date format. Please use YYYY-MM-DD HH:MM."
            )


class TableApp:
    def __init__(self, root, tasks, refresh_rate=1000):  # Added refresh_rate
        self.root = root
        self.root.title("Scheduled Tasks")
        self.root.geometry("700x150")  # Adjust window dimensions

        self.tasks = tasks
        self.last_task_count = len(self.tasks)
        self.refresh_rate = refresh_rate
        self.create_table()
        self.refresh_table()

    def create_table(self):
        # Clear existing widgets first
        for widget in self.root.winfo_children():
            widget.destroy()

        if not self.tasks:
            no_tasks_label = ttk.Label(
                self.root, text="No Tasks Scheduled", font=("Helvetica", 18, "bold")
            )
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
                self.tree.insert(
                    "",
                    "end",
                    iid=i,
                    text=i,
                    values=(
                        task.name,
                        task.date_time.strftime("%Y-%m-%d"),
                        task.date_time.strftime("%H:%M"),
                    ),
                )

            self.tree.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)
        else:
            no_tasks_label = ttk.Label(
                self.root, text="No Tasks Scheduled", font=("Helvetica", 18, "bold")
            )
            no_tasks_label.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

    def refresh_table(self):
        if len(self.tasks) != self.last_task_count:
            self.last_task_count = len(self.tasks)
            self.create_table()
        self.root.after(self.refresh_rate, self.refresh_table)


def login_multion():
    file_path = "multion_token.txt"
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
            print(f"File '{file_path}' removed successfully.")
        except OSError as e:
            print(f"Error occurred while removing the file: {e}")
    multion_login()


class APIKeyInputDialog:
    def __init__(self, parent):
        self.parent = parent
        self.parent.title("OpenAI API Key")

        self.api_key = None
        self.style = ttk.Style()
        self.create_widgets()

    def create_widgets(self):
        # Background and foreground colors
        bg_color = "#ffffff"  # Apple-style white background
        fg_color = "#333333"  # Dark text for better readability
        primary_color = "#007AFF"  # Apple-style blue for buttons and active elements
        hover_color = "#0051c7"  # Slightly darker blue tone for hover
        font_choice = ("Helvetica", 14)  # Font choice

        # Update styles
        self.style.configure(
            "TLabel", font=font_choice, background=bg_color, foreground=fg_color
        )
        self.style.configure(
            "TEntry", font=font_choice, background="#ffffff", foreground=fg_color
        )

        self.label = tk.Label(self.parent, text="Enter your OpenAI API Key:")
        self.label.pack(pady=10)

        self.api_key_entry = tk.Entry(self.parent, font=font_choice, show="*")
        self.api_key_entry.pack(pady=5)
        self.api_key_entry.bind("<Return>", lambda event: self.get_api_key())

        self.ok_button = tk.Button(
            self.parent,
            text="OK",
            command=self.get_api_key,
            relief=tk.FLAT,
            bg=primary_color,
            fg=fg_color,
            font=font_choice,
            cursor="hand2",
        )
        self.ok_button.pack(pady=10)
        self.ok_button.bind("<Enter>", lambda e: self.ok_button.config(bg=hover_color))
        self.ok_button.bind(
            "<Leave>", lambda e: self.ok_button.config(bg=primary_color)
        )

    def get_api_key(self):
        api_key = self.api_key_entry.get()
        print("Submitted API key: ", api_key)

        if api_key:
            self.api_key = api_key
            self.parent.quit()  # Close the input widget
        else:
            messagebox.showerror("Error", "API key cannot be empty")


def get_openai_api_key():
    global OPENAI_API_KEY

    api_key = OPENAI_API_KEY
    if not api_key:
        print("Getting OpenAI API Key...")
        root = tk.Tk()
        dialog = APIKeyInputDialog(root)
        root.mainloop()
        api_key = dialog.api_key
        root.destroy()

    OPENAI_API_KEY = api_key
    return api_key


### Program Start
OPENAI_API_KEY = get_openai_api_key()
if OPENAI_API_KEY is not None:
    os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
    print("Set OPENAI_API_KEY: ", OPENAI_API_KEY)
else:
    print("OPENAI_API_KEY is not set.")

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
            super(RumpsSchedulerApp, self).__init__("Scheduler App", icon="icon-34.png")
            self.tasks = tasks
            self.menu = [
                rumps.MenuItem("Add Task", callback=self.add_task),
                rumps.MenuItem("Show Tasks", callback=self.show_tasks),
                rumps.MenuItem("Login to MultiOn", callback=self.loginmultion),
                # rumps.MenuItem("Exit", callback=rumps.quit_application),
            ]

        def add_task(self, _):
            p = Process(target=start_scheduler_app, args=(self.tasks,))
            p.start()

        def show_tasks(self, _):
            p = Process(target=start_table_app, args=(self.tasks,))
            p.start()

        def loginmultion(self, _):
            login_multion()

    if __name__ == "__main__":
        print("Starting RumpsSchedulerApp...")
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
        elif str(query) == "Show Tasks":
            root = tk.Tk()
            app = TableApp(root, tasks)
            root.mainloop()
        elif str(query) == "Login to MultiOn":
            login_multion()
        elif str(query) == "Exit":
            FLAG = "END"
            icon.stop()

    icon = pystray.Icon(
        "MultiOn Scheduler",
        image,
        "MultiOnScheduler",
        menu=pystray.Menu(
            pystray.MenuItem("Add Task", after_click),
            pystray.MenuItem("Show Tasks", after_click),
            pystray.MenuItem("Login to MultiOn", after_click),
            pystray.MenuItem("Exit", after_click),
        ),
    )

    ### Program Start
    OPENAI_API_KEY = get_openai_api_key()

    icon.run()
