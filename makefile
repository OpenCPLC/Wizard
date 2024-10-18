TARGET = blinky

DEBUG = 1

OPT = -Og

BUILD = build

C_SOURCES = opencplc/inc/int.c opencplc/inc/startup.c opencplc/inc/ST/syscalls.c opencplc/inc/ST/sysmem.c \
opencplc/inc/ST/system_stm32g0xx.c opencplc/lib/dev/bash.c opencplc/lib/dev/dbg.c \
opencplc/lib/dev/stream.c opencplc/lib/ext/buff.c opencplc/lib/ext/eeprom.c opencplc/lib/ext/exbit.c \
opencplc/lib/ext/exmath.c opencplc/lib/ext/exstring.c opencplc/lib/ext/extime.c opencplc/lib/ext/file.c \
opencplc/lib/ext/var.c opencplc/lib/ifc/i2c-master.c opencplc/lib/ifc/i2c-slave.c \
opencplc/lib/ifc/i2c.c opencplc/lib/ifc/spi-master.c opencplc/lib/ifc/spi.c opencplc/lib/ifc/uart.c \
opencplc/lib/per/adc.c opencplc/lib/per/crc.c opencplc/lib/per/flash.c opencplc/lib/per/gpio.c \
opencplc/lib/per/pwm.c opencplc/lib/per/pwr.c opencplc/lib/per/rng.c opencplc/lib/per/rtc.c \
opencplc/lib/per/tim.c opencplc/lib/sys/new.c opencplc/lib/sys/vrts.c opencplc/plc/app/hd44780.c \
opencplc/plc/brd/opencplc-uno.c opencplc/plc/com/modbus-master.c opencplc/plc/com/modbus-slave.c \
opencplc/plc/com/one-wire.c opencplc/plc/per/ain.c opencplc/plc/per/din.c opencplc/plc/per/dout.c \
opencplc/plc/per/max31865.c opencplc/plc/per/pwmi.c opencplc/plc/per/rgb.c opencplc/plc/utils/cron.c \
opencplc/plc/utils/timer.c projects/blinky/main.c 

ASM_SOURCES = opencplc/lib/sys/vrts-pendsv.s 

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

# MCU = $(CPU) -mthumb $(FPU) $(FLOAT-ABI)
MCU = $(CPU) -mthumb

AS_DEFS = -DSTM32G0C1xx -DOPENCPLC_UNO

C_DEFS = -DSTM32G0C1xx -DOPENCPLC_UNO

ASM_INCLUDES =

C_INCLUDES = -Iopencplc/inc -Iopencplc/inc/CMSIS -Iopencplc/inc/ST -Iopencplc/lib/dev -Iopencplc/lib/ext \
-Iopencplc/lib/ifc -Iopencplc/lib/per -Iopencplc/lib/sys -Iopencplc/plc/app -Iopencplc/plc/brd \
-Iopencplc/plc/com -Iopencplc/plc/per -Iopencplc/plc/utils -Iprojects/blinky 

ASFLAGS = $(MCU) $(AS_DEFS) $(ASM_INCLUDES) $(OPT) -Wall -fdata-sections -ffunction-sections
CFLAGS = $(MCU) $(C_DEFS) $(C_INCLUDES) $(OPT) -Wall -fdata-sections -ffunction-sections

ifeq ($(DEBUG), 1)
CFLAGS += -g -gdwarf-2
endif

CFLAGS += -MMD -MP -MF"$(@:%.o=%.d)"

LDSCRIPT = projects/blinky/flash.ld

LIBS = -lc -lm -lnosys
LIBDIR = 
LDFLAGS = $(MCU) -specs=nano.specs -T$(LDSCRIPT) $(LIBDIR) $(LIBS) -Wl,-Map=$(BUILD)/$(TARGET).map,--cref -Wl,--gc-sections

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

earse:
	openocd -f interface/stlink.cfg -f target/stm32g0x.cfg -c "init; halt; stm32g0x mass_erase 0; reset; exit"

clean:
	cmd /c del /q $(BUILD)\\$(TARGET).* &&   if [ -d "$(BUILD)\\opencplc" ]; then cmd /c rmdir /s /q $(BUILD)\\opencplc; fi &&   if [ -d "$(BUILD)\\projects\\blinky" ]; then cmd /c rmdir /s /q $(BUILD)\\projects\\blinky; fi

clean_all:
	if [ -d "$(BUILD)" ]; then cmd /c rmdir /s /q $(BUILD); fi

.PHONY: all build flash earse clean clean_all

-include $(wildcard $(BUILD)/*.d)