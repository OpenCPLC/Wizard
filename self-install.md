## 🦉 Self-installed

Do pracy ze sterownikami OpenCPLC wymagany jest zestaw bardziej specjalistycznych narzędzi, identyczny z tym używanym do pracy z mikrokontrolerami **STM32**. W skład tego zestawu wchodzą:

- Klient [**GIT**](https://git-scm.com/downloads), czyli system kontroli wersji. Będzie potrzebny do pobrania najnowszych bibliotek OpenCPLC, ale jego możliwości sięgają znacznie dalej.
- Pakiet narzędzi [**GNU Arm Embedded Toolchain**](https://developer.arm.com/downloads/-/gnu-rm), który obejmuje on między innymi kompilator. Pakiet trzeba pobrać i zainstalować w lokalizacji `C:\ArmGCC`
- On-Chip Debugger, jakim jest [**OpenOCD** ](https://gnutoolchains.com/arm-eabi/openocd/). Umożliwia komunikację z mikrokontrolerem za pomocą programatora ST-Link. Pakiet trzeba pobrać, rozpakować i umieścić w lokalizacji `C:\OpenOCD`
- Narzędzia do zarządzania procesem kompilacji programów, jakim jest [**Make**](https://www.gnu.org/software/make/).

Aby zainstalować **Make**, można skorzystać z menedżera pakietów [**Chocolatey**](https://chocolatey.org/), który umożliwia prostą instalację wymaganych komponentów. Wystarczy otworzyć **PowerShell** jako 🛡️administrator i wywołać komendy:

```
Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
choco install make
```

Instalacja **Make** oraz **GIT** automatycznie utworzy zmienną systemową, jednak w przypadku pozostałych programów konieczne będzie ręczne ich utworzenie.

🪟 `Win` + `R` » `sysdm.cpl` » Advanced » **Environment Variables**

- ARMGCC → `C:\ArmGCC\bin`
- Path » `%ARMGCC%` oraz `C:\OpenOCD\bin`

![Env](https://sqrt.pl/img/opencplc/env.png)

Na zakończenie należy otworzyć konsolę i zweryfikować, czy wszystkie pakiety zostały zainstalowane poprawnie. Można to zrobić przy użyciu komendy `--version`.

```bash
git --version
arm-none-eabi-gcc --version
openocd --version
make --version
```

W ten sposób możemy upewnić się, że lokalizacja zainstalowanych pakietów została dostosowana do naszych preferencji oraz że zainstalowano najnowsze wersje oprogramowania wraz z dodatkami systemowymi _(takimi jak konsola GIT Bash)_.
