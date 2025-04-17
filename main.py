import sys, argparse
import xaeian as xn, utils
from datetime import datetime

VERSIONS = ["develop"]

class Ico(xn.IcoText): pass
class Color(xn.Color): pass

parser = argparse.ArgumentParser(description="OpenPLC project wizard")
parser.add_argument("name", type=str, nargs="?", help="Nazwa projektu", default="")
parser.add_argument("-n", "--new", type=str, nargs="?", help="Utwórz nowy projekt", const=True)
parser.add_argument("-s", "--sample", type=str, nargs="?", help="Wczytuje demonstracyjny projekt o wskazanej nazwie", const=True)
parser.add_argument("-r", "--reload", action="store_true", help="Przeładuj aktualnie aktywny projekt. Nie wymaga podawania nazwy {name}", default=False)
parser.add_argument("-f", "--framework", type=str, nargs="?", help="Wersja framework'a OpenCPLC, format: <major>.<minor>.<patch> or {latest|develop|main}")
parser.add_argument("-b", "--board", type=str, nargs="?", help="Model sterownika PLC {Uno|DIO|AIO|Eco|None}")
parser.add_argument("-c", "--chip", type=str, nargs="?", help="Wykorzystywany mikrokontroler {STM32G081|STM32G0C1}. Wybór wpływa na dostępną ilość pamięci FLASH[kB] i RAM [kB] na płytce")
parser.add_argument("-m", "--user_memory", type=int, nargs="?", help="Ilość zarezerwowanej pamięci FLASH[kB] na konfigurację i EEPROM w aplikacji", default=0)
parser.add_argument("-o", "--opt-level", type=str, nargs="?", help="Poziom optymalizacji kompilacji {O0, Og, O1} (default: Og)", default="Og")
parser.add_argument("-l", "--list", action="store_true", help="Wyświetla listę istniejących projektów", default=False)
parser.add_argument("-u", "--update", action="store_true", help="Sprawdza dostępność aktualizacji i aktualizuje program Wizard", default=False)
parser.add_argument("-i", "--info", action="store_true", help="Zwraca podstawowe informacje o projekcie", default=False)
parser.add_argument("-v", "--version", action="store_true", help="Wersję programu 'wizard' oraz inne informacje", default=False)
parser.add_argument("-y", "--yes", action="store_true", help="Automatycznie potwierdza wszystkie operacje", default=False)
parser.add_argument("-fv", "--framework_versions", action="store_true", help="Wyświetla wszystkie dostępne wersje frameworka", default=False)
parser.add_argument("-hl", "--hash_list", nargs="+", type=str, help="[Hash] Lista tagów do za-hash'owania")
parser.add_argument("-ht", "--hash_title", type=str, help="[Hash] Tytół dla enum'a, który zostanie utworzony z listy hash'ów", default="")
args = parser.parse_args()

class flag():
  n = f"{Color.YELLOW}-n{Color.END} {Color.GREY}--new{Color.END}"
  r = f"{Color.YELLOW}-r{Color.END} {Color.GREY}--reload{Color.END}"
  s = f"{Color.YELLOW}-s{Color.END} {Color.GREY}--sample{Color.END}"
  f = f"{Color.YELLOW}-f{Color.END} {Color.GREY}--framework{Color.END}"
  b = f"{Color.YELLOW}-b{Color.END} {Color.GREY}--board{Color.END}"
  c = f"{Color.YELLOW}-c{Color.END} {Color.GREY}--chip{Color.END}"
  u = f"{Color.YELLOW}-u{Color.END} {Color.GREY}--user-memory{Color.END}"
  o = f"{Color.YELLOW}-o{Color.END} {Color.GREY}--opt-level{Color.END}"
  fv = f"{Color.YELLOW}-fv{Color.END} {Color.GREY}--framework-versions{Color.END}"

#------------------------------------------------------------------------------

exit_flag = False

if args.version:
  # 0.0.0: Beta init
  print(f"OpenCPLC Wizard {Color.BLUE}{VERSIONS[0]}{Color.END}")
  print(f"{Color.GREY}https://{Color.END}github.com/{Color.TEAL}OpenCPLC{Color.END}/Wizard")
  exit_flag = True

