CC = gcc
CFLAGS = -Wall -Wextra -O3 -fPIC -Iinclude
BUILD_DIR = build
OBJ_DIR = $(BUILD_DIR)/obj
LIB_DIR = $(BUILD_DIR)/lib
BIN_DIR = $(BUILD_DIR)/bin

# Detect Operating System
ifeq ($(OS),Windows_NT)
    TARGET_LIB = $(LIB_DIR)/timsort.dll
    TARGET_BIN = $(BIN_DIR)/timsort_c_test.exe
    RM = del /Q /F
    MKDIR = mkdir
else
    TARGET_LIB = $(LIB_DIR)/libtimsort.so
    TARGET_BIN = $(BIN_DIR)/timsort_c_test
    RM = rm -rf
    MKDIR = mkdir -p
endif

# Automatically find all library source files in src/ (excluding main.c)
LIB_SRCS = $(filter-out src/main.c, $(wildcard src/*.c))
LIB_OBJS = $(patsubst src/%.c, $(OBJ_DIR)/%.o, $(LIB_SRCS))

all: $(TARGET_LIB) $(TARGET_BIN)

# Build shared library (.so / .dll) from all compiled object files
$(TARGET_LIB): $(LIB_OBJS) | $(LIB_DIR)
	$(CC) -shared -o $@ $^

# Build test executable linking main.c with all object files
$(TARGET_BIN): src/main.c $(LIB_OBJS) | $(BIN_DIR)
	$(CC) $(CFLAGS) $^ -o $@

# Pattern rule: compile any src/*.c file into build/obj/*.o
$(OBJ_DIR)/%.o: src/%.c | $(OBJ_DIR)
	$(CC) $(CFLAGS) -c $< -o $@

$(BUILD_DIR) $(OBJ_DIR) $(LIB_DIR) $(BIN_DIR):
	$(MKDIR) $@

clean:
	$(RM) $(BUILD_DIR)

.PHONY: all clean
