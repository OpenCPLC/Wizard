import os, sys, io, argparse
import urllib.request, zipfile
import startup_files as sf, utils

# pip install -U pyinstaller
# pyinstaller --onefile --workpath wizard-build --distpath ./wizard-dist --icon=logo.ico wizard.py

parser = argparse.ArgumentParser(description="OpenPLC project wizard")
parser.add_argument("-n", "--name", type=str, help="Nazwa projektu (default: app)", default="app")
parser.add_argument("-c", "--controller", type=str, help="Model sterownika PLC {Uno|DIO|AIO|Eco|Custom|Void} (default: Uno)" , default="Uno")
parser.add_argument("-f", "--framework", type=str, help="Lokalizacja framework'u OpenCPLC (default: opencplc)" , default="opencplc")
parser.add_argument("-p", "--project", type=str, help="Lokalizacja aktywnego projektu (default: projects/{name})" , default="")
parser.add_argument("-b", "--build", type=str, help="Lokalizacja dla skompilowanych plików framework'u i projektu (default: build)", default="build")
parser.add_argument("-m", "--memory", type=str, help="Ilość pamięci FLASH w wykorzystywanej płytce {128kB|512kB}", default="")
parser.add_argument("-r", "--reset", action="store_true", help="Pozwana na nadpisanie plików konfiguracyjnych", default=False)
parser.add_argument("-o", "--opt", type=str, help="Poziom optymalizacji kompilacji {O0, Og, O1, O2, O3} (default: Og)", default="Og")
parser.add_argument("-v", "--version", action="store_true", help="Wersję programu 'wizard' oraz inne informacje", default=False)
parser.add_argument("-hl", "--hash", nargs="+", type=str, help="[Hash] Lista tagów do za-hash'owania")
parser.add_argument("-ht", "--title", type=str, help="[Hash] Tytół dla enum'a, który zostanie utworzony z listy hash'ów", default="")
parser.add_argument("-hs", "--switch", action="store_true", help="[Hash] Czy wyświetlić gotowy kod switch-case do skopiowania?", default=False)
# -g --gpt Model językowy
args = parser.parse_args()

class Color():
  BLUE = "\033[34m"
  GREEN = "\033[32m"
  RED = "\033[31m"
  YELLOW = "\033[33m"
  CYAN = "\033[36m"
  MAGENTA = "\033[35m"
  GREY = "\033[90m"
  CREAM = "\033[38;5;216m"
  END = "\033[00m"

OK = f"{Color.GREEN}OK{Color.END}"
ERR = f"{Color.RED}ERROR{Color.END}"
WARN = f"{Color.MAGENTA}WARN{Color.END}"
INFO = f"{Color.BLUE}INFO{Color.END}"

if not args.project:
  args.project = f"projects/{args.name}"

if args.hash:
  import chash
  c_code = chash.c_code_enum(args.hash, args.title)
  print(c_code)
  sys.exit()

def print_last_modification(dir:str="./"):
  last_mod = utils.files_mdate_max(dir)
  if not last_mod: return
  file:str = last_mod[0].replace("\\", "/")
  date = last_mod[1].strftime("%Y-%m-%d %H:%M:%S")
  print("•", date, f"{Color.GREY}{file}{Color.END}")

if args.version:
  print(f"Wizard OpenCPLC {Color.CYAN}1.0.0{Color.END}-rc.1")
  # 1.0.0 - Workspace
  # 0.0.3 - Select controller
  # 0.0.2 - Last modification display
  # 0.0.1 - Hash sub-application
  # 0.0.0 - Project builder
  print("Last modifications:")
  print_last_modification(args.framework)
  print_last_modification(args.project)
  print_last_modification(args.build)
  print(f"Repo: {Color.CREAM}https://github.com/OpenCPLC/Wizard{Color.END}")
  sys.exit()

args.controller = args.controller.lower()

