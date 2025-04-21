import signal, sys, argparse
import xaeian as xn, utils
from datetime import datetime

class Ico(xn.IcoText): pass
class Color(xn.Color): pass

VER = "0.0.2"

def HandleSigint(signum, frame):
  print(f"{Ico.WRN} Zamykanie aplikacji {Color.GREY}(Ctrl+C){Color.END}...")
  sys.exit(0)

signal.signal(signal.SIGINT, HandleSigint)

#------------------------------------------------------------------------------

xn.FIX_PATH = True
xn.ONEFILE_PACK = True

class sf(): # startup files
  wizard_json_dict = xn.JSON.Load("files/wizard.json")
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

#------------------------------------------------------------------------------

wizard_config = xn.JSON.Load("wizard.json") or sf.wizard_json_dict
missing = xn.DICT.FindMissingKeys(sf.wizard_json_dict, wizard_config)
if missing:
  print(f"{Ico.ERR} W pliku konfiguracyjnym {Color.ORANGE}wizard.json{Color.END} nie określono {Color.BLUE}{missing[0]}{Color.END}")
  sys.exit(1)

url_framework = "https://github.com/OpenCPLC/Framework"
url_wizard = "https://github.com/OpenCPLC/Wizard"

versions = utils.GitGetRef(url_framework, "--ref", use_git=True)
if versions: wizard_config["versions"] = versions
else:
  print(f"{Ico.WRN} Brak dostępu do internetu lub serwis {Color.BLUE}GitHub{Color.END} nie odpowiada")
  if "versions" not in wizard_config:
    print(f"{Ico.ERR} Pierwsze uruchomienie nie powiedzie się bez dostępu do zasobów zdalnych")
    sys.exit(1)
  wizard_config["versions"] = wizard_config["versions"]

xn.JSON.SavePretty("wizard.json", wizard_config)
wizard_config["version"] = utils.VersionReal(wizard_config["version"], wizard_config["versions"][0])

#------------------------------------------------------------------------------

parser = argparse.ArgumentParser(description="OpenPLC project wizard")
parser.add_argument("name", type=str, nargs="?", help="Nazwa projektu", default="")
parser.add_argument("-n", "--new", type=str, nargs="?", help="Nowy projekt", const=True)
parser.add_argument("-s", "--sample", type=str, nargs="?", help="Przykład demonstracyjny o wskazanej nazwie", const=True)
parser.add_argument("-r", "--reload", action="store_true", help="Przeładowanie aktywnego projektu. Nie wymaga podawania nazwy {name}", default=False)
parser.add_argument("-g", "--get", nargs='+', metavar=("URL", "REF"), help="Pobieranie projektu z GIT'a lub zdalnego pliku ZIP", default=[])
# parser.add_argument("-d", "--delete", type=str, nargs="?", help="Usuwa wybrany projekt", const=True)
parser.add_argument("-f", "--framework", type=str, help=f"Wersja framework'a OpenCPLC, format: <major>.<minor>.<patch> lub (latest, develop, main)", default="")
parser.add_argument("-fl", "--framework_list", action="store_true", help="Wszystkie dostępne wersje framework'a OpenCPLC", default=False)
parser.add_argument("-b", "--board", type=str, help="Model sterownika PLC (Uno, Dio, Aio, Eco, None, ...)", default="")
parser.add_argument("-c", "--chip", type=str, help="Wykorzystywany mikrokontroler (STM32G081, STM32G0C1). Wybór wpływa na dostępną ilość pamięci FLASH[kB] i RAM[kB] na płytce", default="")
parser.add_argument("-m", "--user_memory", type=int, help="Ilość zarezerwowanej pamięci FLASH[kB] na konfigurację i EEPROM w aplikacji", default=0)
parser.add_argument("-o", "--opt-level", type=str, help="Poziom optymalizacji kompilacji (O0, Og, O1)", default="Og")
parser.add_argument("-l", "--list", action="store_true", help="Lista istniejących projektów (lub przykładów z flagą -s)", default=False)
parser.add_argument("-i", "--info", action="store_true", help="Podstawowe informacje o projekcie", default=False)
parser.add_argument("-u", "--update", type=str, help="Aktualizacja program Wizard (do najnowszej wersji lub wskazanej)", default="")
parser.add_argument("-v", "--version", action="store_true", help="Wersję programu oraz link do repozytorium", default=False)
parser.add_argument("-y", "--yes", action="store_true", help="Automatycznie potwierdza wszystkie operacje", default=False)
parser.add_argument("-hl", "--hash_list", nargs="+", help="[Hash] Lista tagów do za-hash'owania")
parser.add_argument("-ht", "--hash_title", type=str, help="[Hash] Tytół dla enum'a hash'y, który zostanie utworzony z listy tagów", default="")
args = parser.parse_args()