if args.framework_versions:
  msg = f"Framework Versions: "
  latest = f" {Color.GREY}(latest){Color.END}"
  color = Color.BLUE
  for ver in VERSIONS:
    msg += f"{color}{ver}{Color.END}{latest}, "
    color = Color.TEAL
    latest = ""
  msg = msg.rstrip(", ")
  print(msg)
  exit_flag = True

if args.hash_list:
  c_code = utils.CCodeEnum(args.hash_list, args.hash_title)
  print(c_code)
  exit_flag = True

if exit_flag: sys.exit(0)

#------------------------------------------------------------------------------

if args.new and args.reload:
  print(f"{Ico.ERR} Nie można jednocześnie utworzyć nowego projektu {flag.n} i przeładować istniejącego {flag.r}")
  sys.exit(1)
if args.reload and args.sample:
  print(f"{Ico.ERR} Nie można jednocześnie przeładować istniejącego projektu {flag.r} i użyć przykładu demonstracyjnego {flag.s}")
  sys.exit(1)
if args.new and args.sample:
  print(f"{Ico.ERR} Nie można jednocześnie utworzyć nowego projektu {flag.n} i użyć przykładu demonstracyjnego {flag.s}")
  sys.exit(1)

if type(args.new) == str:
  if not args.name: args.name = args.new
  elif args.name != args.new:
    print(f"{Ico.ERR} Nie możesz przekazać nazwy projektu jako parametr domyślny oraz wartości flagi {flag.n}")
    sys.exit(1)
  args.new = True

if type(args.sample) == str:
  if not args.name: args.name = args.sample
  elif args.name != args.sample:
    print(f"{Ico.ERR} Nie możesz przekazać nazwy projektu jako parametr domyślny oraz wartości flagi {flag.s}")
    sys.exit(1)
  args.sample = True

# TODO: Obsługa przykłądów -- oraz detekcja w reload -- wykrywanie ścieżki

#------------------------------------------------------------------------------ Install

utils.InstallMissingAddPath("Git", "git", print_version=False)
utils.InstallMissingAddPath("ArmGCC", "arm-none-eabi-gcc", "ARMGCC", print_version=False)
utils.InstallMissingAddPath("OpenOCD", "openocd", print_version=False)
utils.InstallMissingAddPath("Make", "make", print_version=False)

if utils.RESET_CONSOLE:
  print(f"{Ico.WRN} Zresetuj konsolę systemową po zakończeniu pracy {Color.YELLOW}wizard.exe{Color.END}")
  print(f"{Ico.WRN} Spowoduje to załadowanie nowo dodanych ścieżek systemowych")

#------------------------------------------------------------------------------

xn.FIX_PATH = True
xn.ONEFILE_PACK = True

class sf(): # startup files
  wizard_json = xn.FILE.Load("files/wizard.json")
  makefile = xn.FILE.Load("files/makefile")
  flash_ld = xn.FILE.Load("files/flash.ld")
  properties_json = xn.FILE.Load("files/properties.json")
  launch_json = xn.FILE.Load("files/launch.json")
  tasks_json = xn.FILE.Load("files/tasks.json")
  settings_json = xn.FILE.Load("files/settings.json")
  extensions_json = xn.FILE.Load("files/extensions.json")
  main_h = xn.FILE.Load("files/main.h")
  main_c = xn.FILE.Load("files/main.c")
  main_none_c = xn.FILE.Load("files/main-none.c")

xn.ONEFILE_PACK = False

if not xn.FILE.Exists("wizard.json"):
  xn.FILE.Save("wizard.json", sf.wizard_json)
wizard_config = xn.JSON.Load("wizard.json")

# TODO: wykrywanie braków w configu