controller_define = {
  "void": "STM32G0",
  "custom": "OPENCPLC_CUSTOM",
  "uno": "OPENCPLC_UNO",
  "dio": "OPENCPLC_DIO",
  "aio": "OPENCPLC_AIO",
  "eco": "OPENCPLC_ECO"
}

if args.controller not in controller_define:
  print(f"{ERR} Sterownik {Color.BLUE}opencplc-{args.controller}{Color.END} nie istnieje lub nie jest oficjalnie wspierany")
  print(f"{INFO} Jeżeli korzystasz z własnej konstrukcji zastosuj {Color.GREY}-c --controller{Color.END} {Color.CREAM}custom{Color.END}")
else: CONTROLLER = controller_define[args.controller]

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
FREQ = 16000000 if args.controller in ["eco", "void"] else 18432000

if args.controller == "void": FLASH -= 4
elif args.controller == "eco": FLASH -= 12
else: FLASH -= 20

BASE_URL = "http://sqrt.pl"
BASE_PATH = "C:\\OpenCPLC"
BASE_REPO = "https://github.com/OpenCPLC/Core"
YES_NO = f"[{Color.GREEN}TAK{Color.END}/{Color.RED}NIE{Color.END}]"

def install(name:str, yes:bool=False):
  print(f"Program {Color.BLUE}{name}{Color.END} nie jest zainstalowany.", end=" ")
  print(f"Czy zrobić to automatycznie? {YES_NO}:", end=" ")
  yes_no = input().lower()
  if yes_no != "tak" and yes_no != "t" and yes_no != "true":
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

reset = False

def install_missing_add_apth(name:str, cmd:str, var:str|None=None):
  global reset
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
      reset = True

def create_file(name:str, content:str, path:str=".", replace_map:dict={}) -> str:
  file_name = f"{path}/{name}"
  with open(file_name, "w", encoding="utf-8") as file:
    content = content.strip()
    for pattern, value in replace_map.items():
      content = content.replace(pattern, str(value))
    file.write(content)
    suffix = "w prejekcie" if path == "." else f"w folderze {Color.GREY}{path}{Color.END}"
    print(f"{OK} Utworzono plik {Color.CREAM}{name}{Color.END} {suffix}")
  return file_name

install_missing_add_apth("ArmGCC", "arm-none-eabi-gcc", "ARMGCC")
install_missing_add_apth("OpenOCD", "openocd")
install_missing_add_apth("Make", "make")
install_missing_add_apth("Git", "git")

if reset:
  print(f"{WARN} Zresetuj konsolę systemową po zakończeniu pracy {Color.YELLOW}wizard.exe{Color.END}")
  print(f"{WARN} Spowoduje to załadowanie nowo dodanych ścieżek systemowych")

if not os.path.exists(args.framework):
  os.makedirs(args.framework)
  if not utils.clone_repo(BASE_REPO, args.framework):
    print(f"{ERR} Próba sklonowania repozytorium {Color.CREAM}{BASE_REPO}{Color.END} nie powiodła się")
  if args.controller == "void":
    utils.folder_remove(f"{args.framework}/doc")
    utils.folder_remove(f"{args.framework}/img")
    utils.folder_remove(f"{args.framework}/plc")
    os.remove(f"{args.framework}/readme.md")
  print(f"{OK} Repozytorium {Color.CREAM}{BASE_REPO}{Color.END} zostało sklonowane")

if not os.path.exists(args.project):
  os.makedirs(args.project)

# Utworzenie pliku `main.c`, jeśli nie istnieje
src = utils.files_list(args.project, ".c")
if not any(os.path.basename(file) == "main.c" for files in src.values() for file in files):
  create_file("main.c", sf.main_c, args.project)

# Utworzenie pliku `main.h`, jeśli nie istnieje
head = utils.files_list(args.project, ".h")
if not any(os.path.basename(file) == "main.h" for files in head.values() for file in files):
  create_file("main.h", sf.main_h, args.project, {
    "${DATE}": utils.get_date(),
    "${FREQ}": str(FREQ)
  })

