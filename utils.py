import winreg, os, subprocess, codecs, json, glob, re
from datetime import datetime
from typing import Callable

def replace_start(text: str, find:str, replace:str):
  pattern = rf"(?m)^{re.escape(find)}\b"
  return re.sub(pattern, replace, text)

def program_recognized(name:str) -> bool:
  try:
    subprocess.run([name, '--version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    return True
  except Exception:
    return False

def clone_repo(url:str, path:str) -> bool:
  result = subprocess.run(["git", "clone", url, path], capture_output=True, text=True)
  if result.returncode == 0: return True
  else: return False

def files_list(path:str="./", ext:str="") -> dict[str:list[str]]:
  folder_files = {}
  for folder, subfolders, files in os.walk(path):
    file_list = []
    for file in files:
      if not ext or file.endswith(f".{ext.lstrip(".")}"):
        full_path = os.path.join(folder, file)
        file_list.append(full_path)
    if file_list:
      folder_files[folder] = file_list
      # subfolders - not used
  return folder_files

def files_mdate(path:str="./"):
  file_date = {}
  # Traverse through all files and directories within the provided directory
  for folder, subfolders, files in os.walk(path):
    for file in files:
      file_path = os.path.join(folder, file)
      file_date[file_path] = datetime.fromtimestamp(os.path.getmtime(file_path))
  return file_date

def get_date() -> str:
  return datetime.now().strftime("%Y-%m-%d")

def files_mdate_max(path:str="./") -> tuple|None:
  file_date = files_mdate(path)
  if not file_date: return None
  max_date = max(file_date.values())
  file = [klucz for klucz, data in file_date.items() if data == max_date][0]
  return file, max_date

def len_last_line(string:str) -> int:
  return len(string.split('\n')[-1].strip())

def make_folder(path:str):
  if not os.path.exists(path):
    os.makedirs(path)

def folder_exists(path:str):
  if os.path.exists(path) and os.path.isdir(path): return True
  else: return False

def folder_remove(path:str):
  for root, dirs, files in os.walk(path, topdown=False):
    for file in files:
      os.remove(os.path.join(root, file))
    for dir in dirs:
      os.rmdir(os.path.join(root, dir))
  os.rmdir(path)

def save_json_prettie(name:str, content:dict):
  name = name.removesuffix('.json') + '.json'
  openFile = codecs.open(name, "w+", "utf-8")
  openFile.write(json.dumps(content, indent=2))
  openFile.close()

def load_json(name:str):
  if not os.path.exists(name):
    return None
  try:
    with open(name, 'r') as file:
      data = json.load(file)
      return data if data else {}
  except json.JSONDecodeError:
    return None

class Env:
    
  @staticmethod
  def path_exist(path) -> bool:
    env_path = os.environ.get("PATH", "")
    if path in env_path: return True
    else: return False

  @staticmethod
  def var_exist(var) -> bool:
    if var in os.environ: return True
    else: return False

  @staticmethod
  def add_path(path) -> bool:
    try:
      key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Environment", 0, winreg.KEY_SET_VALUE | winreg.KEY_READ)
      current_path, _ = winreg.QueryValueEx(key, "Path")
      winreg.SetValueEx(key, "Path", 0, winreg.REG_EXPAND_SZ, f"{current_path};{path}")
      winreg.CloseKey(key)
      return True
    except Exception as e:
      return False

  @staticmethod
  def add_variable(name, value) -> bool:
    try:
      key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Environment", 0, winreg.KEY_SET_VALUE | winreg.KEY_READ)
      winreg.SetValueEx(key, name, 0, winreg.REG_EXPAND_SZ, value)
      winreg.CloseKey(key)
      return True
    except Exception as e:
      return False
    
def read_makefile_lines(file_path):
  lines = []
  with open(file_path, "r") as file:
    current_line = ""
    for line in file:
      line = line.split("#", 1)[0].rstrip()
      if line.endswith("\\"):
        current_line += line[:-1].rstrip()
      else:
        current_line += line
        current_line = current_line.replace("\\\\", "\\")
        if current_line.strip():
          lines.append(current_line)
        current_line = ""
    if current_line.strip():
      current_line = current_line.replace("\\\\", "\\")
      lines.append(current_line)
  return lines

def get_vars(lines:list[str], prefix_list:list[str]):
  lines = [s for s in lines if any(s.startswith(prefix) for prefix in prefix_list)]
  vars = {}
  pattern = r"^\s*(\w+)\s*=\s*(.*)"
  for line in lines:
    match = re.match(pattern, line)
    if match:
      key = match.group(1).strip()
      value = match.group(2).strip()
      vars[key] = value
  return vars
