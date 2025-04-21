import winreg, os, sys, subprocess, re, json
import urllib.request, urllib.parse, zipfile, io
from datetime import datetime
import packaging.version
from typing import Literal
import xaeian as xn

class Ico(xn.IcoText): pass
class Color(xn.Color): pass

#------------------------------------------------------------------------------

def HashString(string:str) -> int:
  hash_value = 5381
  for char in string:
    hash_value = ((hash_value << 5) + hash_value) + ord(char)
  return hash_value & 0xFFFFFFFF

def CCodeEnum(hash_list:list[str], title:str="") -> str:
  if title: title = "".join(char for char in title.upper() if char.isalpha()) + "_Hash_"
  else: title = "HASH_"
  c_code = "\ntypedef enum {\n"
  for name in hash_list:
    value = HashString(name.lower())
    name = name.title()
    name = ''.join(char for char in name if char.isalpha())
    c_code += "  " + title + name + " = " + str(value) + ",\n"
  c_code += "} " + title + "e;\n"
  return c_code

#------------------------------------------------------------------------------

def FilesList(path:str="./", endswith:str="") -> dict[str:list[str]]:
  folder_files = {}
  for folder, subfolders, files in os.walk(path):
    folder = xn.FixPath(folder)
    file_list = []
    for file in files:
      if not endswith or file.endswith(endswith):
        full_path = xn.FixPath(os.path.join(folder, file))
        file_list.append(full_path)
    if file_list:
      folder_files[folder] = file_list
      # subfolders - not used
  return folder_files

def FilesMDate(path:str="./"):
  file_date = {}
  # Traverse through all files and directories within the provided directory
  for folder, subfolders, files in os.walk(path):
    for file in files:
      file_path = os.path.join(folder, file)
      file_date[file_path] = datetime.fromtimestamp(os.path.getmtime(file_path))
  return file_date

def FilesMDateMax(path:str="./") -> tuple|None:
  file_date = FilesMDate(path)
  if not file_date: return None
  max_date = max(file_date.values())
  file = [key for key, data in file_date.items() if data == max_date][0]
  return file, max_date

class ENV:
    
  @staticmethod
  def PathExist(path) -> bool:
    env_path = os.environ.get("PATH", "")
    if path in env_path: return True
    else: return False

  @staticmethod
  def VarExist(var) -> bool:
    if var in os.environ: return True
    else: return False

  @staticmethod
  def AddPath(path) -> bool:
    try:
      key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Environment", 0, winreg.KEY_SET_VALUE | winreg.KEY_READ)
      current_path, _ = winreg.QueryValueEx(key, "Path")
      winreg.SetValueEx(key, "Path", 0, winreg.REG_EXPAND_SZ, f"{current_path};{path}")
      winreg.CloseKey(key)
      return True
    except Exception as e:
      return False

  @staticmethod
  def AddVariable(name, value) -> bool:
    try:
      key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Environment", 0, winreg.KEY_SET_VALUE | winreg.KEY_READ)
      winreg.SetValueEx(key, name, 0, winreg.REG_EXPAND_SZ, value)
      winreg.CloseKey(key)
      return True
    except Exception as e:
      return False

def Integer(value:str|int|None) -> int|None:
  if value is None: return
  number = ""
  for char in str(value):
    if char.isdigit(): number += char
    else: break
  return int(number) if number else None

#------------------------------------------------------------------------------

def FrameworkVersionCheck(version:str, versions:list[str], msg:str) -> bool:
  if version not in versions:
    print(f"{Ico.ERR} Wersja framework'a {Color.MAGENTA}{version}{Color.END} nie istnieje")
    print(msg)
    sys.exit(1)

# def VersionEncode(version:str, hex=False) -> int|str:
#   try:
#     major, minor, patch = map(int, version.split("."))
#     encoded_version = (major << 24) | (minor << 16) | patch
#     return f"0x{encoded_version:08X}" if hex else encoded_version
#   except ValueError:
#     raise ValueError(f"Invalid version format: {version}, expect: 'major.minor.patch'")

