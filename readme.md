## 🔮 Wizard

**Wizard** jest aplikacją konsolową usprawniającą pracę z **OpenCPLC**, którego zadaniem jest dostosowanie środowiska pracy tak, aby 👨‍💻programista-automatyk mógł skupić się na tworzeniu aplikacji, a nie walce z konfiguracją ekosystemu i kompilacją programu. Pobierz **`wizard.exe`** z 🚀[Releases](https://github.com/OpenCPLC/Wizard/releases) i umieść go w wybranym folderze, który będzie pełnił rolę przestrzeni roboczej _(workspace)_. Następnie otwórz konsolę i wpisz:

```bash
./wizard.exe -n <new_project_name> -c <controller>
./wizard.exe -n blinky -c Uno
```

Konsola systemowa jest dostępna w wielu aplikacjach, takich jak **Command Prompt**, **PowerShell**, [**GIT Bash**](https://git-scm.com/downloads), a nawet terminal w [**VSCode**](https://code.visualstudio.com/). Gdy wywołanie w konsoli zwróci błąd, prawdopodobnie nie została otwarta w przestrzeni roboczej i nie widzi aplikacji `wizard.exe`. Możesz zamknąć konsolę i otworzyć ją w odpowiednim folderze lub przejść ręcznie, używając komendy `cd`.

Jeśli dodamy nowe pliki do projektu, konieczne będzie jego odświeżenie.

```bash
./wizard.exe -s
```

Gdy będziemy mieli więcej projektów, będziemy mogli swobodnie przełączać się między nimi.

```bash
./wizard.exe -s <existing_project_name>
./wizard.exe -s blinky
```

Aby pobrać i dodać istniejący projekt, należy postępować tak samo jak przy tworzeniu nowego projektu. Wystarczy wskazać poprawną ścieżkę do istniejącego projektu.

```bash
./wizard.exe -n <existing_project_name> -c <controller> -p <existing_project_path>
./wizard.exe -n stolen-project -c Uno -p projects/stolen
```

### 🤔 How works?

W pierwszej kolejności **Wizard** zainstaluje **GNU Arm Embedded Toolchain**, **OpenOCD**, **Make**, klienta **Git** oraz ustawi odpowiednio zmienne systemowe, jeżeli aplikacje nie są widoczne w systemie z poziomu konsoli. Jeżeli nie chcemy, aby ktoś grzebał w naszym systemie, możemy przygotować sobie [konfiguracje ręcznie](self-installed.md)

Gdy 🧙🏼‍♂️**Wizard** zainstaluje brakujące aplikacje, poprosi o zresetowanie konsoli, ponieważ zmienne systemowe są ładowane podczas jej uruchamiania, a w procesie instlacji zostały dodane nowe.

Następnie przeniesie biblioteki/framework OpenCPLC z repozytorium [https://github.com/OpenCPLC/Core](https://github.com/OpenCPLC/Core) do nowo utworzonego folderu `opencplc`. Lokalizację bibliotek można zmienić, przekazując alternatywną ścieżkę za pomocą `-f --framework`. Stworzy pliki startowe dla projektu _(`main.c`, `main.h`, `flash.ld`)_ w podanej lokalizacji `-p --project`, chyba że projekt już istnieje, a pliki będą się w nim znajdować.

Najważniejszą funkcjonalnością 🪄**Wizard**'a jest przygotowanie pliku `makefile` dla aplikacji **Make**. Można powiedzieć, że zastępuje w ten sposób narzędzie **CMake**. Choć ma zdecydowanie mniejsze możliwości, nie wymaga żadnej konfiguracji. Automatycznie zakłada, że wszystkie pliki znajdujące się w katalogu bibliotek/framework'u oraz projektu są potrzebne i przygotowuje je do kompilacji. Pamiętajmy, że podczas tworzenia nowego projektu lub przełączania się na istniejący, plik `makefile` oraz powiązane z nim konfiguracje zostają nadpisane.

Ostatnim zadaniem 🔮**Wizard**'a jest utworzenie plików konfiguracyjnych dla VSCode, które integrują IDE z zainstalowanymi programami oraz z projektem.

Niezbędne informacje o utworzonych projektach są przechowywane w pliku `wizard.json`. Ten mechanizm umożliwia swobodne przełączanie się `-s --select` między projektami bez utraty konfiguracji, ponieważ zawiera kompletny zestaw informacji potrzebnych do ich odtworzenia. Po usunięciu katalogu z projektem zostanie on automatycznie usunięty z listy.

### 🚩 Flags

Oprócz podstawowych flag opisanych powyżej, istnieje jeszcze kilka, które mogą pozostać niezmienione, ale warto znać ich istnienie. Poniżej znajduje się lista wszystkich flag:

- `-n --name`: Nazwa projektu _(domyślnie: `app`)_. Będzie wykorzystywany do przełączania się między różnymi projektami. Końcowy plik wsadowy programu `.bin`/`.hex` będzie nosił tą nazwę.
- `-c --controller`: Model sterownika PLC z oficjalnie wspieranych konstrukcji: `Uno`, `DIO`, `AIO`, `Eco` (domyślnie: `Uno`), lub:
  - `Custom` - dla konstrukcji niestandardowej w ramach frameworku **OpenCPLC**
  - `Void` - dla projektu **STM32** pozbawionego warstwy abstrakcji dedykowanej sterownikom PLC
- `-f --framework`: Lokalizacja/folder dla framework'u/bibliotek _(domyślnie: `opencplc`)_. Pliki w tym folderze zostaną wykorzystane podczas kompilacji i będą traktowane przez **VSCode** jako część projektu.
- `-fv --framework-version`: Wersja framework'u/bibliotek, która zostanie pobrana _(domyślnie: `latest`)_. Brak ustawienia tej flagi spowoduje pobranie najnowszej stabilnej wersji. Można pobrać wersję deweloperską _(w fazie testów)_, ustawiając `dev`. Ustawienie flagi bez podania wersji spowoduje wyświetlenie listy dostępnych wersji.
- `-p --project`: Lokalizacja/folder aktywnego projektu. Domyślnie zostanie utworzony folder `projects`, a w nim folder projektu o nazwie `--name`. Pliki w tym folderze zostaną wykorzystane podczas kompilacji i będą traktowane przez **VSCode** jako część projektu.
- `-b --build`: Lokalizacja/katalog dla skompilowanych plików framework'u i projektu _(domyślnie: `build`)_. Bezpośrednio w tym folderze zostanie umieszczony końcowy plik wsadowy programu `.bin`/`.hex`.
- `-m --memory`: Ilość pamięci FLASH w wykorzystywanej płytce. Nie należy ustawiać dla oficjalnie wspieranych konstrukcji. W przypadku konstrukcji niestandardowych należy wybrać `128kB` lub `512kB`, w zależności od użytego mikrokontrolera.
- `-o --opt`: Poziom optymalizacji kodu dla kompilacji: `O0`, `Og`, `O1` _(default: `Og`)_. Poziomy optymalizacji `O2`, `O3` są niedozwolone!
- `-s --select`: Umożliwia przełączanie się między istniejącymi projektami. Gdy projekt zostanie utworzony, a następnie utworzymy nowy, powrót do pierwszego projektu polega na wywołaniu z tą flagą i podaniu jego nazwy. W przypadku dodania nowego pliku do projektu konieczne jest odświeżenie - wystarczy użyć tej flagi bez podawania wartości.
- `-l --list`: Wyświetla listę istniejących projektów.
- `-v --version`: Zwraca wersję programu 🧙🏼‍♂️**Wizard** oraz ścieżkę repozytorium.
- `-i --info`: Zwraca podstawowe informacje o bieżącym projekcie, czyli tym, nad którym aktualnie pracujesz. Dla tego projektu jest przygotowywany plik `makefile`, a polecenie `make` będzie z nim współpracować.

## ✨ Make

Aby zbudować program i wgrać go na sterownik PLC _(mikrokontroler)_, wystarczy otworzyć konsolę w przestrzeni roboczej _(tam, gdzie pracowaliśmy z wizard.exe)_ i wpisać:

```bash
make build # build c projekt to binary program
make flash # move binary fole to PLC (micorcotroler) memeory
```

Zawiera zestaw instrukcji **Make** przygotowany w pliku `makefile`:

- **`make build`** lub samo **`make`**: Buduje projekt w języku C do postaci plików wsadowych `.bin`, `.hex`, `.elf`
- **`make flash`**: Wgrywa plik wsadowy programu do pamięci sterownika PLC _(mikrokontrolera)_
- **`make run`**: Wykonuje `make build`, a następnie `make flash`
- **`make clean`** lub `make clr`: Usuwa zbudowane pliki wsadowe dla aktywnego projektu
- `make clean_all`: Usuwa zbudowane pliki wsadowe dla wszystkich projektów
- **`make erase`**: Wgrywa pusty program na sterownik mikrokontrolera
- `make erase_real`: Całkowicie czyści pamięć mikrokontrolera

Użycie `erase_real` **_(erase full chip)_** powoduje zawieszenie mikrokontrolera. Aby przywrócić jego działanie, należy wgrać dowolny działający program za pomocą instrukcji `make flash` lub `make erase`, a następnie odłączyć zasilanie i ponownie je podłączyć po kilku sekundach.

## 💼 Workspace Management

Sposób organizacji przestrzeni roboczej zależy od liczby projektów i wielkości organizacji. Domyślnie zakładamy, że pracujesz sam lub w małym zespole. Wówczas najlepiej sprawdzi się struktura katalogów:

- Workspace folder `./`:
  - Framework: `./opencplc/`
  - Projekty: `./projects/`
    - Projekt **1**: `./projects/<pro1_name>/`
    - Projekt **2**: `./projects/<pro2_name>/`
    - Projekt **3**: `./projects/<pro3_name>/`

Jest to domyślna struktura, więc tworząc nowy projekt, wystarczy wywołać z konsoli:

```bash
./wizard.exe -n <new_project_name> -c <controller>
```

Gdy planujemy większą liczbę projektów, warto je pogrupować, tematycznie lub według klientów:

- Workspace folder `./`:
  - Framework: `./opencplc/`
  - Projekty: `./projects/`
    - Grupa **A**: `./projects/<group_a_name>/`
      - Projekt **A1**: `./projects/<group_a_name>/<pro_a1_name>/`
      - Projekt **A2**: `./projects/<group_a_name>/<pro_a2_name>/`
    - Grupa **B**: `./projects/<group_b_name>/`
      - Projekt **B1**: `./projects/<group_b_name>/<pro_b1_name>/`

Wówczas przy uruchomieniu wizard'a trzeba przekazać ścieżkę do projektu za pomocą flagi `-p`:

```bash
./wizard.exe -n <new_project_name> -c <controller> -p projects/<group_name>/<pro_name>
```

Jeśli prowadzimy tylko jeden większy projekt i nie planujemy więcej, można wykorzystać płaską strukturę, gdzie wszystkie katalogi będą w jednym folderze projektu:

- Project folder `./`
- Framework folder: `./`

Wówczas przy uruchomieniu wizard'a trzeba przekazać ścieżkę do projektu `-p` i zmienić ścieżkę framework'u za pomocą `-f`:

```bash
./wizard.exe -n <new_project_name> -c <controller> -p ./ -f ./
```

W przypadku pracy w dużej firmie z licznymi projektami nie ma sensu przechowywać wszystkich projektów w jednym workspace; konieczne jest ich wersjonowanie, ponieważ aktualizacje frameworku mogą powodować błędy w aplikacjach, których może zabraknąć czasu na szybkie poprawienie. Przy pracy nad wieloma projektami z innymi deweloperami warto mieć osobny folder dla każdej używanej **wersji OpenCPLC**, co pozwala rozwijać każdy projekt w odpowiedniej wersji, a aktualizację do nowszej wersji przeprowadzać wtedy, gdy będzie to konieczne lub możliwe czasowo.

- Workspace folder `./`:
  - Framework: `./opencplc/`
    - Wersja **1.2.0-rc.3**: `./opencplc/1.2.0-rc.3/`
    - Wersja **1.1.7**: `./opencplc/1.1.7/`
    - Wersja **1.0.2**: `./opencplc/1.0.2/`
  - Projekty: `./projects/`
    - Projekt **1**: `./projects/<pro1_name>/`
    - Projekt **2**: `./projects/<pro2_name>/`
    - Projekt **3**: `./projects/<pro3_name>/`
    - Projekt **4**: `./projects/<pro4_name>/`

Wówczas przy uruchomieniu wizard'a warto mieć kontrolę nad wersją, na której pracujemy:

```bash
./wizard.exe -n <new_project_name> -c <controller> -f <framework_path> -fv <opencplc_version>
```

Gdy wersja framework'u się nie zgadza, wizard poinformuje nas o tym. Informacje o wymaganej wersji framework'u OpenCPLC przechowuje definicja **`PRO_OPENCPLC_VERSION`** w pliku `main.h`.
