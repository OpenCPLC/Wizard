flash_ld = """
ENTRY(Reset_Handler)

_estack = ORIGIN(RAM) + LENGTH(RAM);

_Min_Heap_Size = 0x200;
_Min_Stack_Size = 0x400;

MEMORY
{
  RAM(xrw)  : ORIGIN = 0x20000000, LENGTH = ${RAM}K
  FLASH(rx) : ORIGIN = 0x8000000,  LENGTH = ${FLASH}K
}

SECTIONS
{
  .isr_vector : {
    . = ALIGN(4);
    KEEP(*(.isr_vector))
    . = ALIGN(4);
  } >FLASH

  .text : {
    . = ALIGN(4);
    *(.text)
    *(.text*)
    *(.glue_7)
    *(.glue_7t)
    *(.eh_frame)
    KEEP (*(.init))
    KEEP (*(.fini))
    . = ALIGN(4);
    _etext = .;
  } >FLASH

  .rodata : {
    . = ALIGN(4);
    *(.rodata)
    *(.rodata*)
    . = ALIGN(4);
  } >FLASH

  .ARM.extab : { 
    . = ALIGN(4);
    *(.ARM.extab* .gnu.linkonce.armextab.*)
    . = ALIGN(4);
  } >FLASH
  
  .ARM : {
    . = ALIGN(4);
    __exidx_start = .;
    *(.ARM.exidx*)
    __exidx_end = .;
    . = ALIGN(4);
  } >FLASH

  .preinit_array : {
    . = ALIGN(4);
    PROVIDE_HIDDEN (__preinit_array_start = .);
    KEEP (*(.preinit_array*))
    PROVIDE_HIDDEN (__preinit_array_end = .);
    . = ALIGN(4);
  } >FLASH
  
  .init_array : {
    . = ALIGN(4);
    PROVIDE_HIDDEN (__init_array_start = .);
    KEEP (*(SORT(.init_array.*)))
    KEEP (*(.init_array*))
    PROVIDE_HIDDEN (__init_array_end = .);
    . = ALIGN(4);
  } >FLASH
  
  .fini_array : {
    . = ALIGN(4);
    PROVIDE_HIDDEN (__fini_array_start = .);
    KEEP (*(SORT(.fini_array.*)))
    KEEP (*(.fini_array*))
    PROVIDE_HIDDEN (__fini_array_end = .);
    . = ALIGN(4);
  } >FLASH

  _sidata = LOADADDR(.data);

  .data : {
    . = ALIGN(4);
    _sdata = .;
    *(.data)
    *(.data*)
    . = ALIGN(4);
    _edata = .;
  } >RAM AT> FLASH

  . = ALIGN(4);

  .bss : {
    _sbss = .;
    __bss_start__ = _sbss;
    *(.bss)
    *(.bss*)
    *(COMMON)

    . = ALIGN(4);
    _ebss = .;
    __bss_end__ = _ebss;
  } >RAM

  ._user_heap_stack : {
    . = ALIGN(8);
    PROVIDE ( end = . );
    PROVIDE ( _end = . );
    . = . + _Min_Heap_Size;
    . = . + _Min_Stack_Size;
    . = ALIGN(8);
  } >RAM

  /DISCARD/ : {
    libc.a ( * )
    libm.a ( * )
    libgcc.a ( * )
  }

  .ARM.attributes 0 : { *(.ARM.attributes) }
}
"""

