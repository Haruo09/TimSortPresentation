CC = gcc
CFLAGS = -Wall -Wextra -O3 -fPIC -Iinclude
BUILD_DIR = build
OBJ_DIR = $(BUILD_DIR)/obj
LIB_DIR = $(BUILD_DIR)/lib
BIN_DIR = $(BUILD_DIR)/bin

# Detect Operating System & Normalize Commands
ifeq ($(OS),Windows_NT)
    TARGET_LIB = $(LIB_DIR)/timsort.dll
    TARGET_BIN = $(BIN_DIR)/timsort_c_test.exe
    FIX_PATH = $(subst /,\,$1)
    MKDIR = if not exist $(call FIX_PATH,$1) mkdir $(call FIX_PATH,$1)
    RM = if exist $(call FIX_PATH,$(BUILD_DIR)) rmdir /s /q $(call FIX_PATH,$(BUILD_DIR))
else
    TARGET_LIB = $(LIB_DIR)/libtimsort.so
    TARGET_BIN = $(BIN_DIR)/timsort_c_test
    FIX_PATH = $1
    MKDIR = mkdir -p $1
    RM = rm -rf $(BUILD_DIR)
endif

# Find all C sources in src/ (excluding main.c)
LIB_SRCS = $(filter-out src/main.c, $(wildcard src/*.c))
LIB_OBJS = $(patsubst src/%.c, $(OBJ_DIR)/%.o, $(LIB_SRCS))

all: $(TARGET_LIB) $(TARGET_BIN)

# Link dynamic shared library (.so / .dll)
$(TARGET_LIB): $(LIB_OBJS) | $(LIB_DIR)
	$(CC) -shared -o $@ $^

# Build C test binary
$(TARGET_BIN): src/main.c $(LIB_OBJS) | $(BIN_DIR)
	$(CC) $(CFLAGS) $^ -o $@

# Pattern rule for object files
$(OBJ_DIR)/%.o: src/%.c | $(OBJ_DIR)
	$(CC) $(CFLAGS) -c $< -o $@

# Create required output directories
$(BUILD_DIR) $(OBJ_DIR) $(LIB_DIR) $(BIN_DIR):
	$(call MKDIR,$@)

clean:
	$(RM)

.PHONY: all clean