class flag():
  n = f"{Color.YELLOW}-n{Color.END} {Color.GREY}--new{Color.END}"
  s = f"{Color.YELLOW}-s{Color.END} {Color.GREY}--sample{Color.END}"
  r = f"{Color.YELLOW}-r{Color.END} {Color.GREY}--reload{Color.END}"
  g = f"{Color.YELLOW}-g{Color.END} {Color.GREY}--get{Color.END}"
  f = f"{Color.YELLOW}-f{Color.END} {Color.GREY}--framework{Color.END}"
  fl = f"{Color.YELLOW}-fl{Color.END} {Color.GREY}--framework_list{Color.END}"
  b = f"{Color.YELLOW}-b{Color.END} {Color.GREY}--board{Color.END}"
  c = f"{Color.YELLOW}-c{Color.END} {Color.GREY}--chip{Color.END}"
  m = f"{Color.YELLOW}-m{Color.END} {Color.GREY}--user-memory{Color.END}"
  o = f"{Color.YELLOW}-o{Color.END} {Color.GREY}--opt-level{Color.END}"

#------------------------------------------------------------------------------ Print

exit_flag = False

if args.version:
  print(f"OpenCPLC Wizard {Color.BLUE}{VER}{Color.END}")
  print(utils.ColorUrl("https://github.com/OpenCPLC/Wizard"))
  exit_flag = True

if args.framework_list:
  msg = f"Framework Versions: "
  latest = f" {Color.GREY}(latest){Color.END}"
  color = Color.BLUE
  for ver in wizard_config["versions"]:
    msg += f"{color}{ver}{Color.END}{latest}, "
    color = Color.CYAN
    latest = ""
  msg = msg.rstrip(", ")
  print(msg)
  exit_flag = True

if args.hash_list:
  c_code = utils.CCodeEnum(args.hash_list, args.hash_title)
  print(c_code)
  exit_flag = True

if args.update:
  new = True if args.update in ["last", "latest"] else False
  versions = utils.GitGetRef(url_wizard, "--tags", use_git=True)
  if not versions:
    print(f"{Ico.ERR} Brak dostępu do internetu lub serwis {Color.BLUE}GitHub{Color.END} nie odpowiada")
    sys.exit(1)
  args.update = utils.VersionReal(args.update, versions[0])
  if args.update != VER:
    print(f"{Ico.INF} OpenCPLC Wizard jest zainstalowany w wersji {Color.ORANGE}{VER}{Color.END}")
    msg = f"{'Najnowsza dostępna' if new else 'Wskazana'} wersja to {Color.BLUE}{args.update}{Color.END}."
    msg += f"Wymagana {"aktualizacja" if new else "podmiana"}"
    print(f"{Ico.INF} {msg}")
    utils.Install("wizard.exe", f"https://github.com/OpenCPLC/Wizard/releases/download/{args.update}", "./", args.yes, False)
  else:
    print(f"{Ico.OK} OpenCPLC Wizard jest już zainstalowany w {'aktualnej' if new else 'określonej'} wersji {Color.BLUE}{VER}{Color.END}")
  exit_flag = True

if exit_flag: sys.exit(0)

#------------------------------------------------------------------------------

used = [flag.n if args.new else None, flag.r if args.reload else None, flag.s if args.sample else None, flag.g if args.get else None]
used = [fg for fg in used if fg]

if len(used) > 1:
  print(f"{Ico.ERR} Flagi {', '.join(used)} nie mogą być użyte jednocześnie")
  sys.exit(1)

args.name, args.new = utils.AssignName(args.name, args.new, flag.n)
args.name, args.sample = utils.AssignName(args.name, args.sample, flag.s)
args.name, args.reload = utils.AssignName(args.name, args.reload, flag.r) 

#------------------------------------------------------------------------------ Install

utils.InstallMissingAddPath("Git", "git", None, args.yes, "2.47.1")
utils.InstallMissingAddPath("ArmGCC", "arm-none-eabi-gcc", "ARMGCC", args.yes, "14.2.1")
utils.InstallMissingAddPath("OpenOCD", "openocd", None, args.yes, "0.12.0")
utils.InstallMissingAddPath("Make", "make", None, args.yes, "4.4.1")