if not args.name:
  if args.reload or args.info:
    if not xn.FILE.Exists("makefile"):
      print(f"{Ico.ERR} Nie znaleziono pliku {Color.ORANGE}makefile{Color.END}, który jest wymagany do przeładowania projektu")
      print(f"{Ico.INF} W takim przypadku należy podać jego nazwę jako argument domyślny")
      sys.exit(1)
    lines = xn.FILE.LoadLines("makefile")
    lines = utils.LinesClear(lines, "#")
    makefile_name = utils.GetVar(lines, "NAME")
    if makefile_name is None:
      print(f"{Ico.ERR} Plik {Color.ORANGE}makefile{Color.END} nie zawiera nazwy projektu")
      print(f"{Ico.INF} W takim przypadku należy podać jego nazwę jako argument domyślny")
      sys.exit(1)
    args.name = makefile_name
  else:
    print(f"{Ico.ERR} Nazwa {Color.YELLOW}name{Color.END} projektu nie została określona")
    print(f"{Ico.INF} Dotyczy to zarówno przełączenia się na istniejący projekt, jak i tworzenia nowego za pomocą flagi {flag.n}")
    print(f"{Ico.RUN} Gdy chcesz przeładować aktywny projekt, dodaj do wywołania flagę {flag.r}")
    sys.exit(1)

CFG = { "name": args.name }
PATH = wizard_config["paths"]
PRO = utils.GetProjectList(PATH["projects"])
PATH["pro"] = xn.LocalPath(PATH["projects"] + "/" + args.name)

wizard_config["default"]["framework-version"] = utils.FrameworkTrueVersion(wizard_config["default"]["framework-version"], VERSIONS[0])
args.framework = utils.FrameworkTrueVersion(args.framework, VERSIONS[0])

#------------------------------------------------------------------------------

if args.new:
  if args.name.lower() in (pro_name.lower() for pro_name in PRO.keys()):
    print(f"{Ico.ERR} Projekt {Color.YELLOW}{args.name}{Color.END} już istnieje")
    print(f"{Ico.RUN} Użyj innej nazwy lub uruchom prgram {Color.TEAL}wizard{Color.END} bez flagi {flag.n}")
    sys.exit(1)
  if not args.board:
    print(f"{Ico.WRN} Nie określiłeś sterownika {Color.MAGENTA}board{Color.END}")
    if not args.yes and not utils.IsYes(f"Czy pracujesz na płycie OpenCPLC {Color.TEAL}Uno{Color.END}"):
      print(f"{Ico.ERR} W takim razie musisz wybrać sterownik podczas tworzenia nowego projektu")
      print(f"{Ico.RUN} Uruchom program wizard, dodając flagę {flag.b}")
      sys.exit(1)
    args.board = "Uno"
  CFG["board"] = args.board.lower()
  if args.chip: CFG["chip"] = args.chip
  elif CFG["board"] in ["uno", "dio", "aio"]: CFG["chip"] = "STM32G0C1"
  elif CFG["board"] in ["eco"]: CFG["chip"] = "STM32G081"
  else: CFG["chip"] = wizard_config["default"]["chip"]
  CFG["framework-version"] = args.framework or wizard_config["default"]["framework-version"]
  if args.user_memory: CFG["user-memory"] = args.user_memory
  elif CFG["board"] in ["uno", "dio", "aio"]: CFG["user-memory"] = 20
  elif CFG["board"] in ["eco"]: CFG["user-memory"] = 12
  else: CFG["user-memory"] = wizard_config["default"]["user-memory"]
  CFG["opt-level"] = args.opt_level or wizard_config["default"]["opt-level"]
  CFG["log-level"] = "LOG_LEVEL_INFO"
  CFG["freq"] = 59904000 if CFG["board"] in ["uno", "dio", "aio"] else 64000000
