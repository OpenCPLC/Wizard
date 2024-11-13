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
- `-p --project`: Lokalizacja/folder aktywnego projektu. Domyślnie zostanie utworzony folder `projects`, a w nim folder projektu o nazwie `--name`. Pliki w tym folderze zostaną wykorzystane podczas kompilacji i będą traktowane przez **VSCode** jako część projektu.
- `-b --build`: Lokalizacja/katalog dla skompilowanych plików framework'u i projektu _(domyślnie: `build`)_. Bezpośrednio w tym folderze zostanie umieszczony końcowy plik wsadowy programu `.bin`/`.hex`.
- `-m --memory`: Ilość pamięci FLASH w wykorzystywanej płytce. Nie należy ustawiać dla oficjalnie wspieranych konstrukcji. W przypadku konstrukcji niestandardowych należy wybrać `128kB` lub `512kB`, w zależności od użytego mikrokontrolera.
- `-o --opt`: Poziom optymalizacji kodu dla kompilacji: `O0`, `Og`, `O1`, `O2`, `O3` _(default: `Og`)_
- `-s --select`: Umożliwia przełączanie się między istniejącymi projektami. Gdy projekt zostanie utworzony, a następnie utworzymy nowy, powrót do pierwszego projektu polega na wywołaniu z tą flagą i podaniu jego nazwy. W przypadku dodania nowego pliku do projektu konieczne jest odświeżenie - wystarczy użyć tej flagi bez podawania wartości.
- `-l --list`: Wyświetla listę istniejących projektów.
- `-v --version`: Zwraca wersję programu 🧙🏼‍♂️**Wizard** oraz ścieżkę repozytorium.
- `-i --info`: Zwraca podstawowe informacje o bieżącym projekcie, czyli tym, nad którym aktualnie pracujesz. Dla tego projektu jest przygotowywany plik `makefile`, a polecenie `make` będzie z nim współpracować.