if utils.RESET_CONSOLE:
  print(f"{Ico.DOC} Zresetuj konsolę systemową po zakończeniu pracy {Color.YELLOW}wizard.exe{Color.END}")
  print(f"{Ico.DOC} Spowoduje to załadowanie nowo dodanych ścieżek systemowych")
  sys.exit(0)

#------------------------------------------------------------------------------ Load

CFG = { "framework-version": args.framework or wizard_config["version"] }
PATH = wizard_config["paths"]
PATH["fw"] = PATH["framework"] + "/" + CFG["framework-version"]
PATH["samples"] = PATH["fw"] + "/res/samples"
utils.FrameworkVersionCheck(CFG["framework-version"], wizard_config["versions"], f"{Ico.RUN} Sprawdź listę dostępnych wersji za pomocą flagi {flag.fl}")
utils.GitCloneMissing(url_framework, PATH["fw"], CFG["framework-version"], args.yes)

make_info = None
if xn.FILE.Exists("makefile"):
  lines = xn.FILE.LoadLines("makefile")
  lines = utils.LinesClear(lines, "#")
  make_info = utils.GetVars(lines, ["NAME", "FW", "PRO"])

if args.get:
  if args.sample:
    args.sample = False
    print(f"{Ico.WRN} Wybór przykładów demonstracyjnych {flag.s} został zignorowany")
  url = args.get[0]
  ref = args.get[1] if len(args.get) > 1 else None
  args.name = utils.ProjectRemote(url, PATH["projects"], ref, args.name)

PRO = utils.GetProjectList(PATH["projects"])
SAM = utils.GetProjectList(PATH["samples"])

#------------------------------------------------------------------------------

if args.list or args.name.isdigit():
  LIST = SAM if args.sample else PRO
  if not LIST:
    if args.sample: print(f"{Ico.ERR} Nie znaleziono żadnych przykładów demonstracyjnych")
    else:
      print(f"{Ico.WRN} Nie znaleziono żadnych {"przykładów demonstracyjnych" if args.sample else "projektów"}")
      print(f"{Ico.INF} Utwórz nowy projekt za pomocą flagi {flag.n}")
    sys.exit(1)
  i = 1
  for name, path in LIST.items():
    if args.list:
      path = xn.LocalPath(path)
      path = xn.ReplaceEnd(path, name, "")
      nbr = (Color.ORANGE if args.sample else Color.YELLOW) + str(i).ljust(3, " ") + Color.END
      print(f"{nbr} {Color.GREY}{path}{Color.END}{Color.CYAN if args.sample else Color.BLUE}{name}{Color.END}")
    else:
      if int(args.name) == i:
        args.name = name
        break
    i += 1
  if args.list: sys.exit(0)

#------------------------------------------------------------------------------

if not args.name and not args.reload and not args.info:
  print(f"{Ico.ERR} Nazwa {Color.YELLOW}name{Color.END} projektu nie została określona")
  print(f"{Ico.INF} Dotyczy to zarówno przełączenia się na istniejący projekt, jak i tworzenia nowego za pomocą flagi {flag.n}")
  print(f"{Ico.RUN} Gdy chcesz przeładować aktywny projekt, dodaj do wywołania flagę {flag.r}")
  sys.exit(1)

if not args.name and (args.reload or args.info):
  if make_info is None:
    print(f"{Ico.ERR} Nie znaleziono pliku {Color.ORANGE}makefile{Color.END}, który jest wymagany do przeładowania projektu")
    print(f"{Ico.INF} W takim przypadku należy podać jego nazwę jako argument domyślny")
    sys.exit(1)
  if not make_info:
    print(f"{Ico.ERR} Plik {Color.ORANGE}makefile{Color.END} zawiera niezdefiniowane zmienne")
    print(f"{Ico.INF} W takim przypadku nie możesz zkorzystać z oipcji ")
    sys.exit(1)
  if make_info["PRO"].startswith(make_info["FW"]): args.sample = True
  args.name = make_info["NAME"]

CFG["name"] = args.name
PATH["pro"] = PATH["projects"] + "/" + CFG["name"]

#------------------------------------------------------------------------------

noun1, noun2 = ("Przykład demonstracyjny", "przykładu demonstracyjnego") if args.sample else ("Projekt", "projektu")