makefile = """
TARGET = ${NAME}
CTRL = ${CTRL}
FW = ${FRAMEWORK}
PRO = ${PROJECT}
BUILD = ${BUILD}
OPT = ${OPT}
FAMILY = ${FAMILY}

C_SOURCES = \\
${C_SOURCES}

ASM_SOURCES = \\
${ASM_SOURCES}

PREFIX = arm-none-eabi-

ifdef GCC_PATH
CC = $(GCC_PATH)/$(PREFIX)gcc
AS = $(GCC_PATH)/$(PREFIX)gcc -x assembler-with-cpp
CP = $(GCC_PATH)/$(PREFIX)objcopy
SZ = $(GCC_PATH)/$(PREFIX)size
else
CC = $(PREFIX)gcc
AS = $(PREFIX)gcc -x assembler-with-cpp
CP = $(PREFIX)objcopy
SZ = $(PREFIX)size
endif
HEX = $(CP) -O ihex
BIN = $(CP) -O binary -S
 
CPU = -mcpu=cortex-m0plus

# MCU = $(CPU) -mthumb $(FPU) $(FLOAT-ABI) # Floating point numbers
MCU = $(CPU) -mthumb
AS_DEFS = -D$(FAMILY) -D$(CTRL)
C_DEFS = -D$(FAMILY) -D$(CTRL)

ASM_INCLUDES =

C_INCLUDES = \\
${C_INCLUDES}

ASFLAGS = $(MCU) $(AS_DEFS) $(ASM_INCLUDES) -$(OPT) -Wall -fdata-sections -ffunction-sections
CFLAGS = $(MCU) $(C_DEFS) $(C_INCLUDES) -$(OPT) -Wall -fdata-sections -ffunction-sections
CFLAGS += -g -gdwarf-2 # DEBUG
CFLAGS += -MMD -MP -MF"$(@:%.o=%.d)"

CFLAGS += -MMD -MP -MF"$(@:%.o=%.d)"

LDSCRIPT = ${LD_FILE}

LIBS = -lc -lm -lnosys
LIBDIR = 
LDFLAGS = $(MCU) -specs=nano.specs -T$(LDSCRIPT) $(LIBDIR) $(LIBS)
LDFLAGS += -Wl,-Map=$(BUILD)/$(TARGET).map,--cref -Wl,--gc-sections

all: $(BUILD)/$(TARGET).elf $(BUILD)/$(TARGET).hex $(BUILD)/$(TARGET).bin

OBJECTS = $(patsubst %.c,$(BUILD)/%.o,$(C_SOURCES))
C_DIRS := $(sort $(dir $(shell find . -name "*.c")))
vpath %.c $(C_DIRS)
OBJECTS += $(patsubst %.s,$(BUILD)/%.o,$(ASM_SOURCES))
ASM_DIRS := $(sort $(dir $(shell find . -name "*.s")))
vpath %.s $(ASM_DIRS)

$(BUILD)/%.o: %.c Makefile | $(dir $(BUILD)/%)
	@mkdir -p $(dir $@)
	$(CC) -c $(CFLAGS) -Wa,-a,-ad,-alms=$(BUILD)/$(<:%.c=%.lst) $< -o $@
	
$(BUILD)/%.o: %.s Makefile | $(dir $(BUILD)/%)
	$(AS) -c $(CFLAGS) $< -o $@

$(BUILD)/$(TARGET).elf: $(OBJECTS) Makefile
	$(CC) $(OBJECTS) $(LDFLAGS) -o $@
	$(SZ) $@

$(BUILD)/%.hex: $(BUILD)/%.elf | $(dir $(BUILD)/%)
	$(HEX) $< $@

$(BUILD)/%.bin: $(BUILD)/%.elf | $(dir $(BUILD)/%)
	$(BIN) $< $@

$(dir $(BUILD)/%):
	mkdir -p $@

build: all

flash: all
	openocd -f interface/stlink.cfg -f target/stm32g0x.cfg -c "program $(BUILD)/$(TARGET).elf verify reset exit"

run: flash

earse:
	openocd -f interface/stlink.cfg -f target/stm32g0x.cfg -c "init; halt; stm32g0x mass_erase 0; reset; exit"

clean:
	cmd /c del /q $(BUILD)\\\\$(TARGET).* && \\${DEVELOP_CLEAN}
	if [ -d "$(BUILD)\\\\$(PRO)" ]; then cmd /c rmdir /s /q $(BUILD)\\\\$(PRO); fi

clr: clean

clean_all:
	if [ -d "$(BUILD)" ]; then cmd /c rmdir /s /q $(BUILD); fi

.PHONY: all build flash run earse clean clr clean_all

-include $(wildcard $(BUILD)/$(TARGET).d)${DEVELOP_WILDCARD}
-include $(wildcard $(BUILD)/$(PRO)/*.d)
"""

properties_json = """
{
  "configurations": [
    {
      "name": "${NAME}",
      "includePath": [
        "${workspaceFolder}/${FRAMEWORK}/**",
        "${workspaceFolder}/${PROJECT}/**"
      ],
      "defines": [
        "${FAMILY}",
        "${CTRL}"
      ],
      "cStandard": "c11",
      "cppStandard": "c++17",
      "intelliSenseMode": "gcc-arm",
      "compilerPath": "${env:ARMGCC}/arm-none-eabi-gcc.exe",
      "compilerArgs": [
        "-mcpu=cortex-m0plus",
        "-mthumb"
      ],
      "configurationProvider": "ms-vscode.makefile-tools"
    }
  ],
  "version": 4
}
"""

