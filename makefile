TARGET = blinky
CTRL = OPENCPLC_UNO
FW = opencplc
PRO = projects\\blinky
BUILD = build
OPT = Og
FAMILY = STM32G0C1xx 
DEVELOP = False 

C_SOURCES = \
$(FW)/inc/int.c $(FW)/inc/startup.c $(FW)/inc/ST/syscalls.c $(FW)/inc/ST/sysmem.c \
$(FW)/inc/ST/system_stm32g0xx.c $(FW)/lib/dev/bash.c $(FW)/lib/dev/dbg.c $(FW)/lib/dev/stream.c \
$(FW)/lib/ext/buff.c $(FW)/lib/ext/eeprom.c $(FW)/lib/ext/exbit.c $(FW)/lib/ext/exmath.c \
$(FW)/lib/ext/exstring.c $(FW)/lib/ext/extime.c $(FW)/lib/ext/file.c $(FW)/lib/ext/var.c \
$(FW)/lib/ifc/i2c-master.c $(FW)/lib/ifc/i2c-slave.c $(FW)/lib/ifc/i2c.c $(FW)/lib/ifc/spi-master.c \
$(FW)/lib/ifc/spi.c $(FW)/lib/ifc/uart.c $(FW)/lib/per/adc.c $(FW)/lib/per/crc.c $(FW)/lib/per/flash.c \
$(FW)/lib/per/gpio.c $(FW)/lib/per/pwm.c $(FW)/lib/per/pwr.c $(FW)/lib/per/rng.c $(FW)/lib/per/rtc.c \
$(FW)/lib/per/tim.c $(FW)/lib/sys/new.c $(FW)/lib/sys/vrts.c $(FW)/plc/app/hd44780.c \
$(FW)/plc/brd/opencplc-uno.c $(FW)/plc/com/modbus-master.c $(FW)/plc/com/modbus-slave.c \
$(FW)/plc/com/one-wire.c $(FW)/plc/per/ain.c $(FW)/plc/per/din.c $(FW)/plc/per/dout.c \
$(FW)/plc/per/max31865.c $(FW)/plc/per/pwmi.c $(FW)/plc/per/rgb.c $(FW)/plc/utils/cron.c \
$(FW)/plc/utils/timer.c projects/blinky/main.c 

ASM_SOURCES = \
$(FW)/lib/sys/vrts-pendsv.s 

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

C_INCLUDES = \
-I$(FW)/inc -I$(FW)/inc/CMSIS -I$(FW)/inc/ST -I$(FW)/lib/dev -I$(FW)/lib/ext -I$(FW)/lib/ifc \
-I$(FW)/lib/per -I$(FW)/lib/sys -I$(FW)/plc/app -I$(FW)/plc/brd -I$(FW)/plc/com -I$(FW)/plc/per \
-I$(FW)/plc/utils -Iprojects/blinky 

ASFLAGS = $(MCU) $(AS_DEFS) $(ASM_INCLUDES) -$(OPT) -Wall -fdata-sections -ffunction-sections
CFLAGS = $(MCU) $(C_DEFS) $(C_INCLUDES) -$(OPT) -Wall -fdata-sections -ffunction-sections
CFLAGS += -g -gdwarf-2 # DEBUG
CFLAGS += -MMD -MP -MF"$(@:%.o=%.d)"

CFLAGS += -MMD -MP -MF"$(@:%.o=%.d)"

LDSCRIPT = projects/app/flash.ld

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

earse:
	openocd -f interface/stlink.cfg -f target/stm32g0x.cfg -c "init; halt; stm32g0x mass_erase 0; reset; exit"

clean:
	cmd /c del /q $(BUILD)\\$(TARGET).* && \
	ifeq ($(DEVELOP), True)
		if [ -d "$(BUILD)\\$(FW)" ]; then cmd /c rmdir /s /q $(BUILD)\\$(FW); fi && \
	endif
	if [ -d "$(BUILD)\\$(PRO)" ]; then cmd /c rmdir /s /q $(BUILD)\\$(PRO); fi

clean_all:
	if [ -d "$(BUILD)" ]; then cmd /c rmdir /s /q $(BUILD); fi

.PHONY: all build flash earse clean clean_all

-include $(wildcard $(BUILD)/$(TARGET).d)
ifeq ($(DEVELOP), True)
  -include $(wildcard $(BUILD)/$(FW)/*.d)
endif
-include $(wildcard $(BUILD)/$(PRO)/*.d)