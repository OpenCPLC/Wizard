## 🕒 Changes

### 2025-xx-xx: `0.0.2`

- [x] Usuwanie projektów za pomocą flagi `-d --delete`.
- [x] Pobieranie projektu z **GIT**'a lub zdalnego pliku **ZIP** za pomocą flagi `-g --get`.
  - Jeśli `@name` w pliku `main.h` jest poprawnie zdefiniowane, nie ma potrzeby podawania nazwy projektu.
- [x] Generowanie pliku `main.c` w przypadku pracy bez sterownika _(`-b --board` ustawione na `None`)_. Na przykład podczas pracy na gołej płytce **Nucleo**.
- [x] Indeksowanie projektów podczas wyświetlania list _(dla przykładów i projektów demonstracyjnych)_.
  - Teraz podczas ładowania projektów i przykładów demonstracyjnych można odwoływać się do indeksów.

```bash
./wizard -l -s # wyświetlenie listy przykładów
1   opencplc/develop/res/samples/ain/basic
2   opencplc/develop/res/samples/ain/scale
3   opencplc/develop/res/samples/basic/led
4   opencplc/develop/res/samples/basic/volts
5   opencplc/develop/res/samples/rs485/modbus
6   opencplc/develop/res/samples/rtd/pt100
7   opencplc/develop/res/samples/twi/shtc3
./wizard -s 3 # wybranie do załadowania przykładu 3: basic/led
```

### 2025-04-19: `0.0.1`

- [x] Aktualizacja programu **Wizard** z flagą `-u --update`.
- [x] Sprawdzanie minimalnych wersji programów: Git, ArmGCC, OpenOCD i Make. Ostrzeżenie `WRN`, gdy zainstalowana wersja programu jest starsza niż zalecana. Ze starszą wersją **ArmGCC** występowały problemy.
- [x] Poprawa generowanego pliku `launch.json`. Nie działało debugowanie przez złą nazwę pliku `.elf`, która była inna niż nazwa projektu, bo nie mogła zawierać znaków `/`.
- [x] Poprawa generowanego pliku `makefile`, żeby działał dobrze zarówno w konsoli `pwsh`, jak i `bash` _(na razie testowane jedynie pod Windows)_.

### 2025-04-18: `0.0.0`

- [x] Pierwsza stabilna wersja alfa, która pozornie wygląda, jakby wszystko działało.
