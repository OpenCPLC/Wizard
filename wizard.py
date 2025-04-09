import os, sys, io, argparse
import urllib.request, zipfile
import startup_files as sf, utils

parser = argparse.ArgumentParser(description="OpenPLC project wizard")



# wizard -i
# jak projekt został usunięty daj o tym informację
#

# 


# TODO `wizard.exe`:
# - Kompilator `gcc` i `openocd` tworzące się lokalnie w przestrznie workspace _(wyeliminuje to problem z wersjami)_
#   - Wtedy make luzem na dysku C
# - Wszystkie kofiguracjie przechowywane w pliku `main.h`, a nie wspólnym `.json` 
#   - Prościej będzie przywrócić projekt, bo nie będzie trzeba znać jego konfiguracji
#   - Prościej będzie po prostu zmodyfikować jakieś wybrane wcześniej ustawienia
# - Plik `flash.ld` generowany dynamicznie, zgodnie z ustawieniami _(tam się nic nie zmienia - będzie czyściej z punktu widzenia programisty aplikacji)_


parser.add_argument("name", type=str, help="Nazwa {name} projektu", default="")
parser.add_argument("-n", "--new", action="store_true", help="Utwórz projekt o wybranej nazwie", default=False)
parser.add_argument("-s", "--select", action="store_true", help="Ustaw wybrany projekt jako aktywny", default=False)
parser.add_argument("-r", "--remove", action="store_true", help="Usuń wybrany projekt", default=False)
parser.add_argument("-c", "--controller", type=str, help="Model sterownika PLC {Uno|DIO|AIO|Eco|Custom|Void} (default: Uno)", default="Uno")
parser.add_argument("-p", "--project", type=str, help="Lokalizacja aktywnego projektu (default: projects/{name})", default="")
parser.add_argument("-f", "--framework", type=str, help="Lokalizacja framework'u OpenCPLC (default: opencplc)" , default="opencplc")
parser.add_argument("-fv", "--framework-version", type=str, nargs="?", help="Wersja framework'u OpenCPLC (default: latest)", const=None, default="latest")
parser.add_argument("-u", "--microcontroller", type=int, help="Ilość pamięci FLASH [kB] w wykorzystywanej płytce {STM32G081|STM32G0C1}", default=0)
parser.add_argument("-m", "--memory", type=int, help="Ilość zarezerwowanej pamięci FLASH [kB] na config i eeprom", default="")
parser.add_argument("-o", "--opt", type=str, help="Poziom optymalizacji kompilacji {O0, Og, O1} (default: Og)", default="Og")
parser.add_argument("-b", "--build", type=str, help="Lokalizacja dla skompilowanych plików framework'u i projektu (default: build)", default="build")
parser.add_argument("-l", "--list", action="store_true", help="Wyświetla listę istniejących projektów", default=False)
parser.add_argument("-i", "--info", action="store_true", help="Zwraca podstawowe informacje o bieżącym projekcie", default=False)
parser.add_argument("-v", "--version", action="store_true", help="Wersję programu 'wizard' oraz inne informacje", default=False)
parser.add_argument("-hl", "--hash", nargs="+", type=str, help="[Hash] Lista tagów do za-hash'owania")
parser.add_argument("-ht", "--hash_title", type=str, help="[Hash] Tytół dla enum'a, który zostanie utworzony z listy hash'ów", default="")
args = parser.parse_args()

# STM32G081|STM32G0C1

class Color():
  BLUE = "\033[34m"
  GREEN = "\033[32m"
  RED = "\033[31m"
  YELLOW = "\033[33m"
  CYAN = "\033[36m"
  TEAL = "\033[38;2;32;178;170m"
  MAGENTA = "\033[35m"
  GREY = "\033[90m"
  CREAM = "\033[38;5;216m"
  END = "\033[00m"