else:
  if args.name.lower() not in (pro_name.lower() for pro_name in PRO.keys()):
    print(f"{Ico.ERR} Projekt o nazwie {Color.MAGENTA}{args.name}{Color.END} nie został znaleziony")
    print(f"{Ico.RUN} Możesz spróbować utworzyć projekt, dodając flagę {flag.n} podczas wywołania")
    sys.exit(1)
  lines = xn.FILE.LoadLines(PRO[args.name] + "/main.h")
  lines = utils.LinesClear(lines, "//")
  info = utils.GetVars(lines, ["PRO_BOARD", "PRO_CHIP"], "_", "#define")
  info |= utils.GetVars(lines, ["PRO_FRAMEWORK_VERSION", "PRO_OPT_LEVEL", "PRO_USER_MEMORY_KB", "LOG_LEVEL", "SYS_CLOCK_FREQ"], " ", "#define")
  CFG["board"] = info["PRO_BOARD"]
  CFG["chip"] = info["PRO_CHIP"]
  CFG["framework-version"] = info["PRO_FRAMEWORK_VERSION"]
  if args.framework and args.framework != CFG["framework-version"]:
    print(f"{Ico.ERR} Wersja projektu {Color.MAGENTA}{CFG["framework-version"]}{Color.END} nie zgadza się z wersją frameworka {Color.BLUE}{args.framework}{Color.END}")
    print(f"{Ico.RUN} Zmień wersję w projekcie lub uruchom program bez podawania wersji frameworka przy użyciu flagi {flag.f}")
    sys.exit(1)
  CFG["user-memory"] = int(info["PRO_USER_MEMORY_KB"])
  CFG["opt-level"] = info["PRO_OPT_LEVEL"]
  CFG["log-level"] = info["LOG_LEVEL"]
  CFG["freq"] = info["SYS_CLOCK_FREQ"]
  msg = "jest ignrowana podczas ładowania istniejącgo projektu"
  if args.board: print(f"{Ico.WRN} Flaga {flag.b} {msg}")
  if args.chip: print(f"{Ico.WRN} Flaga {flag.c} {msg}")
  if args.user_memory: print(f"{Ico.WRN} Flaga {flag.u} {msg}")

CFG["board"] = CFG["board"].lower()
if CFG["board"] == "none": CFG["board"] = None
CFG["chip"] = CFG["chip"].upper()
CFG["user-memory"] = utils.Integer(CFG["user-memory"])
CFG["opt-level"] = CFG["opt-level"][0].upper() + CFG["opt-level"][1].lower()
if CFG["opt-level"] not in ["O0", "Og", "01", "02", "03"]: CFG["opt-level"] = "0g"
if CFG["opt-level"] in ["02", "03"]:
  print(f"{Ico.ERR} Poziom optymalizacji {CFG["opt-level"]} jest niedozwolony")
  sys.exit(1)
CFG["family"] = CFG["chip"] + "xx"
CFG["device"] = { "STM32G081": "STM32G081RB", "STM32G0C1": "STM32G0C1RE" }[CFG["chip"]]
CFG["svd"] = { "STM32G081": "stm32g081.svd", "STM32G0C1": "stm32g0C1.svd" }[CFG["chip"]]
CFG["flash"] = { "STM32G081": 128, "STM32G0C1": 512 }[CFG["chip"]] - CFG["user-memory"]
CFG["ram"] = { "STM32G081": 36, "STM32G0C1": 144 }[CFG["chip"]]

#------------------------------------------------------------------------------

if args.info:
  print(f"{Ico.INF} Project name: {Color.TEAL}{CFG["name"]}{Color.END}")
  print(f"{Ico.GAP} Board {flag.b}: {Color.BLUE}{CFG["board"]}{Color.END}")
  print(f"{Ico.GAP} Chip {flag.c}: {Color.ORANGE}{CFG["chip"]}{Color.END}")
  print(f"{Ico.GAP} Framework version: {flag.f}: {Color.BLUE}{CFG["framework-version"]}{Color.END}")
  print(f"{Ico.GAP} User memory {flag.u}: {Color.CYAN}{CFG["user-memory"]}{Color.END}kB")
  print(f"{Ico.GAP} Optimization level {flag.o}: {Color.ORANGE}{CFG["opt-level"]}{Color.END}")
  print(f"{Ico.GAP} Log level: {Color.BLUE}{xn.ReplaceStart(CFG["log-level"], "LOG_LEVEL_", "")}{Color.END}")
  print(f"{Ico.GAP} System frequency clock: {Color.CYAN}{CFG["freq"]}{Color.END}Hz")
  print(f"{Ico.GAP} Last modification: {Color.CYAN}{utils.LastModification(PATH["pro"])}{Color.END}")
  sys.exit(0)

#------------------------------------------------------------------------------

if CFG["framework-version"] not in VERSIONS:
  print(f"{Ico.ERR} Wersja framework'a {Color.MAGENTA}{CFG['framework-version']}{Color.END} nie istnieje")
  print(f"{Ico.RUN} Sprawdź listę dostępnych wersji za pomocą flagi {flag.fv}")
  sys.exit(1)