# def VersionDecode(encoded_versiWon:int|str) -> str:
#   if isinstance(encoded_version, str):
#     if encoded_version.lower().startswith("0x"):
#       encoded_version = int(encoded_version, 16)
#     else:
#       raise ValueError(f"Invalid hex format: {encoded_version}, expect: '0xAABBCCCC'")
#   major = (encoded_version >> 24) & 0xFF
#   minor = (encoded_version >> 16) & 0xFF
#   patch = encoded_version & 0xFFFF
#   return f"{major}.{minor}.{patch}"

def VersionReal(framework_version:str, latest_version:str):
  if framework_version in ["latest", "last"]: framework_version = latest_version
  elif framework_version in ["dev", "develop"]: framework_version = "develop"
  elif framework_version in ["main", "master"]: framework_version = "main"
  return framework_version

def VersionOlderThan(a:str, b:str) -> bool:
  return packaging.version.Version(a) < packaging.version.Version(b)

#------------------------------------------------------------------------------

def LineRemove(text:str, phrase:str, limit:int=1) -> str:
  lines = text.splitlines()
  result = []
  count = 0
  for line in lines:
    if phrase in line and count < limit: count += 1
    else: result.append(line)
  return "\n".join(result)

def LineReplace(text:str, phrase:str, new_content:str, limit:int=1) -> str:
  lines = text.splitlines()
  result = []
  count = 0
  for line in lines:
    if phrase in line and count < limit:
      indent = len(line) - len(line.lstrip())
      new_line = " " * indent + new_content
      result.append(new_line)
      count += 1
    else:
      result.append(line)
  return "\n".join(result)

def LineAddBefore(text: str, phrase:str, new_line:str, limit:int=1) -> str:
  lines = text.splitlines()
  result = []
  count = 0
  for line in lines:
    if phrase in line and count < limit:
      result.append(new_line)
    result.append(line)
  return "\n".join(result)

def LinesClear(lines:list[str], comment:str="#"):
  lines_ok = []
  current_line = ""
  for line in lines:
    line = line.split(comment, 1)[0].rstrip()
    if line.endswith("\\"):
      current_line += line[:-1].rstrip()
    else:
      current_line += line
      if current_line.strip():
        lines_ok.append(current_line.replace("\\\\", "\\"))
      current_line = ""
  if current_line.strip():
    lines_ok.append(current_line.replace("\\\\", "\\"))
  return lines_ok

def GetVars(lines:list[str], prefix_list:list[str], sep="=", trim_start:str="", required:str=True) -> dict:
  if trim_start:
    lines = [re.sub(f"^{re.escape(trim_start)}+", "", line).lstrip() for line in lines]
  filtered_lines = [s for s in lines if any(s.startswith(prefix) for prefix in prefix_list)]
  variables = {}
  pattern = r"^\s*(\w+)\s*" + re.escape(sep) + r"\s*(.*)"
  for line in filtered_lines:
    match = re.match(pattern, line)
    if match:
      key = match.group(1).strip()
      value = match.group(2).strip().strip('"')
      variables[key] = value
  if required:
    for key in prefix_list:
      if key not in variables:
        print(f"{Ico.WRN} Nie znaleziono zmiennej {Color.MAGENTA}{key}{Color.END}")
        return {}
  return variables

def GetVar(lines:list[str], var_name:str, sep="=", trim_start:str="") -> dict|None:
  vars = GetVars(lines, [var_name])
  return vars[var_name] if var_name in vars else None

def LastLineLen(string:str) -> int:
  return len(string.split('\n')[-1].strip())

#------------------------------------------------------------------------------ High-Level