OK = f"{Color.GREEN}OK{Color.END}"
ERR = f"{Color.RED}ERROR{Color.END}"
WARN = f"{Color.MAGENTA}WARN{Color.END}"
INFO = f"{Color.BLUE}INFO{Color.END}"
YES_NO = f"[{Color.GREEN}TAK{Color.END}/{Color.RED}NIE{Color.END}]"

data = utils.load_json("wizard.json")
if not data: data = {}

keys_to_remove = [key for key, info in data.items() if not os.path.exists(info["project"])]
for key in keys_to_remove:
  del data[key]

if not args.project:
  args.project = f"projects/{args.name}"

exit_flag = False

if args.framework_version is None:
  versions = ["1.0.2", "1.0.1", "1.0.0"]
  msg = f"Framework Versions: "
  latest = " (latest)"
  for ver in versions:
    msg += f"{Color.CYAN}{ver}{Color.END}{latest}, "
    latest = ""
  msg = msg.rstrip(", ")
  print(msg)
  exit_flag = True

if args.list:
  msg = f"Projects: "
  for key, info in data.items():
    color = {
      "Uno": Color.TEAL,
      "DIO": Color.BLUE,
      "AIO": Color.GREEN,
      "Eco": Color.CYAN,
      "Void": Color.MAGENTA,
      "Custom": Color.RED
    }[info["controller"]]
    msg += f"{color}{info["name"]}{Color.END}, "
  msg = msg.rstrip(", ")
  print(msg)
  exit_flag = True

if args.version:
  print(f"{Color.TEAL}Wizard{Color.END} OpenCPLC {Color.CYAN}1.0.0-rc.4{Color.END}")
  print(f"Repo: {Color.CREAM}https://github.com/OpenCPLC/Wizard{Color.END}")
  exit_flag = True

def get_last_modification(dir:str="./"):
  last_mod = utils.files_mdate_max(dir)
  if not last_mod: return
  date = last_mod[1].strftime("%Y-%m-%d %H:%M:%S")
  return date

if args.info:
  lines = utils.read_lines("makefile", "#")
  info = utils.get_vars(lines, ["TARGET", "FW", "PRO", "BUILD", "OPT", "CTRL", "FAMILY"])
  info["FW"] = info["FW"].replace("\\", "/")
  info["PRO"] = info["PRO"].replace("\\", "/")
  info["BUILD"] = info["BUILD"].replace("\\", "/")
  opencplc_h = utils.read_lines(f"{info["FW"]}/plc/brd/opencplc.h", "//")
  fw_version = utils.get_vars(opencplc_h, ["OPENCPLC_VERSION"], " ", "#define")["OPENCPLC_VERSION"]
  ctrl_define = {
    "STM32G0": f"Void {Color.GREY}{info["FAMILY"]}{Color.END}",
    "OPENCPLC_CUSTOM": "Custom",
    "OPENCPLC_UNO": f"OpenCPLC {Color.BLUE}Uno{Color.END}",
    "OPENCPLC_DIO": f"OpenCPLC {Color.BLUE}DIO{Color.END}",
    "OPENCPLC_AIO": f"OpenCPLC {Color.BLUE}AIO{Color.END}",
    "OPENCPLC_ECO": f"OpenCPLC {Color.BLUE}Eco{Color.END}"
  }
  print(f"{Color.TEAL}OpenCPLC{Color.END} project information:")
  print(f"• Name {Color.GREY}-n{Color.END}: {Color.BLUE}{info["TARGET"]}{Color.END}")
  ctrl = ctrl_define[info["CTRL"]] if info["CTRL"] in ctrl_define else f"{Color.RED}Not found{Color.END}"
  print(f"• Controller {Color.GREY}-c{Color.END}: {ctrl}")
  print(f"• Framework path {Color.GREY}-f{Color.END}: {Color.CREAM}{info["FW"]}{Color.END}")
  print(f"• Framework version {Color.GREY}-f{Color.END}: OpenCPLC {Color.CYAN}{fw_version}{Color.END}")
  print(f"• Framework update: {get_last_modification(info["FW"])}")
  print(f"• Project path {Color.GREY}-p{Color.END}: {Color.CREAM}{info["PRO"]}{Color.END}")
  print(f"• Project last modification: {get_last_modification(info["PRO"])}")
  print(f"• Build path {Color.GREY}-b{Color.END}: {Color.CREAM}{info["BUILD"]}{Color.END}")
  print(f"• Optimization level {Color.GREY}-o{Color.END}: {info["OPT"]}")
  exit_flag = True