if args.new:
  if CFG["name"].lower() in (name.lower() for name in PRO.keys()):
    print(f"{Ico.ERR} Projekt {Color.MAGENTA}{CFG["name"]}{Color.END} już istnieje")
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
  CFG["project-version"] = args.framework or wizard_config["version"]
  if args.user_memory: CFG["user-memory"] = args.user_memory
  elif CFG["board"] in ["uno", "dio", "aio"]: CFG["user-memory"] = 20
  elif CFG["board"] in ["eco"]: CFG["user-memory"] = 12
  else: CFG["user-memory"] = wizard_config["default"]["user-memory"]
  CFG["opt-level"] = args.opt_level or wizard_config["default"]["opt-level"]
  CFG["log-level"] = "LOG_LEVEL_INF"
  CFG["freq"] = 59904000 if CFG["board"] in ["uno", "dio", "aio"] else 64000000
else:
  if args.sample:
    PRO = SAM
    msg = f"Sprawdz listę przykładów w katalogu {Color.GREY}{PATH["samples"]}{Color.END}"
  else: msg = f"Możesz spróbować utworzyć projekt, dodając flagę {flag.n} podczas wywołania"
  if CFG["name"].lower() not in (name.lower() for name in PRO.keys()):
    print(f"{Ico.ERR} {noun1} o nazwie {Color.MAGENTA}{CFG["name"]}{Color.END} nie został znaleziony")
    print(f"{Ico.RUN} {msg}")
    sys.exit(1)
  lines = xn.FILE.LoadLines(PRO[CFG["name"]] + "/main.h")
  lines = utils.LinesClear(lines, "//")
  info1 = utils.GetVars(lines, ["PRO_BOARD", "PRO_CHIP"], "_", "#define")
  info2 = utils.GetVars(lines, ["PRO_VERSION", "PRO_OPT_LEVEL", "PRO_USER_MEMORY_KB", "LOG_LEVEL", "SYS_CLOCK_FREQ"], " ", "#define")
  if not info1 or not info2:
    print(f"{Ico.ERR} Plik {Color.ORANGE}main.h{Color.END} z katalogu {Color.GREY}{PRO[CFG["name"]]}{Color.END} zawiera niezdefiniowane definicje")
    sys.exit(1)
  info = info1 | info2
  CFG["board"] = info["PRO_BOARD"]  
  CFG["chip"] = info["PRO_CHIP"]
  CFG["project-version"] = info["PRO_VERSION"]
  CFG["user-memory"] = int(info["PRO_USER_MEMORY_KB"])
  CFG["opt-level"] = info["PRO_OPT_LEVEL"]
  CFG["log-level"] = info["LOG_LEVEL"]
  CFG["freq"] = info["SYS_CLOCK_FREQ"]
  utils.FrameworkVersionCheck(CFG["project-version"], wizard_config["versions"],
    f"{Ico.ERR} Definicja {Color.BLUE}PRO_VERSION{Color.END} z pliku {Color.ORANGE}main.h{Color.END} jest nie poprawna"
  )
  fw = PATH["framework"] + "/" + CFG["project-version"]
  if args.sample:
    CFG["framework-version"] = CFG["project-version"]
    PATH["pro"] = PATH["fw"] + "/res/samples/" + CFG["name"]
  elif not utils.GitCloneMissing(url_framework, fw, CFG["project-version"], args.yes, False):
    mag = f"Projekt {Color.MAGENTA}{CFG["name"]}{Color.END} jest w innej wersji {Color.GREY}({CFG['project-version']}){Color.END} "
    mag += f"niż framework {Color.GREY}({CFG['framework-version']}){Color.END}"
    print(f"{Ico.WRN} {mag}")
    print(f"{Ico.WRN} Może to uniemożliwić kompilację lub powodować niepoprawną pracę programu")
  msg = f"jest ignrowana podczas ładowania istniejącgo {noun2}"
  if args.board: print(f"{Ico.WRN} Flaga {flag.b} {msg}")
  if args.chip: print(f"{Ico.WRN} Flaga {flag.c} {msg}")
  if args.user_memory: print(f"{Ico.WRN} Flaga {flag.m} {msg}")

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

path = xn.LocalPath(PATH["pro"])
path = xn.ReplaceEnd(path, CFG["name"], "")

msg = f"{Color.GREY}{path}{Color.TEAL}{CFG["name"]}{Color.END}"