def SwapCommentLines(content:str, comment:str="#", next_line:bool=False) -> str:
  lines = content.splitlines(keepends=False)
  i = 0
  while i < len(lines):
    find = None
    replace = ""
    if lines[i].startswith(f"{comment} "):
      find = f"{comment} "
    elif lines[i].startswith(f"{comment}\t"):
      find = f"{comment}\t"
      replace = "\t"
    if find is not None:
      lines[i] = xn.ReplaceStart(lines[i], find, replace)
      if next_line:
        if i + 1 < len(lines):
          lines[i + 1] = find + lines[i + 1].lstrip()
          i += 1
      elif i:
        lines[i - 1] = find + lines[i - 1].lstrip()
    i += 1
  return "\n".join(lines)

def CreateFile(name:str, content:str, path:str="./", replace_map:dict={}, remove_line:str="", rewrite:bool=False, color:str=Color.ORANGE) -> str:
  file_name = xn.FixPath(f"{path}/{name}")
  content = content.strip()
  for pattern, value in replace_map.items():
    content = content.replace(pattern, str(value))
  if remove_line: content = LineRemove(content, remove_line)
  xn.FILE.Save(file_name, content)
  suffix = "w prejekcie" if path == "." else f"w folderze {Color.GREY}{path}{Color.END}"
  print(f"{Ico.OK} {"Nadpisano" if rewrite else "Utworzono"} plik {color}{name}{Color.END} {suffix}")
  return file_name

def GetProjectList(path:str) -> list[str]:
  pro_names = []
  pro_paths = []
  path = xn.FixPath(path)
  files_list = FilesList(path, "main.h")
  for pro_path in files_list.keys():
    pro_name = xn.ReplaceStart(pro_path, path + "/", "")
    if not any(pn.lower() == pro_name.lower() for pn in pro_names):
      pro_names.append(pro_name)
      pro_paths.append(pro_path)
    else: print(f"{Ico.WRN} Nazwa projektu {Color.RED}name{Color.END} powtórzyła się w lokalizacji {Color.YELLOW}{pro_names}{Color.END} {Color.RED}{pro_path}{Color.END}")
  return dict(zip(pro_names, pro_paths))

def LastModification(path:str="./") -> str:
  file_date = FilesMDateMax(path)
  if not file_date: return f"{Color.GREY}Unknown{Color.END}"
  file = xn.LocalPath(file_date[0], path)
  date = file_date[1].strftime("%Y-%m-%d %H:%M:%S")
  return f"{Color.BLUE}{file}{Color.END} {Color.GREY}({date}){Color.END}"

#------------------------------------------------------------------------------ Remote

def IsYes(msg:str="Czy zrobić to automatycznie"):
  YES_NO = f"[{Color.GREEN}TAK{Color.END}/{Color.RED}NIE{Color.END}]"
  print(f"{Ico.INF} {msg}? {YES_NO}:", end=" ")
  yes = input().lower()
  return yes == "tak" or yes == "t" or yes == "true" or yes == "yes" or yes == "y"

def Download(url:str, timeout:float=10) -> bytes:
  try:
    response = urllib.request.urlopen(url, timeout=timeout)
    data = response.read()
    zipfile.ZipFile(io.BytesIO(data)).extractall(url)
  except urllib.error.URLError:
    print(f"{Ico.ERR} Nie udało się połączyć z adresem {Color.GREY}{url}{Color.END}")
    sys.exit(1)
  except urllib.error.HTTPError as e:
    print(f"{Ico.ERR} Serwer zwrócił błąd HTTP {e.code} dla {Color.GREY}{url}{Color.END}")
    sys.exit(1)
  return data

def Unzip(data:bytes, path:str, drop_iferr=True):
  try:
    xn.DIR.Create(path)
    zipfile.ZipFile(io.BytesIO(data)).extractall(path)
  except zipfile.BadZipFile:
    print(f"{Ico.ERR} Plik ZIP jest uszkodzony lub nieprawidłowy")
    sys.exit(1)