if args.hash:
  import chash
  c_code = chash.c_code_enum(args.hash, args.hash_title)
  print(c_code)
  exit_flag = True

if exit_flag:
  utils.save_json_prettie("wizard.json", data)
  sys.exit()

def isyes():
  yes = input().lower()
  return yes == "tak" or yes == "t" or yes == "true" or yes == "yes" or yes == "y"

if args.select != None:
  if args.select == "":
    lines = utils.read_lines("makefile", "#")
    args.select = utils.get_vars(lines, ["TARGET"])["TARGET"]
  KEY = args.select.lower()
  if KEY in data:
    args.name = data[KEY]["name"]
    args.controller = data[KEY]["controller"]
    if args.controller in ["void", "custom"]:
      args.memory = data[KEY]["memory"]
    args.framework = data[KEY]["framework"]
    args.project = data[KEY]["project"]
    args.build = data[KEY]["build"]
    args.opt = data[KEY]["opt"]
  else:
    print(f"{ERR} Projekt o nazwie {Color.YELLOW}{args.select}{Color.END} nie istnieje")
    print(f"{INFO} Do wyświetlania listy projektów służy flaga {Color.GREY}-l --list{Color.END}")
    print(f"{INFO} Aby stworzyć nowy projekt zastosuj: {Color.GREY}-n --name{Color.END} {args.select}")
    sys.exit()
else:
  KEY = args.name.lower()
  if KEY in data:
    print(f"{WARN} Projekt o nazwie {Color.YELLOW}{args.name}{Color.END} już istnieje")
    print(f"{WARN} Czy nadpisać konfigurację? {YES_NO}:", end=" ")
    if not isyes():
      print(f"{INFO} Aby przełączyć się na istniejący projekt zastosuj: {Color.GREY}-s --select{Color.END} {args.name}")
      sys.exit()

args.opt = args.opt[0].upper() + args.opt[1].lower()
if args.opt not in ["O0", "Og", "01", "02", "03"]: args.opt = "0g"
if args.opt in ["02", "03"]:
  print(f"{ERR} Poziom optymalizacji {args.opt} jest niedozwolony")
  sys.exit()

controller_define = {
  "void": "STM32G0",
  "custom": "OPENCPLC_CUSTOM",
  "uno": "OPENCPLC_UNO",
  "dio": "OPENCPLC_DIO",
  "aio": "OPENCPLC_AIO",
  "eco": "OPENCPLC_ECO"
}
args.controller = args.controller.lower()

if args.controller not in controller_define:
  print(f"{ERR} Sterownik {Color.BLUE}opencplc-{args.controller}{Color.END} nie istnieje lub nie jest oficjalnie wspierany")
  print(f"{INFO} Jeżeli korzystasz z własnej konstrukcji zastosuj: {Color.GREY}-c --controller{Color.END} custom")
  sys.exit()
else: CTRL = controller_define[args.controller]

if not args.memory:
  if args.controller in ["eco", "void"]: args.memory = "128kB"
  else: args.memory = "512kB"

if args.memory == "128": args.memory = "128kB"
if args.memory == "512": args.memory = "512kB"

FAMILY = { "128kB": "STM32G081xx", "512kB": "STM32G0C1xx" }[args.memory]
DEVICE = { "128kB": "STM32G081RB", "512kB": "STM32G0C1RE" }[args.memory]
SVD = { "128kB": "stm32g081.svd", "512kB": "stm32g0C1.svd" }[args.memory]
FLASH = { "128kB": 128, "512kB": 512 }[args.memory]
RAM = { "128kB": 36, "512kB": 144 }[args.memory]
FREQ = 64000000 if args.controller in ["eco", "void"] else 59904000

