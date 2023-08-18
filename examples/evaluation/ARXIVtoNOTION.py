import os
import openai
import multion
from langchain.agents.agent_toolkits import MultionToolkit
from langchain.document_loaders import ArxivLoader
from langchain import OpenAI
from langchain.agents import initialize_agent, AgentType
import tkinter as tk
from tkinter import simpledialog, messagebox, Entry, Label, Button, Text, PhotoImage

# Initialize OpenAI
openai.api_key = os.environ.get('OPENAI_API_KEY')

# Initialize Multion
multion.login()
llm = OpenAI(temperature=0)
toolkit = MultionToolkit()
agent = initialize_agent(
    tools=toolkit.get_tools(),
    llm=llm,
    agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)

def get_summary_from_arxiv(doc_name):
    # Load document from arXiv
    docs = ArxivLoader(query=doc_name, load_max_docs=1).load()
    doc_content = docs[0].page_content
    
    # Get summary from OpenAI
    response = openai.Completion.create(
        engine="davinci",
        prompt=f"Provide a concise summary for the following content:\n\n{doc_content[:1000]}\n",
        max_tokens=100
    )
    
    summary = response.choices[0].text.strip()
    return summary

def display_summary():
    doc_name = doc_name_entry.get()
    summary = get_summary_from_arxiv(doc_name)
    summary_text.delete(1.0, tk.END)
    summary_text.insert(tk.END, summary)

def save_to_notion():
    summary = summary_text.get(1.0, tk.END).strip()
    # Run the Multion agent to simulate saving to Notion
    agent.run(
        f"Navigate to Notion. Start a new page. Type out the following summary in its entirety: '{summary}'. Ensure the entire summary is typed before saving. Once typed, click on 'Save' or equivalent to store the summary."
    )
    messagebox.showinfo("Info", "Summary saved to Notion!")

# GUI Setup
root = tk.Tk()
root.title("ArXiv Summary to Notion")
root.geometry("600x400")

# Set a background color
root.configure(bg="#f5f5f5")

# arXiv logo

logo_label = Label(root, bg="#f5f5f5")
logo_label.pack(pady=10)

Label(root, text="Enter Document Name:", bg="#f5f5f5").pack(pady=10)
doc_name_entry = Entry(root, width=50)
doc_name_entry.pack(pady=10)

btn_display_summary = Button(root, text="Display ArXiv Summary", command=display_summary)
btn_display_summary.pack(pady=10)

summary_text = Text(root, width=70, height=10, wrap=tk.WORD)
summary_text.pack(pady=10)

btn_save_to_notion = Button(root, text="Save to Notion with Multion", command=save_to_notion)
btn_save_to_notion.pack(pady=10)

root.mainloop()
