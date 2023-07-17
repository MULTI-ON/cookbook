import shutil
import os

def copy_files(source_file, destination_file):
    shutil.copy2(source_file, destination_file)


print(os.getcwd())
src_dir = "..\\venv\\Lib\\site-packages\\langchain"
dest_dir = ""

files = ["agents\\agent_toolkits\\multion\\base.py","agents\\agent_toolkits\\multion\\__init__.py","tools\\multion\\__init__.py","tools\\multion\\tool.py","utilities\\multion.py"]

for f in files:
    print(os.path.join(os.getcwd(),f))
    copy_files(os.path.join(src_dir,f),os.path.join(os.getcwd(),f))