VOID = False
if args.controller == "void":
  FLASH -= 4
  VOID = True
elif args.controller == "eco": FLASH -= 12
else: FLASH -= 20

BASE_URL = "http://sqrt.pl"
BASE_PATH = "C:\\OpenCPLC"
BASE_REPO = "https://github.com/OpenCPLC/Core"

def install(name:str, yes:bool=False):
  print(f"{WARN} Program {Color.BLUE}{name}{Color.END} nie jest zainstalowany.")
  print(f"{INFO} Czy zrobić to automatycznie? {YES_NO}:", end=" ")
  if not isyes():
    print(f"{ERR} Zapoznaj się z instrukcją {Color.BLUE}{BASE_REPO}{Color.END}!")
    sys.exit()
  try:
    url = f"{BASE_URL}/{name}.zip"
    response = urllib.request.urlopen(url)
    zip_content = response.read()
    with zipfile.ZipFile(io.BytesIO(zip_content)) as zip_ref:
      utils.make_folder(f"{BASE_PATH}\\{name}")
      zip_ref.extractall(f"{BASE_PATH}\\{name}")
      print(f"{OK} Instalacja zakończona powodzeniem")
  except Exception as e:
    print(f"{ERR} Błąd podczas instalacji {Color.BLUE}{name}{Color.END}: {e}")
    sys.exit()

reset_console = False

def install_missing_add_path(name:str, cmd:str, var:str|None=None):
  global reset_console
  if not utils.program_recognized(cmd):
    install(name)
    path = f"{BASE_PATH}\\{name}\\bin"
    if var: utils.Env.add_variable(var, path)
    if not utils.Env.path_exist(path):
      if var and utils.Env.add_path(f"%{var}%") or utils.Env.add_path(path):
        print(f"{OK} Ścieżka dla {Color.YELLOW}{cmd}{Color.END} została dodana do zmiennych środowiskowych")
      else:
        print(f"{ERR} Błąd podczas dodawania ścieżki dla {Color.YELLOW}{cmd}{Color.END} do zmiennych środowiskowych")
        sys.exit()
      reset_console = True

def create_file(name:str, content:str, path:str=".", replace_map:dict={}, remove_line:str="") -> str:
  file_name = f"{path}/{name}"
  with open(file_name, "w", encoding="utf-8") as file:
    content = content.strip()
    for pattern, value in replace_map.items():
      content = content.replace(pattern, str(value))
    if remove_line: content = utils.line_remove(content, remove_line)
    file.write(content)
    suffix = "w prejekcie" if path == "." else f"w folderze {Color.GREY}{path}{Color.END}"
    print(f"{OK} Utworzono plik {Color.CREAM}{name}{Color.END} {suffix}")
  return file_name

#if not VOID:

install_missing_add_path("ArmGCC", "arm-none-eabi-gcc", "ARMGCC")
install_missing_add_path("OpenOCD", "openocd")
install_missing_add_path("Make", "make")
install_missing_add_path("Git", "git")

if reset_console:
  print(f"{WARN} Zresetuj konsolę systemową po zakończeniu pracy {Color.YELLOW}wizard.exe{Color.END}")
  print(f"{WARN} Spowoduje to załadowanie nowo dodanych ścieżek systemowych")

if not os.path.exists(args.framework):
  os.makedirs(args.framework)
  # TODO: Pobierz framework w wskazanej wersji args.framework_version
  if not utils.clone_repo(BASE_REPO, args.framework):
    print(f"{ERR} Próba sklonowania repozytorium {Color.CREAM}{BASE_REPO}{Color.END} nie powiodła się")
  # if args.controller == "void":
  #   utils.folder_remove(f"{args.framework}/res")
  #   utils.folder_remove(f"{args.framework}/plc")
  #   os.remove(f"{args.framework}/readme.md")
  print(f"{OK} Repozytorium {Color.CREAM}{BASE_REPO}{Color.END} zostało sklonowane")
