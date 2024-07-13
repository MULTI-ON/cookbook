from graphviz import Digraph
from type import TaskList


def visualize_task_list(tasks: TaskList):
    dot = Digraph(comment="Task List")

    # Add nodes
    for task in tasks:
        label = f"Name: {task.name}\nDescription: {task.description}\nCmd: {task.cmd}\nURL: {task.url}"
        dot.node(str(task.id), label, color="blue")

    # Render the graph
    dot.render("task_list.gv", view=True)