def GitCloneRepo(url:str, path:str, ref:str|None=None, drop_iferr:bool=False):
  cmd = ["git", "clone"]
  if ref: cmd += ["--branch", ref]
  cmd += [url, path]
  result = subprocess.run(cmd, capture_output=True, text=True)
  if result.returncode:
    if drop_iferr: xn.DIR.Remove(path, force=True)
    print(f"{Ico.ERR} Próba sklonowania repozytorium {Color.ORANGE}{url}{Color.END} nie powiodła się")
    sys.exit(1)

def ProjectRemote(url:str, path:str, ref:str|None=None, name:str="") -> str:
  tmp = ".remote"
  xn.DIR.Create(tmp)
  if url.endswith(".zip"):
    data = Download(url)
    Unzip(data, tmp, drop_iferr=True)
  else:
    GitCloneRepo(url, tmp, ref, True)
  lines = xn.FILE.LoadLines(f"{tmp}/main.h")
  if not lines:
    print(f"{Ico.ERR} Zdalny projekt nie zawiera pliku {Color.BLUE}main.h{Color.END}")
    sys.exit(1)
  if not name:
    name_line = next((line for line in lines if "@name" in line), "")
    name_line = re.sub(r"\(.*?\)|\{.*?\}|\[.*?\]", "", name_line) # del all between (), {}, []
    name_line = re.sub(r"[<>:\"|?*]", "", name_line).replace("\\", "/").strip()
    parts = name_line.split()
    if not parts:
      print(f"{Ico.ERR} Nie udało się odczytać nazwy projektu z pliku {Color.BLUE}main.h{Color.END}")
      print(f"{Ico.INF} Musisz podać nazwę projektu jako argument przy wywołaniu")
      sys.exit(1)
    name = parts[-1]
  path = f"{path}/{name}"
  if xn.DIR.Exists(path):
    print(f"{Ico.ERR} Projekt o nazwie {Color.CYAN}{name}{Color.END} już istnieje")
    sys.exit(1)
  xn.DIR.Move(tmp, path)
  print(f"{Ico.OK} Projekt {Color.CYAN}{name}{Color.END} został pobrany z {Color.GREY}{url}{Color.END}")
  return name

def ProgramVersion(name:str) -> str|None:
  try:
    result = subprocess.run([name, '--version'], capture_output=True, check=True, text=True)
    output = result.stdout + result.stderr
    match = re.search(r'\b\d+\.\d+\.\d+\b', output)
    if match:
      return match.group(0)
    return None
  except Exception:
    return None

def Install(name:str, url:str, path:str, yes:bool=False, unpack_zip:bool=True):
  if not yes and not IsYes():
    print(f"{Ico.ERR} Zapoznaj się z instrukcją https://github.com/OpenCPLC/Wizard")
    sys.exit(1)
  try:
    url = f"{url}/{name}.zip" if unpack_zip else f"{url}/{name}"
    data = Download(url)
    xn.DIR.Create(path + "/")
    path = xn.FixPath(f"{path}/{name}")
    if unpack_zip: Unzip(data, path)
    else:
      with open(path, "wb") as file: file.write(data)
    print(f"{Ico.OK} Instalacja zakończona powodzeniem")
  except Exception as e:
    print(f"{Ico.ERR} Błąd podczas instalacji {Color.BLUE}{name}{Color.END}: {e}")
    sys.exit(1)

FTP_PATH = "http://sqrt.pl"
INSTALL_PATH = "C:"
RESET_CONSOLE = False