else:
  pass
  # TODO: Jeśli folder z framework'iem istnieje, sprawdź jego wersję
  # TODO: W przypadku konfliktu zgłoś błąd

if not os.path.exists(args.project):
  os.makedirs(args.project)

# Utworzenie pliku `main.c`, jeśli nie istnieje
src = utils.files_list(args.project, ".c")
if not any(os.path.basename(file) == "main.c" for files in src.values() for file in files):
  main_c = sf.main_c_void if VOID else sf.main_c
  create_file("main.c", main_c, args.project, {
    "${FAMILY}": FAMILY,
  })

# Utworzenie pliku `main.h`, jeśli nie istnieje
head = utils.files_list(args.project, ".h")
if not any(os.path.basename(file) == "main.h" for files in head.values() for file in files):
  create_file("main.h", sf.main_h, args.project, {
    "${NAME}": args.name,
    "${DATE}": utils.get_date(),
    "${FREQ}": str(FREQ)
  })
  # TODO: Dla wersji różnej od 'dev'|'develop' utwórz #define PRO_OPENCPLC_VERSION
else:
  pass
  # TODO: Jeżeli istnieje, porównaj z wersją frameworka.
  # TODO: W przypadku konfliktu zgłoś błąd

INC = args.framework + "/inc"
LIB = args.framework + "/lib"
PLC = args.framework + "/plc"

utils.make_folder(INC)
utils.make_folder(LIB)
if not VOID: utils.make_folder(PLC)

if os.path.exists("./makefile"):
  os.remove("./makefile")
  print(f"{INFO} Plik {Color.YELLOW}makefile{Color.END} został nadpisany")

new_makefile = False

