## 🔮 Wizard

**Wizard** jest aplikacją konsolową usprawniającą pracę z **OpenCPLC**, którego zadaniem jest dostosowanie środowiska pracy tak, aby 👨‍💻programista-automatyk mógł skupić się na tworzeniu aplikacji, a nie walce z konfiguracją ekosystemu i kompilacją programu. Pobierz **`wizard.exe`** z 🚀[Releases](https://github.com/OpenCPLC/Wizard/releases) i umieść go w wybranym folderze, który będzie pełnił rolę przestrzeni roboczej _(workspace)_. Następnie otwórz [konsolę](#-console) i wpisz:

```bash
./wizard.exe --new <project_name> -b <board>
./wizard.exe --new blinky -b Uno
```

Wówczas w [lokalizacji z projektami](#️-config) `${projects}` tworzony jest katalog (lub drzewo katalogów) zgodny z przekazaną nazwą `<project_name>`.  
Powstają w nim dwa pliki: `main.c` i `main.h`, które stanowią minimalny zestaw plików projektu.  Nie można ich usuwać ani przenosić do podkatalogów.

Gdy będziemy mieli więcej projektów, będziemy mogli swobodnie przełączać się między nimi.

```bash
./wizard.exe <project_name>
./wizard.exe blinky
```

Podczas tworzenia nowego projektu lub przełączania się na istniejący, generowane są na nowo wszystkie pliki _(`makefile`, `flash.ld`, ...)_ niezbędne do poprawnego przeprowadzenia procesu kompilacji, czyli przekształcenia całości _(plików projektu i framework'a: `.c`, `.h`, `.s`)_ w plik wsadowy `.bin`/`.hex`, który można wgrać do sterownika jako działający program.

W przypadku zmiany wartości konfiguracyjnych `PRO_x` w pliku **`main.h`** lub modyfikacji **struktury projektu**, obejmującej:

- dodawanie nowych plików,
- przenoszenie plików
- usuwanie plików,
- zmiany nazw plików,

niezbędne jest ponowne załadowanie projektu. Jeśli projekt jest już aktywny, nie trzeba podawać jego nazwy `-r --reload`:

```bash
./wizard.exe -r
```

Tutaj _(upraszczając_)_ kończy się zadanie programu `wizard.exe`, a dalsza praca przebiega tak samo jak w typowym projekcie **embedded systems**, czyli przy użyciu **`make`**

## ✨ Make

Jeżeli mamy poprawnie przygotowaną konfigurację projektu oraz plik `makefile` wygenerowany za pomocą programu 🔮**Wizard**, to aby zbudować i wgrać program na sterownik PLC, wystarczy otworzyć konsolę w przestrzeni roboczej i wpisać:

```bash
make build # build c projekt to binary program
make flash # move binary fole to PLC (micorcotroler) memeory
# lub
make run   # run = build + flash
```

Zawiera zestaw instrukcji **Make** przygotowany w pliku `makefile`:

- **`make build`** lub samo **`make`**: Buduje projekt w języku C do postaci plików wsadowych `.bin`, `.hex`, `.elf`
- **`make flash`**: Wgrywa plik wsadowy programu do pamięci sterownika PLC _(mikrokontrolera)_
- **`make run`**: Wykonuje `make build`, a następnie `make flash`
- **`make clean`** lub `make clr`: Usuwa zbudowane pliki wsadowe dla aktywnego projektu
- `make clean_all`: Usuwa zbudowane pliki wsadowe dla wszystkich projektów
- **`make erase`**: Wgrywa pusty program na sterownik mikrokontrolera
- `make erase_real`: Całkowicie czyści pamięć mikrokontrolera

Użycie `erase_real` **_(erase full chip)_** może powodować zawieszenie mikrokontrolera. Aby przywrócić jego działanie, należy wgrać dowolny działający program za pomocą instrukcji `make flash` lub `make erase`, a następnie odłączyć zasilanie i ponownie je podłączyć po kilku sekundach.

### ⚙️ Config

Podczas pierwszego uruchomienia 🧙🏼‍♂️Wizard'a tworzony jest plik konfiguracyjny **`wizard.json`**. Zawiera on:

- **`paths`**: Lista ścieżek (względnych)
  - **`projects`**: Główny katalog z projektami. Nowe projekty tworzone są w tym miejscu. Można też skopiować projekt ręcznie. Wszystkie projekty są wykrywane automatycznie. Nazwą projektu jest dalsza część tej ścieżki.
  - **`framework`**: Katalog zawierający wszystkie wersje frameworka OpenCPLC. W jego wnętrzu tworzone są podkatalogi odpowiadające wersjom w formacie `major.minor.patch`, `develop` lub `main`. Każdy z nich zawiera pliki odpowiedniej wersji frameworka. Pobierane będą jedynie niezbędne wersje.
  - **`build`**: Katalog z zbudowanymi aplikacjami
- **`default`**: Lista domyślnych wartości dla nieprzekazanych flag podczas uruchamiania `wizard.exe`
- **`pwsh`**: Ustawienie tego parametru wymusza przygotowanie pliku `makefile` w wersji dla PowerShell _(wymagane na systemie Windows Home)_.

### 🤔 How works?

W pierwszej kolejności **Wizard** zainstaluje **GNU Arm Embedded Toolchain**, **OpenOCD**, **Make**, klienta **Git** oraz ustawi odpowiednio zmienne systemowe, jeżeli aplikacje nie są widoczne w systemie z poziomu konsoli. Jeżeli nie chcemy, aby ktoś grzebał w naszym systemie, możemy przygotować sobie [konfiguracje ręcznie](readme-install.md). Gdy 🪄**Wizard** zainstaluje brakujące aplikacje, poprosi o zresetowanie konsoli, ponieważ zmienne systemowe są ładowane podczas jej uruchamiania, a w procesie instlacji zostały dodane nowe.

Następnie, w razie konieczności, skopiuje framework OpenCPLC z [repozytorium](https://github.com/OpenCPLC/Framework) do folderu `${framework}` podanego w pliku konfiguracyjnym `wizard.json`. Domyślnie zostanie sklonowana najnowsza wersja frameworka, ale można wymusić pobranie wskazanej lub deweloperskiej pomocą `-f --framework`:

```bash
./wizard.exe <project_name> --new -f 1.0.2
./wizard.exe <project_name> --new -f develop
```

W przypadku przełączania się na istniejący projekt, flaga ta jest ignorowana, a projekt korzysta z wersji frameworka zapisanej w pliku `main.h` należącym do projektu. Wersja ta jest określona za pomocą definicji `#define PRO_FRAMEWORK_VERSION`.

Główną funkcją **Wizard**'a jest przygotowanie plików niezbędnych do pracy z wybranym projektem:

- `flash.ld`: definiuje rozkład pamięci RAM i FLASH mikrokontrolera _(nadpisuje)_
- `makefile`: Zawiera reguły budowania, czyszczenia i flashowania projektu _(nadpisuje)_
- `c_cpp_properties.json`: ustawia ścieżki do nagłówków i konfigurację IntelliSense w VS Code _(nadpisuje)_
- `launch.json`: konfiguruje debugowanie w VSCode _(nadpisuje)_
- `tasks.json`: opisuje zadania takie jak kompilacja czy flashowanie
- `settings.json`: ustawia lokalne preferencje edytora dla projektu
- `extensions.json`: sugeruje przydatne rozszerzenia do VSCode

### 🚩 Flags

Oprócz podstawowych flag opisanych powyżej, istnieje jeszcze kilka, które mogą pozostać niezmienione, ale warto znać ich istnienie. Poniżej znajduje się lista wszystkich flag:

- `name`: Nazwa projektu. Parametr domyśly przekazywany jako pierwszy. Będzie stanowić ścieżkę do projektu: `${projects}/name`, a końcowe pliki wsadowe _(`.bin`,`.hex`,`.elf`)_ zostaną zapisane w lokalizacji `${build}/name.bin`, `${build}/name.hex`, `${build}/name.elf`.


- `-n --new`: Tworznie nowego projektu o nazwie `{name}`. Nazwa musi byuć unkalna i nie zajęta. Wówczas opłaca się okśre flagi `-b`, `-

- `-s`: Wybiera projekt demonstracyjny dostępny w zasobach framework'a `res/samples`.


`-r`


- `-b --board`: Model sterownika PLC: `Uno`, `DIO`, `AIO`, `Eco` lub `None` dla pracy z czystym mikrokontrolerem lub inna nazwa własna


- `-f --framework`: Wersja frameworka _(domyślnie: `opencplc`)_. Pliki w tym folderze zostaną wykorzystane podczas kompilacji i będą traktowane przez **VSCode** jako część projektu.






- `-fv --framework-version`: Wersja framework'u/bibliotek, która zostanie pobrana _(domyślnie: `latest`)_. Brak ustawienia tej flagi spowoduje pobranie najnowszej stabilnej wersji. Można pobrać wersję deweloperską _(w fazie testów)_, ustawiając `dev`. Ustawienie flagi bez podania wersji spowoduje wyświetlenie listy dostępnych wersji.
- `-p --project`: Lokalizacja/folder aktywnego projektu. Domyślnie zostanie utworzony folder `projects`, a w nim folder projektu o nazwie `--name`. Pliki w tym folderze zostaną wykorzystane podczas kompilacji i będą traktowane przez **VSCode** jako część projektu.
- `-b --build`: Lokalizacja/katalog dla skompilowanych plików framework'u i projektu _(domyślnie: `build`)_. Bezpośrednio w tym folderze zostanie umieszczony końcowy plik wsadowy programu `.bin`/`.hex`.
- `-m --memory`: Ilość pamięci FLASH w wykorzystywanej płytce. Nie należy ustawiać dla oficjalnie wspieranych konstrukcji. W przypadku konstrukcji niestandardowych należy wybrać `128kB` lub `512kB`, w zależności od użytego mikrokontrolera.
- `-o --opt`: Poziom optymalizacji kodu dla kompilacji: `O0`, `Og`, `O1` _(default: `Og`)_. Poziomy optymalizacji `O2`, `O3` są niedozwolone!
- `-s --select`: Umożliwia przełączanie się między istniejącymi projektami. Gdy projekt zostanie utworzony, a następnie utworzymy nowy, powrót do pierwszego projektu polega na wywołaniu z tą flagą i podaniu jego nazwy. W przypadku dodania nowego pliku do projektu konieczne jest odświeżenie - wystarczy użyć tej flagi bez podawania wartości.
- `-l --list`: Wyświetla listę istniejących projektów.
- `-v --version`: Zwraca wersję programu 🧙🏼‍♂️**Wizard** oraz ścieżkę repozytorium.
- `-i --info`: Zwraca podstawowe informacje o bieżącym projekcie, czyli tym, nad którym aktualnie pracujesz. Dla tego projektu jest przygotowywany plik `makefile`, a polecenie `make` będzie z nim współpracować.

### 📟 Console

Programy 🧙🏼‍♂️Wizard oraz ✨Make są programami uruchamianymi z konsoli. Stanowią niezbędnik do pracy z OpenCPLC.

Konsola systemowa jest dostępna w wielu aplikacjach, takich jak **Command Prompt**, **PowerShell**, [**GIT Bash**](https://git-scm.com/downloads), a nawet terminal w [**VSCode**](https://code.visualstudio.com/). Gdy wywołanie w konsoli zwróci błąd, prawdopodobnie nie została otwarta w przestrzeni roboczej i nie widzi aplikacji `wizard.exe`. Możesz zamknąć konsolę i otworzyć ją w odpowiednim folderze lub przejść ręcznie, używając komendy `cd`.