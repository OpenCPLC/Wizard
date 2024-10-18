## 🔮 Wizard

**Wizard** jest aplikacją konsolową usprawniającą pracę z **OpenCPLC**, którego zadaniem jest dostosowanie środowiska pracy tak, aby 👨‍💻programista-automatyk mógł skupić się na tworzeniu aplikacji, a nie walce z konfiguracją ekosystemu i kompilacją programu. Podczas uruchomienia konieczne jest wybranie sterownika `-c --controller`, ustawienie nazwy projektu `-n --name` oraz jego lokalizacji `-p --project`.

```bash
./wizard.exe -n <project_name> -c <controller> -p <path/to/project>
./wizard.exe -n blinky -c Uno -p projects/blinky
```

W pierwszej kolejności **Wizard** zainstaluje **GNU Arm Embedded Toolchain**, **OpenOCD**, **Make**, klienta **Git** oraz ustawi odpowiednio zmienne systemowe, jeżeli aplikacje nie są widoczne w systemie z poziomu konsoli. Jeżeli nie chcemy, aby ktoś grzebał w naszym systemie, możemy przygotować sobie [konfiguracje ręcznie](self-installed.md)

Gdy 🧙🏼‍♂️ **Wizard** zainstaluje brakujące aplikacje, poprosi o zresetowanie konsoli, ponieważ zmienne systemowe są ładowane podczas jej uruchamiania, a w procesie instlacji zostały dodane nowe.

Następnie przeniesie biblioteki/framework OpenCPLC z repozytorium [https://github.com/OpenCPLC/Core](https://github.com/OpenCPLC/Core) do nowo utworzonego folderu `opencplc`. Lokalizację bibliotek można zmienić, przekazując alternatywną ścieżkę za pomocą `-f --framework`. Stworzy pliki startowe dla projektu _(`main.c`, `main.h`, `flash.ld`)_ w podanej lokalizacji `-p --project`, chyba że projekt już istnieje, a pliki będą się w nim znajdować.

Najważniejszą funkcjonalnością 🪄 **Wizard**'a jest przygotowanie pliku `makefile` dla aplikacji **Make**. Można powiedzieć, że zastępuje w ten sposób narzędzie **CMake**. Choć ma zdecydowanie mniejsze możliwości, nie wymaga żadnej konfiguracji. Automatycznie zakłada, że wszystkie pliki znajdujące się w katalogu bibliotek/framework'u oraz projektu są potrzebne i przygotowuje je do kompilacji. Aby plik `makefile` został nadpisany podczas przełączania się między projektami lub zmiany ustawień projektu, należy ustawić flagę `-r --reset`.

Ostatnim zadaniem 🔮 **Wizard**'a jest utworzenie plików konfiguracyjnych dla VSCode, które integrują IDE z zainstalowanymi programami oraz z projektem.

## 🚩 Flags

Oprócz podstawowych flag opisanych powyżej, istnieje jeszcze kilka, które mogą pozostać niezmienione, ale warto znać ich istnienie. Poniżej znajduje się lista wszystkich flag:

- `-n --name`: Nazwa projektu _(domyślnie: `app`)_. Końcowy plik wsadowy programu `.bin`/`.hex` będzie nosił tą nazwę.
- `-c --controller`: Model sterownika PLC z oficjalnie wspieranych konstrukcji: `Uno`, `DIO`, `AIO`, `Eco` (domyślnie: `Uno`), lub:
  - `Custom` - dla konstrukcji niestandardowej w ramach frameworku **OpenCPLC**
  - `Void` - dla projektu **STM32** pozbawionego warstwy abstrakcji dedykowanej sterownikom PLC
- `-f --framework`: Lokalizacja/folder dla framework'u/bibliotek _(domyślnie: `opencplc`)_. Pliki w tym folderze zostaną wykorzystane podczas kompilacji i będą traktowane przez **VSCode** jako część projektu.
- `-p --project`: Lokalizacja/folder projektu. Domyślnie zostanie utworzony folder `projects`, a w nim folder projektu o nazwie `--name`. Pliki w tym folderze zostaną wykorzystane podczas kompilacji i będą traktowane przez **VSCode** jako część projektu.
- `-b --build`: Lokalizacja/katalog dla skompilowanych plików frameworka i projektu _(domyślnie: `build`)_. Bezpośrednio w tym folderze zostanie umieszczony końcowy plik wsadowy programu `.bin`/`.hex`.
- `-m --memory`: Ilość pamięci FLASH w wykorzystywanej płytce. ⚠️ Nie należy ustawiać dla oficjalnie wspieranych konstrukcji. W przypadku konstrukcji niestandardowych należy wybrać `128kB` lub `512kB`, w zależności od użytego mikrokontrolera.
- `-r --reset`: Umożliwia nadpisanie pliku `makefile` oraz innych powiązanych plików konfiguracyjnych. Należy użyć w przypadku zmiany konfiguracji projektu, tworzenia nowego projektu lub przełączania się między projektami.
- `-o --opt`: Poziom optymalizacji kodu dla kompilacji: `O0`, `Og`, `O1`, `O2`, `O3` _(default: `Og`)_
- `-v --version`: Zwraca wersję programu 🧙🏼‍♂️ **Wizard** oraz inne informacje o programie. Dodatkowo, znajduje ostatnio modyfikowany plik w folderach `-f --framework`, `-p --project` oraz `-b --build`, a także zwraca datę jego ostatniej modyfikacji.
