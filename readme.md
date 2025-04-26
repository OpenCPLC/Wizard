## 🔮 Wizard

**Wizard** jest aplikacją konsolową usprawniającą pracę z **OpenCPLC**, którego zadaniem jest dostosowanie środowiska pracy tak, aby 👨‍💻programista-automatyk mógł skupić się na tworzeniu aplikacji, a nie walce z konfiguracją ekosystemu i kompilacją programu. Pobierz **`wizard.exe`** z 🚀[Releases](https://github.com/OpenCPLC/Wizard/releases) i umieść go w wybranym folderze, który będzie pełnił rolę przestrzeni roboczej _(workspace)_. Następnie otwórz konsolę [CMD](#-console) i wpisz:

```bash
./wizard --new <project_name> -b <board>
./wizard --new blinky -b Uno
```

Wówczas w [lokalizacji z projektami](#️-config) `${projects}` tworzony jest katalog _(lub drzewo katalogów)_ zgodny z przekazaną nazwą `<project_name>`. Powstają w nim dwa pliki: `main.c` i `main.h`, które stanowią minimalny zestaw plików projektu. Nie można ich usuwać ani przenosić do podkatalogów.

Gdy będziemy mieli więcej projektów, będziemy mogli swobodnie przełączać się między nimi.

```bash
./wizard <project_name>
./wizard blinky
```

Podczas tworzenia nowego projektu lub przełączania się na istniejący, generowane są na nowo wszystkie pliki _(`makefile`, `flash.ld`, ...)_ niezbędne do poprawnego przeprowadzenia procesu kompilacji, czyli przekształcenia całości _(plików projektu i framework'a: `.c`, `.h`, `.s`)_ w pliki wsadowe `.bin`/`.hex`, które można wgrać do sterownika jako działający program.

W przypadku zmiany wartości konfiguracyjnych `PRO_x` w pliku **`main.h`** lub modyfikacji **struktury projektu**, obejmującej:

- dodawanie nowych plików,
- przenoszenie plików
- usuwanie plików,
- zmiany nazw plików,

niezbędne jest ponowne załadowanie projektu. Jeśli projekt jest już aktywny, nie trzeba podawać jego nazwy `-r --reload`:

```bash
./wizard <project_name>
./wizard -r
```

Tutaj _(upraszczając)_ kończy się zadanie programu `wizard.exe`, a dalsza praca przebiega tak samo jak w typowym projekcie **embedded systems**, czyli przy użyciu [**✨Make**](#-make)

## ✨ Make

Jeżeli mamy poprawnie przygotowaną konfigurację projektu oraz plik `makefile` wygenerowany za pomocą programu 🔮**Wizard**, to aby zbudować i wgrać program na sterownik PLC, wystarczy otworzyć konsolę w przestrzeni roboczej _(workspace)_ i wpisać:

```bash
make build # build c projekt to binary program
make flash # move binary fole to PLC (micorcotroler) memeory
# lub
make run   # run = build + flash
```

Plik `makefile` udostępnia również kilka innych funkcji. Oto pełna lista:

- **`make build`** lub samo **`make`**: Buduje projekt w języku C do postaci plików wsadowych `.bin`, `.hex`, `.elf`
- **`make flash`**: Wgrywa plik wsadowy programu do pamięci sterownika PLC _(mikrokontrolera)_
- **`make run`**: Wykonuje `make build`, a następnie `make flash`
- **`make clean`** lub `make clr`: Usuwa zbudowane pliki wsadowe dla aktywnego projektu
- `make clean_all` lub `make clr_all`:: Usuwa zbudowane pliki wsadowe dla wszystkich projektów
- **`make erase`**: Całkowicie czyści pamięć mikrokontrolera _(**erase** full chip)_

### ⚙️ Config

Podczas pierwszego uruchomienia 🧙🏼‍♂️Wizard'a tworzony jest plik konfiguracyjny **`wizard.json`**. Zawiera on:

- **`version`**: Domyślna wersja oprogramowania. Wymuszana jest jej instlacja. Zastępuje nieokreśloną wersję `-f --framework`.
- `paths`: Lista ścieżek _(względnych)_
  - `projects`: Główny katalog z projektami. Nowe projekty tworzone są w tym miejscu. Można też skopiować projekt ręcznie. Wszystkie projekty są wykrywane automatycznie. Nazwą projektu jest dalsza część tej ścieżki.
  - `framework`: Katalog zawierający wszystkie wersje frameworka OpenCPLC. W jego wnętrzu tworzone są podkatalogi odpowiadające wersjom w formacie `major.minor.patch`, `develop` lub `main`. Każdy z nich zawiera pliki odpowiedniej wersji frameworka. Pobierane będą jedynie niezbędne wersje.
  - `build`: Katalog z zbudowanymi aplikacjami
- `default`: Lista domyślnych wartości _(`chip`, `user-memory`, `opt-level`)_ dla nieprzekazanych parametrów podczas tworzenia nowego projektu 
- **`pwsh`**: Ustawienie tego parametru na `true` wymusza przygotowanie pliku `makefile` w wersji dla powłoki **PowerShell**.  Dla wartości `false` zostanie przygotowana wersja dla powłoki **Bash**.
- `available-versions`: Lista wszystkich dostępnych wersji framework'a. Jej zawartość jest ustawiana automatycznie.

### 🤔 How works?

W pierwszej kolejności **Wizard** zainstaluje **GNU Arm Embedded Toolchain**, **OpenOCD**, **Make**, klienta **Git** oraz ustawi odpowiednio zmienne systemowe, jeżeli aplikacje nie są widoczne w systemie z poziomu konsoli. Jeżeli nie chcemy, aby ktoś grzebał w naszym systemie, możemy przygotować sobie [konfiguracje ręcznie](self-install.md). Gdy 🪄**Wizard** zainstaluje brakujące aplikacje, poprosi o zresetowanie konsoli, ponieważ zmienne systemowe są ładowane podczas jej uruchamiania, a w procesie instlacji zostały dodane nowe.

Następnie, w razie konieczności, skopiuje framework OpenCPLC z [repozytorium](https://github.com/OpenCPLC/Framework) do folderu `${framework}` podanego w pliku konfiguracyjnym `wizard.json`. Zostanie sklonowana wersja z pliku konfiguracyjnego lub wskazana za pomocą `-f --framework`:

```bash
./wizard <project_name> --new -f 1.0.2
./wizard <project_name> --new -f develop
```

W przypadku przełączania się na istniejący projekt, flaga ta jest ignorowana, a projekt korzysta z wersji frameworka zapisanej w pliku `main.h` należącym do projektu. Wersja ta jest określona za pomocą definicji `#define` `PRO_VERSION`.

Główną funkcją **Wizard**'a jest przygotowanie plików niezbędnych do pracy z wybranym projektem:

- `flash.ld`: definiuje rozkład pamięci RAM i FLASH mikrokontrolera _(nadpisuje)_
- `makefile`: Zawiera reguły budowania, czyszczenia i flashowania projektu _(nadpisuje)_
- `c_cpp_properties.json`: ustawia ścieżki do nagłówków i konfigurację IntelliSense w VS Code _(nadpisuje)_
- `launch.json`: konfiguruje debugowanie w VSCode _(nadpisuje)_
- `tasks.json`: opisuje zadania takie jak kompilacja czy flashowanie
- `settings.json`: ustawia lokalne preferencje edytora dla projektu
- `extensions.json`: sugeruje przydatne rozszerzenia do VSCode

Istnieje także całkiem sporo funkcji pomocniczych, do których dostęp uzyskuje się za pomocą sprytnego wykorzystania [**🚩flag**](#-flags).

### 🚩 Flags

Oprócz podstawowych flag opisanych powyżej, istnieje jeszcze kilka, które mogą pozostać niezmienione, ale warto znać ich istnienie. Poniżej znajduje się lista wszystkich flag:

- **`name`**: Nazwa projektu. Parametr domyślny przekazywany jako pierwszy. Będzie również stanowić ścieżkę do projektu: `${projects}/name`, a końcowe pliki wsadowe _(`.bin`, `.hex`, `.elf`)_ będą z nią ściśle skorelowane.
- `-s --sample`: Wczytuje przykład demonstracyjny o wskazanej nazwie. 
- `-r --reload`: Pobiera nazwę projektu oraz określa, czy jest to przykład, na podstawie wcześniej wygenerowanego pliku `makefile`, a następnie generuje pliki projektowe na nowo. Wówczas nie jest wymagane podawania nazwy **`name`**
- `-g --get`: Pobiera projekt z serwisu GIT _(**GitHub**, **GitLab**, ...)_ lub zdalnego pliku ZIP i dodaje go jako nowy. Jako drugi argument _(pierwszym jest link)_ można przekazać referencję _(`branch`, `tag`)_. Jeśli nie została określona nazwa projektu **`name`**, zostanie podjęta próba odczytania jej z pola `@name` z pliku `main.h`.
- `-d --delete`: Usuwa wybrany projekt ze wskazaną nazwą **`name`**.
- `-f --framework`: Wersja framework'a. Jeśli nie zostanie podana, zostanie odczytana z pola `version` w pliku konfiguracyjnym `wizard.json`. Format: `<major>.
- `-fl --framework_list`: Wyświetla wszystkie dostępne wersje frameworka OpenCPLC.
- `-b --board`: Model sterownika PLC dla nowego projektu. Oficjalnie wspierana konstrukcja `Uno`, `DIO`, `AIO`, `Eco`, `None` dla pracy z czystym mikrokontrolerem lub inna nazwa własna.
- `-c --chip`: Wykorzystywany mikrokontroler: `STM32G081`, `STM32G0C1` w nowym projekcie. Dla oficjalnie wspieranych konstrukcji zostanie dobrany automatycznie, więc lepiej go nie podawać. Wybór wpływa na dostępną ilość pamięci FLASH[kB] i RAM[kB] na płytce oraz na dodawane pliki nagłówkowe.
- `-m --user_memory`: Ilość zarezerwowanej pamięci FLASH[kB] na konfigurację i EEPROM w aplikacji. Powoduje zmniejszenie dostępnej pamięci na program w pliku linkera `flash.ld`.
- `-o --opt`: Poziom optymalizacji kodu dla kompilacji: `O0`, `Og`, `O1` _(default: `Og`)_. Poziomy optymalizacji `O2`, `O3` są niedozwolone!
- `-l --list`: Wyświetla listę istniejących projektów lub przykładów, gdy aktywna jest flaga `-s --sample`.
- `-i --info`: Zwraca podstawowe informacje o wskazanym lub aktywnym projekcie.
- `-a --assets`: Pobiera materiały pomocnicze przydatne podczas projektowania _(dokumentacja, diagramy)_. Jako wartość można przekazać nazwę folderu, w którym paczka zostanie umieszczona.
- `-u --update`: Sprawdza dostępność aktualizacji i aktualizuje program 🪄Wizard.  
- `-v --version`: Wyświetla wersję programu 🔮Wizard oraz link do repozytorium.

🗑️Usuwanie i 💾kopiowanie projektów można oczywiście wykonywać bezpośrednio z poziomu systemu operacyjnego.
Każdy projekt przechowuje wszystkie niezbędne informacje o sobie, a jego obecność jest automatycznie wykrywana podczas uruchamiania programu.

### 📟 Console

Programy 🧙🏼‍♂️Wizard oraz ✨Make są programami uruchamianymi z konsoli CMD. Stanowią niezbędnik do pracy z OpenCPLC.

Konsola systemowa jest dostępna w wielu aplikacjach, takich jak **Command Prompt**, **PowerShell**, [**GIT Bash**](https://git-scm.com/downloads), a nawet terminal w [**VSCode**](https://code.visualstudio.com/). Gdy wywołanie w konsoli zwróci błąd, prawdopodobnie nie została otwarta w przestrzeni roboczej _(workspace)_ i nie widzi aplikacji `wizard.exe`. Możesz zamknąć konsolę i otworzyć ją w odpowiednim folderze lub przejść ręcznie, używając komendy `cd`.