launch_json = """
{
  "version": "0.2.0",
  "tasks": [
    {
      "label": "make",
      "type": "shell",
      "command": "make",
      "group": {
        "kind": "build",
        "isDefault": true
      }
    }
  ],
  "configurations": [
    {
      "name": "Debug",
      "cwd": "${workspaceRoot}",
      "executable": "${BUILD}/${NAME}.elf",
      "request": "launch",
      "type": "cortex-debug",
      "servertype": "openocd",
      "device": "${DEVICE}",
      "configFiles": [
        "interface/stlink.cfg",
        "target/stm32g0x.cfg"
      ],
      "svdFile": "${FRAMEWORK}/inc/ST/${SVD}",
      "preLaunchTask": "make"
    }
  ]
}
"""

tasks_json = """
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "make",
      "type": "shell",
      "command": "make",
      "group": {
        "kind": "build",
        "isDefault": true
      }
    }
  ]
}
"""

settings_json = """
{
  "files.associations": {
    "*.h": "c"
  },
  "editor.tabSize": 2,
  "editor.insertSpaces": true,
  "editor.mouseWheelZoom": true,
  "editor.tokenColorCustomizations": {
    "textMateRules": [
      { "scope": "variable.other.global.c", "settings": { "foreground": "#62CCDC" } },
      { "scope": "variable.other.local.c", "settings": { "foreground": "#9CDCFE" } },
      { "scope": "variable.other", "settings": { "foreground": "#ACEDFF" } },
      { "scope": "comment", "settings": { "foreground": "#777", "fontStyle": "italic" } },
      { "scope": "entity.name.function.preprocessor", "settings": { "foreground": "#68D" } },
      { "scope": "storage.modifier", "settings": { "foreground": "#9786c5" } }
    ]
  }
}
"""

extensions_json = """
{
  "recommendations": [
    "ms-vscode.cpptools",
    "ms-vscode.cpptools-themes",
    "ms-vscode.makefile-tools",
    "ms-vscode.hexeditor",
    "mechatroner.rainbow-csv",
    "marus25.cortex-debug",
    "jeff-hykin.better-cpp-syntax"
  ]
}
"""

main_h = """
/**
 * @file  main.h
 * @brief W tym pliku należy umieścić parametry konfiguracyjne `#define`, które chce się nadpisać.
 *        Wiele z bibliotek OpenCPLC załącza ten plik `#include`, zatem musi on istnieć, nawet jeśli będzie pusty.
 *        Dzięki takiemu rozwiązaniu można nadpisać różnego rodzaju definicje (zmienne) konfiguracyjne.
 *        Biblioteki OpenCPLC w pierwszej kolejności będą pobierały zawarte tutaj zmienne,
 *        zamiast korzystać z domyślnych wartości zawartych we własnych plikach nagłówkowych `.h`.
 * @date  ${DATE}
 */

#define SYS_CLOCK_FREQ ${FREQ}
"""

main_c = """
// Import podstawowych funkcji sterownika.
#include "opencplc.h"

// Stos pamięci dla wątku PLC
static uint32_t stack_plc[256];
// Stos pamięci dla wątku Debugera (bash + dbg + log)
static uint32_t stack_dbg[256];
// Stos pamięci dla funkcji loop
static uint32_t stack_loop[1024];

void loop(void)
{
  while(1) {
    // Ustawienie diody informacyjnej, aby świeciła na czerwoną
    LED_Set(RGB_Red);
    delay(1000); // Odczekaj 1s
    // Ustawienie diody informacyjnej, aby świeciła na zieloną
    LED_Set(RGB_Green);
    delay(1000); // Odczekaj 1s
    // Ustawienie diody informacyjnej, aby świeciła na niebieską
    LED_Set(RGB_Blue);
    delay(1000); // Odczekaj 1s
    // Wyłączenie diody informacyjnej
    LED_Rst();
    delay(1000); // Odczekaj 1s
  }
}

int main(void)
{
  // Dodanie wątku sterownika
  thread(&PLC_Thread, stack_plc, sizeof(stack_plc) / sizeof(uint32_t));
  // Dodanie wątku sterownika
  thread(&DBG_Loop, stack_dbg, sizeof(stack_dbg) / sizeof(uint32_t));
  // Dodanie funkcji loop jako wątek
  thread(&loop, stack_loop, sizeof(stack_loop) / sizeof(uint32_t));
  // Włączenie systemy przełączania wątków VRTS
  VRTS_Init();
  // W to miejsce program nigdy nie powinien dojść
  while(1);
}
"""