if not os.path.exists("./makefile"):

  ld = utils.files_list(args.project, ".ld")
  ld_count = len(ld)
  if ld_count == 0:
    LD_FILE = create_file("flash.ld", sf.flash_ld, args.project, {
      "${FLASH}": FLASH,
      "${RAM}": RAM
    })
  else:
    _, ld_files = ld.popitem()
    if ld_count > 1 or len(ld_files) > 1:
      print(f"{ERR} Projekt zawiera więcej niż jeden plik {Color.CREAM}ld{Color.END}. {Color.RED}Usuń zbędny plik!{Color.END}")
      sys.exit()
    else:
      LD_FILE = ld_files[0]
  
  fw:str = args.framework.replace("\\", "/").lstrip("./")
  pro:str = args.project.replace("\\", "/").lstrip("./")
  build:str = args.build.replace("\\", "/").lstrip("./")
  LD_FILE = os.path.relpath(LD_FILE, pro)

  inc = utils.files_list(INC, ".c")
  lib = utils.files_list(LIB, ".c")
  plc = utils.files_list(PLC, ".c") if not VOID else {}
  scr = utils.files_list(pro, ".c")

  c_sources = {**inc, **lib, **plc, **scr}
  C_SOURCES = ""
  for folder, files in c_sources.items():
    for file in files:
      file:str = file.replace("\\", "/").lstrip("./")
      folder:str = folder.replace("\\", "/").lstrip("./")
      if folder == f"{PLC}/brd" and file != f"{PLC}/brd/opencplc-" + args.controller + ".c": continue
      file = utils.replace_start(file, fw, "$(FW)")
      file = utils.replace_start(file, pro, "$(PRO)")
      if utils.len_last_line(C_SOURCES) > 80: C_SOURCES += "\\\n"
      C_SOURCES += file.replace("\\", "/").lstrip("./") + " "
  C_SOURCES = C_SOURCES.rstrip(" ")

  inc = utils.files_list(INC, ".s")
  lib = utils.files_list(LIB, ".s")
  plc = utils.files_list(PLC, ".s") if not VOID else {}
  scr = utils.files_list(pro, ".s")
  asm_sources = {**inc, **lib, **plc, **scr}
  ASM_SOURCES = ""
  for folder, files in asm_sources.items():
    for file in files:
      file:str = utils.replace_start(file, fw, "$(FW)")
      file = utils.replace_start(file, pro, "$(PRO)")
      if utils.len_last_line(ASM_SOURCES) > 80: ASM_SOURCES += "\\\n"
      ASM_SOURCES += file.replace("\\", "/").lstrip("./") + " "
  ASM_SOURCES = ASM_SOURCES.rstrip(" ")

  inc = utils.files_list(INC, ".h")
  lib = utils.files_list(LIB, ".h")
  plc = utils.files_list(PLC, ".h") if not VOID else {}
  scr = utils.files_list(pro, ".h")
  c_includes = {**inc, **lib, **plc, **scr}
  C_INCLUDES = ""
  for folder, files in c_includes.items():
    folder:str = utils.replace_start(folder, fw, "$(FW)")
    folder = utils.replace_start(folder, pro, "$(PRO)")
    if utils.len_last_line(C_INCLUDES) > 80: C_INCLUDES += "\\\n"
    C_INCLUDES += "-I" + folder.replace("\\", "/").lstrip("./") + " "
  C_INCLUDES = C_INCLUDES.rstrip(" ")

  create_file("makefile", sf.makefile, ".", {
    "${NAME}": args.name,
    "${CTRL}": CTRL,
    "${FRAMEWORK}": fw.replace('\\', '\\\\').replace('/', '\\\\'),
    "${PROJECT}": pro.replace('\\', '\\\\').replace('/', '\\\\'),
    "${OPT}": args.opt,
    "${BUILD}": build,
    "${FAMILY}": FAMILY,
    "${C_SOURCES}": C_SOURCES,
    "${ASM_SOURCES}": ASM_SOURCES,
    "${C_INCLUDES}": C_INCLUDES,
    "${LD_FILE}": LD_FILE
  })
  new_makefile = True

else:
  print(f"{ERR} Nie można nadpisać pliku {Color.CREAM}makefile{Color.END}. Usuń go ręcznie!")
  sys.exit()

utils.make_folder("./.vscode")

if new_makefile or not os.path.exists(".vscode/c_cpp_properties.json"):
  create_file("c_cpp_properties.json", sf.properties_json, ".vscode", {
    "${FRAMEWORK}": fw,
    "${PROJECT}": pro,
    "${NAME}": args.name,
    "${FAMILY}": FAMILY,
    "${CTRL}": CTRL
  }, remove_line = "/plc/**" if VOID else "")

if new_makefile or not os.path.exists(".vscode/launch.json"):
  create_file("launch.json", sf.launch_json, ".vscode", {
    "${FRAMEWORK}": fw,
    "${BUILD}": build,
    "${NAME}": args.name,
    "${DEVICE}": DEVICE,
    "${SVD}": SVD
  })

if not os.path.exists(".vscode/tasks.json"):
  create_file("tasks.json", sf.tasks_json, ".vscode")

if not os.path.exists(".vscode/settings.json"):
  create_file("settings.json", sf.settings_json, ".vscode")

if not os.path.exists(".vscode/extensions.json"):
  create_file("extensions.json", sf.extensions_json, ".vscode")

if KEY not in data: data[KEY] = {}
data[KEY]["name"] = args.name
data[KEY]["controller"] = {"void": "Void", "custom": "Custom", "uno": "Uno", "dio": "DIO", "aio": "AIO", "eco": "Eco" }[args.controller]
if args.controller in ["void", "custom"]:
  data[KEY]["memory"] = args.memory
data[KEY]["framework"] = fw
data[KEY]["project"] = pro
data[KEY]["build"] = build
data[KEY]["opt"] = args.opt

utils.save_json_prettie("wizard.json", data)