INC = args.framework + "/inc"
LIB = args.framework + "/lib"
PLC = args.framework + "/plc"

utils.make_folder(INC)
utils.make_folder(LIB)
if args.controller != "void": utils.make_folder(PLC)

if args.reset:
  if os.path.exists("./makefile"):
    os.remove("./makefile")
    print(f"{WARN} Usunięto plik {Color.YELLOW}makefile{Color.END}")

new_makefile = False

if not os.path.exists("./makefile"):

  ld = utils.files_list("./", ".ld")
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

  inc = utils.files_list(INC, ".c")
  lib = utils.files_list(LIB, ".c")
  plc = utils.files_list(PLC, ".c")
  scr = utils.files_list(args.project, ".c")
  c_sources = {**inc, **lib, **plc, **scr}
  C_SOURCES = ""
  for folder, files in c_sources.items():
    for file in files:
      file:str = file.replace("\\", "/").lstrip("./")
      folder:str = folder.replace("\\", "/").lstrip("./")
      if folder == f"{PLC}/brd" and file != f"{PLC}/brd/opencplc-" + args.controller + ".c": continue      
      if utils.len_last_line(C_SOURCES) > 80: C_SOURCES += "\\\n"
      C_SOURCES += file.replace("\\", "/").lstrip("./") + " "
  LD_FILE = LD_FILE.replace("\\", "/").lstrip("./")

  inc = utils.files_list(INC, ".s")
  lib = utils.files_list(LIB, ".s")
  plc = utils.files_list(PLC, ".s")
  scr = utils.files_list(args.project, ".s")
  asm_sources = {**inc, **lib, **plc, **scr}
  ASM_SOURCES = ""
  for folder, files in asm_sources.items():
    for file in files:
      file:str
      if utils.len_last_line(ASM_SOURCES) > 80: ASM_SOURCES += "\\\n"
      ASM_SOURCES += file.replace("\\", "/").lstrip("./") + " "

  inc = utils.files_list(INC, ".h")
  lib = utils.files_list(LIB, ".h")
  plc = utils.files_list(PLC, ".h")
  scr = utils.files_list(args.project, ".h")
  c_includes = {**inc, **lib, **plc, **scr}
  C_INCLUDES = ""
  for folder, files in c_includes.items():
    folder:str
    if utils.len_last_line(C_INCLUDES) > 80: C_INCLUDES += "\\\n"
    C_INCLUDES += "-I" + folder.replace("\\", "/").lstrip("./") + " "

  create_file("makefile", sf.makefile, ".", {
    "${NAME}": args.name,
    "${OPT}": args.opt,
    "${BUILD}": args.build,
    "${FAMILY}": FAMILY,
    "${CONTROLLER}": CONTROLLER,
    "${C_SOURCES}": C_SOURCES,
    "${ASM_SOURCES}": ASM_SOURCES,
    "${C_INCLUDES}": C_INCLUDES,
    "${LD_FILE}": LD_FILE,
    "${FRAMEWORK}": args.framework.replace('\\', '\\\\').replace('/', '\\\\'),
    "${PROJECT}": args.project.replace('\\', '\\\\').replace('/', '\\\\')
  })
  new_makefile = True

else:
  print(f"{INFO} Plik {Color.CREAM}makefile{Color.END} już istnieje. Jeżeli chcesz go nadpisać użyj flagi {Color.GREY}-r --reset{Color.END}")

utils.make_folder("./.vscode")

if new_makefile or not os.path.exists(".vscode/c_cpp_properties.json"):
  create_file("c_cpp_properties.json", sf.properties_json, ".vscode", {
    "${FRAMEWORK}": args.framework,
    "${PROJECT}": args.project,
    "${NAME}": args.name,
    "${FAMILY}": FAMILY,
    "${CONTROLLER}": CONTROLLER
  })

if new_makefile or not os.path.exists(".vscode/launch.json"):
  create_file("launch.json", sf.launch_json, ".vscode", {
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