def InstallMissingAddPath(name:str, cmd:str, var:str|None=None, yes:bool=False, min_version:str="") -> str|None:
  global RESET_CONSOLE
  version = ProgramVersion(cmd)
  if not version:
    print(f"{Ico.WRN} Program {Color.BLUE}{name}{Color.END} nie jest zainstalowany")
    Install(name, FTP_PATH, INSTALL_PATH, yes)
    path = f"{INSTALL_PATH}\\{name}\\bin"
    if var: ENV.AddVariable(var, path)
    if not ENV.PathExist(path):
      if var and ENV.AddPath(f"%{var}%") or ENV.AddPath(path):
        print(f"{Ico.OK} Ścieżka dla {Color.YELLOW}{cmd}{Color.END} została dodana do zmiennych środowiskowych")
      else:
        print(f"{Ico.ERR} Błąd podczas dodawania ścieżki dla {Color.YELLOW}{cmd}{Color.END} do zmiennych środowiskowych")
        sys.exit(1)
      RESET_CONSOLE = True
  elif min_version and VersionOlderThan(version, min_version):
    print(f"{Ico.WRN} Program {Color.YELLOW}{cmd}{Color.END} jest zainstalowany w wersji {Color.ORANGE}{version}{Color.END}")
    print(f"{Ico.WRN} Wymagana minimalna wersja to {Color.BLUE}{min_version}{Color.END}")
  return version

def ColorUrl(url:str):
  return url.replace("https://", f"{Color.GREY}https://{Color.END}").replace("OpenCPLC", f"{Color.TEAL}OpenCPLC{Color.END}")

def GitCloneMissing(url:str, path:str, ref:str, yes:bool=False, required:bool=True) -> bool:
  if not xn.DIR.Exists(path):
    print(f"{Ico.WRN} Framework {Color.MAGENTA}opencplc{Color.END} nie jest zainstalowany w wersji {Color.BLUE}{ref}{Color.END}")
    if not yes and not IsYes():
      if not required: return False
      print(f"{Ico.ERR} Możesz pobrać go samodzielnie z {ColorUrl(url)}")
      sys.exit(0)
    GitCloneRepo(url, path, ref)
    print(f"{Ico.OK} Repozytorium {Color.ORANGE}{url}{Color.END} zostało sklonowane do {Color.GREY}{xn.LocalPath(path)}{Color.END}")
  return True

def GitGetRef(url: str, option: Literal["--heads", "--tags", "--ref"] = "--ref", use_git: bool = True):
  if option == "--ref": return GitGetRef(url, "--tags", use_git) + GitGetRef(url, "--heads", use_git)
  if use_git:
    result = subprocess.run(["git", "ls-remote", option, url], capture_output=True, text=True)
    lines = result.stdout.strip().splitlines()
    rx = r"refs/tags/([^\^{}]+)$" if option == "--tags" else r"refs/heads/(.+)$"
    refs = [re.search(rx, l).group(1) for l in lines if re.search(rx, l)]
    return sorted(refs, key=packaging.version.parse, reverse=True) if option == "--tags" else refs
  host = "github" if "github.com" in url else "gitlab" if "gitlab.com" in url else None
  if not host:
    raise ValueError("Obsługiwane tylko GitHub/GitLab")
  repo = url.replace(f"https://{host}.com/", "").rstrip("/")
  api = f"https://{host}.com/api/v4/projects/{urllib.parse.quote_plus(repo)}" if host == "gitlab" else f"https://api.github.com/repos/{repo}"
  endpoint = "/repository/tags" if host == "gitlab" and option == "--tags" else \
    "/repository/branches" if host == "gitlab" else \
    "/tags" if option == "--tags" else "/branches"
  data = subprocess.run(["curl", "-s", api + endpoint], capture_output=True, text=True).stdout
  out = json.loads(data)
  names = [x["name"] for x in out]
  return sorted(names, key=packaging.version.parse, reverse=True) if option == "--tags" else names

def AssignName(name:str|bool|None, flag:str|bool|None, msg:str):
  if type(flag) == str:
    if not name: name = flag
    elif name != flag:
      print(f"{Ico.ERR} Nie możesz przekazać nazwy projektu jako parametr domyślny oraz wartości flagi {msg}")
      sys.exit(1)
    flag = True
  return name, flag