PATH["fw"] = xn.FixPath(PATH["framework"] + "/" + CFG["framework-version"])
utils.GitCloneMissing("https://github.com/OpenCPLC/Framework", PATH["fw"], CFG["framework-version"], args.yes)

#------------------------------------------------------------------------------

print(f"{Ico.INF} Projekt {Color.TEAL}{CFG["name"]}{Color.END} na wersji framework'a {Color.BLUE}{CFG["framework-version"]}{Color.END}")

xn.DIR.Create(PATH["pro"])
if not xn.FILE.Exists(PATH["pro"] + "/main.c"): # Utworzenie pliku `main.c`, jeśli nie istnieje
  main_c = sf.main_c
  include = "opencplc.h"
  if CFG["board"] is None: main_c = sf.main_none_c
  elif CFG["board"] not in ["uno", "dio", "aio", "eco"]: include = f"opencplc-{CFG["board"]}.h"
  utils.CreateFile("main.c", main_c, PATH["pro"], {
    "${FAMILY}": CFG["family"],
    "${INCLUDE}": include
  })
if not xn.FILE.Exists(PATH["pro"] + "/main.h"): # Utworzenie pliku `main.h`, jeśli nie istnieje
  utils.CreateFile("main.h", sf.main_h, PATH["pro"], {
    "${NAME}": CFG["name"],
    "${DATE}": datetime.now().strftime("%Y-%m-%d"),
    "${BOARD}": "NONE" if  CFG["board"] is None else CFG["board"].upper(),
    "${CHIP}": CFG["chip"].upper(),
    "${FRAMEWORK_VERSION}": CFG["framework-version"],            
    "${OPT_LEVEL}": CFG["opt-level"],
    "${USER_MEMORY}": CFG["user-memory"],
    "${LOG_LEVEL}": CFG["log-level"],
    "${FREQ}": CFG["freq"],
  })

#------------------------------------------------------------------------------

PATH["inc"] = xn.FixPath(PATH["fw"] + "/inc")
PATH["lib"] = xn.FixPath(PATH["fw"] + "/lib")
PATH["plc"] = xn.FixPath(PATH["fw"] + "/plc")
PATH["pro"] = xn.FixPath(PATH["pro"])

xn.DIR.Create(PATH["inc"])
xn.DIR.Create(PATH["lib"])
if CFG["board"] is not None: xn.DIR.Create(PATH["plc"])

drop = xn.FILE.Remove("flash.ld")
PATH["ld"] = utils.CreateFile("flash.ld", sf.flash_ld, "./", {
  "${FLASH}": CFG["flash"],
  "${RAM}": CFG["ram"]
}, rewrite=drop)

inc = utils.FilesList(PATH["inc"], ".c")
lib = utils.FilesList(PATH["lib"], ".c")
plc = utils.FilesList(PATH["plc"], ".c") if CFG["board"] is not None else {}
scr = utils.FilesList(PATH["pro"], ".c")

c_sources = {**inc, **lib, **plc, **scr}
C_SOURCES = ""
for folder, files in c_sources.items():
  folder:str = folder.replace("\\", "/").lstrip("./")
  for file in files:
    file:str = file.replace("\\", "/").lstrip("./")
    if folder == f"{PATH["plc"]}/brd" and file != f"{PATH["plc"]}/brd/opencplc-" + CFG["board"] + ".c": continue
    file = xn.ReplaceStart(file, PATH["fw"], "$(FW)")
    file = xn.ReplaceStart(file, PATH["pro"], "$(PRO)")
    if utils.LastLineLen(C_SOURCES) > 80: C_SOURCES += "\\\n"
    C_SOURCES += file.replace("\\", "/").lstrip("./") + " "
C_SOURCES = C_SOURCES.rstrip(" ")

inc = utils.FilesList(PATH["inc"], ".s")
lib = utils.FilesList(PATH["lib"], ".s")
plc = utils.FilesList(PATH["plc"], ".s") if CFG["board"] is not None else {}
scr = utils.FilesList(PATH["pro"], ".s")
asm_sources = {**inc, **lib, **plc, **scr}
ASM_SOURCES = ""
for folder, files in asm_sources.items():
  for file in files:
    file:str = xn.ReplaceStart(file, PATH["fw"], "$(FW)")
    file = xn.ReplaceStart(file, PATH["pro"], "$(PRO)")
    if utils.LastLineLen(ASM_SOURCES) > 80: ASM_SOURCES += "\\\n"
    ASM_SOURCES += file.replace("\\", "/").lstrip("./") + " "