if args.info:
  sample_msg = f" {Color.RED}(sample){Color.END}" if args.sample else ""
  print(f"{Ico.INF} Project: {msg}{sample_msg}")
  print(f"{Ico.GAP} Board {flag.b}: {Color.BLUE}{str(CFG["board"]).capitalize()}{Color.END}")
  print(f"{Ico.GAP} Chip {flag.c}: {Color.ORANGE}{CFG["chip"]}{Color.END}")
  print(f"{Ico.GAP} Project version: {Color.MAGENTA}{CFG["project-version"]}{Color.END}")
  print(f"{Ico.GAP} Framework version: {Color.MAGENTA}{CFG["framework-version"]}{Color.END}")
  print(f"{Ico.GAP} User memory {flag.m}: {Color.CYAN}{CFG["user-memory"]}{Color.END}kB")
  print(f"{Ico.GAP} Optimization level {flag.o}: {Color.ORANGE}{CFG["opt-level"]}{Color.END}")
  print(f"{Ico.GAP} Log level: {Color.BLUE}{xn.ReplaceStart(CFG["log-level"], "LOG_LEVEL_", "")}{Color.END}")
  print(f"{Ico.GAP} System frequency clock: {Color.CYAN}{CFG["freq"]}{Color.END}Hz")
  print(f"{Ico.GAP} Last modification: {Color.CYAN}{utils.LastModification(PATH["pro"])}{Color.END}")
  sys.exit(0)

#------------------------------------------------------------------------------

print(f"{Ico.INF} {noun1} {msg} w wersji {Color.BLUE}{CFG["framework-version"]}{Color.END}")

xn.DIR.Create(PATH["pro"])

if not xn.FILE.Exists(PATH["pro"] + "/main.c"): # Utworzenie pliku `main.c`, jeśli nie istnieje
  main_c = sf.main_c
  include = "opencplc.h"
  if CFG["board"] is None: main_c = sf.main_none_c
  elif CFG["board"] not in ["uno", "dio", "aio", "eco"]: include = f"opencplc-{CFG["board"]}.h"
  utils.CreateFile("main.c", main_c, PATH["pro"], {
    "${FAMILY}": CFG["family"],
    "${INCLUDE}": include
  }, color=Color.BLUE)

if not xn.FILE.Exists(PATH["pro"] + "/main.h"): # Utworzenie pliku `main.h`, jeśli nie istnieje
  utils.CreateFile("main.h", sf.main_h, PATH["pro"], {
    "${NAME}": CFG["name"],
    "${DATE}": datetime.now().strftime("%Y-%m-%d"),
    "${BOARD}": str(CFG["board"]).upper(),
    "${CHIP}": CFG["chip"].upper(),
    "${PROJECT_VERSION}": CFG["project-version"],            
    "${OPT_LEVEL}": CFG["opt-level"],
    "${USER_MEMORY}": CFG["user-memory"],
    "${LOG_LEVEL}": CFG["log-level"],
    "${FREQ}": CFG["freq"],
  }, color=Color.BLUE)

#------------------------------------------------------------------------------

PATH["inc"] = xn.FixPath(PATH["fw"] + "/inc")
PATH["lib"] = xn.FixPath(PATH["fw"] + "/lib")
PATH["plc"] = xn.FixPath(PATH["fw"] + "/plc")
PATH["fw"] = xn.FixPath(PATH["fw"])
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
    file = xn.ReplaceStart(file, PATH["pro"], "$(PRO)")
    file = xn.ReplaceStart(file, PATH["fw"], "$(FW)")
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
  "${NAME}": CFG["name"],
  "${PREFIX}": "sample-" if args.sample else "",
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
    "${NAME}": CFG["name"],
    "${FRAMEWORK_PATH}": PATH["fw-workspace"] ,
    "${PROJECT_PATH}": PATH["pro-workspace"],
    "${FAMILY}": CFG["family"],
    "${BOARD}": "NONE" if  CFG["board"] is None else CFG["board"].upper()
  },
  "/plc/**" if CFG["board"] is None else "", rewrite=drop
)

drop = xn.FILE.Remove(".vscode/launch.json")
utils.CreateFile("launch.json", sf.launch_json, ".vscode", {
  "${TARGET}": f"{"sample-" if args.sample else ""}{CFG["name"].replace("/", "-")}",
  "${FRAMEWORK_PATH}": PATH["fw"],
  "${PROJECT_PATH}": PATH["pro"],
  "${BUILD_PATH}": PATH["build"],
  "${DEVICE}": CFG["device"],
  "${SVD}": CFG["svd"]
}, rewrite=drop)

if not xn.FILE.Exists(".vscode/tasks.json"): utils.CreateFile("tasks.json", sf.tasks_json, ".vscode")
if not xn.FILE.Exists(".vscode/settings.json"): utils.CreateFile("settings.json", sf.settings_json, ".vscode")
if not xn.FILE.Exists(".vscode/extensions.json"): utils.CreateFile("extensions.json", sf.extensions_json, ".vscode")

#------------------------------------------------------------------------------
