# lybrary name
TARGET = libpymetranet.so

# object dir
OBJ_DIR = obj
DIST_DIR = dist
COPY_DIR = ../examples

# source files and headers
SRC = lzw.c bitx.c version.c
OBJ = $(SRC:%.c=$(OBJ_DIR)/%.o)  # objects files (.o)
HEADERS = lzw.h bitx.h

# compiling options
DEBUG_FLAGS = -Wall -Wextra -Og -g -fPIC  # options to build in debug mode
RELEASE_FLAGS = -Wall -Wextra -O3 -fPIC  # options to build in release mode
CFLAGS = $(RELEASE_FLAGS) # this is the default

# commands
CC = gcc
LD = gcc
LDFLAGS = -shared

# default compilation rule
all: Release

# Debug compilation rule
Debug: CFLAGS = $(DEBUG_FLAGS)
Debug: $(DIST_DIR)/$(TARGET)

# Release compilation rule
Release: CFLAGS = $(RELEASE_FLAGS)
Release: $(DIST_DIR)/$(TARGET)

# rule for the creation of the library
$(DIST_DIR)/$(TARGET): $(OBJ)
	@mkdir -p $(DIST_DIR)
	$(LD) $(LDFLAGS) -o $@ $(OBJ)
	cp -p $(DIST_DIR)/$(TARGET) $(COPY_DIR)/

# rule to create object files
$(OBJ_DIR)/%.o: %.c $(HEADERS)
	@mkdir -p $(OBJ_DIR)
	$(CC) $(CFLAGS) -c $< -o $@

# cleaning of the generated files
clean:
	rm -f $(OBJ_DIR)/*.o $(DIST_DIR)/$(TARGET)
	rmdir $(OBJ_DIR) 2>/dev/null || true
	rmdir $(DIST_DIR) 2>/dev/null || true

# show message
.PHONY: all clean Debug Release