ASM_SOURCES = ASM_SOURCES.rstrip(" ")

inc = utils.FilesList(PATH["inc"], ".h")
lib = utils.FilesList(PATH["lib"], ".h")
plc = utils.FilesList(PATH["plc"], ".h") if CFG["board"] is not None else {}
scr = utils.FilesList(PATH["pro"], ".h")
c_includes = {**inc, **lib, **plc, **scr}
C_INCLUDES = ""
for folder, files in c_includes.items():
  folder:str = xn.ReplaceStart(folder, PATH["fw"], "$(FW)")
  folder = xn.ReplaceStart(folder, PATH["pro"], "$(PRO)")
  if utils.LastLineLen(C_INCLUDES) > 80: C_INCLUDES += "\\\n"
  C_INCLUDES += "-I" + folder.replace("\\", "/").lstrip("./") + " "
C_INCLUDES = C_INCLUDES.rstrip(" ")

PATH["fw-workspace"] = xn.LocalPath(PATH["fw"], prefix="${workspaceFolder}/")
PATH["pro-workspace"] = xn.LocalPath(PATH["pro"], prefix="${workspaceFolder}/")
PATH["fw"] = xn.LocalPath(PATH["fw"])
PATH["pro"] = xn.LocalPath(PATH["pro"])
PATH["build"] = xn.LocalPath(PATH["build"])
PATH["ld"] = xn.LocalPath(PATH["ld"])

if wizard_config["pwsh"]:
  sf.makefile = utils.SwapCommentLines(sf.makefile)

drop = xn.FILE.Remove("makefile")
utils.CreateFile("makefile", sf.makefile, "./", {
  "${NAME}": args.name,
  "${FRAMEWORK_PATH}": PATH["fw"].replace("/", "\\\\"),
  "${PROJECT_PATH}": PATH["pro"].replace("/", "\\\\"),
  "${BUILD_PATH}": PATH["build"].replace("/", "\\\\"),
  "${FAMILY}": CFG["family"],
  "${BOARD}": "NONE" if  CFG["board"] is None else CFG["board"].upper(),
  "${OPT_LEVEL}": CFG["opt-level"],
  "${C_SOURCES}": C_SOURCES,
  "${ASM_SOURCES}": ASM_SOURCES,
  "${C_INCLUDES}": C_INCLUDES,
  "${LD_FILE}": PATH["ld"].replace("/", "\\\\"),
  "${GCC_PATH}": "", # system-path
  "${OPENOCD_PATH}": "" # system-path
}, rewrite=drop)

xn.DIR.Create("./.vscode")

drop = xn.FILE.Remove(".vscode/c_cpp_properties.json")
utils.CreateFile("c_cpp_properties.json", sf.properties_json, ".vscode", {
    "${NAME}": args.name,
    "${FRAMEWORK_PATH}": PATH["fw-workspace"] ,
    "${PROJECT_PATH}": PATH["pro-workspace"],
    "${FAMILY}": CFG["family"],
    "${BOARD}": "NONE" if  CFG["board"] is None else CFG["board"].upper()
  },
  "/plc/**" if CFG["board"] is None else "", rewrite=drop
)

drop = xn.FILE.Remove(".vscode/launch.json")
utils.CreateFile("launch.json", sf.launch_json, ".vscode", {
  "${NAME}": args.name,
  "${FRAMEWORK_PATH}": PATH["fw"],
  "${PROJECT_PATH}": PATH["pro"],
  "${BUILD_PATH}": PATH["build"],
  "${DEVICE}": CFG["device"],
  "${SVD}": CFG["svd"]
}, rewrite=drop)

if not xn.FILE.Exists(".vscode/tasks.json"): utils.CreateFile("tasks.json", sf.tasks_json, ".vscode")
if not xn.FILE.Exists(".vscode/settings.json"): utils.CreateFile("settings.json", sf.settings_json, ".vscode")
if not xn.FILE.Exists(".vscode/extensions.json"): utils.CreateFile("extensions.json", sf.extensions_json, ".vscode")
