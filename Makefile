APP := analizador_lexico
ENGINE := lexer_engine
BUILD_DIR := build
DIST_DIR := dist
SRC_DIR := src

FLEX := flex
CC := gcc
CFLAGS := -std=c11 -D_POSIX_C_SOURCE=200809L -Wall -Wextra -Wpedantic -g

.PHONY: all run clean dist check-deps

all: $(BUILD_DIR)/$(ENGINE)

$(BUILD_DIR):
	@mkdir -p $@

$(SRC_DIR)/lex.yy.c: $(SRC_DIR)/lexer.l
	$(FLEX) --outfile=$@ $<

$(BUILD_DIR)/$(ENGINE): $(SRC_DIR)/lex.yy.c | $(BUILD_DIR)
	$(CC) $(CFLAGS) $(SRC_DIR)/lex.yy.c -o $@

run: all
	LEXER_ENGINE=$(abspath $(BUILD_DIR)/$(ENGINE)) python3 app.py

dist: all
	@mkdir -p $(DIST_DIR)
	cp app.py $(DIST_DIR)/$(APP)
	cp $(BUILD_DIR)/$(ENGINE) $(DIST_DIR)/$(APP)_engine
	chmod +x $(DIST_DIR)/$(APP)

check-deps:
	@command -v $(FLEX) >/dev/null || (echo "Falta flex"; exit 1)
	@python3 -c 'import gi; gi.require_version("Gtk", "4.0"); gi.require_version("Adw", "1"); from gi.repository import Adw, Gtk' || (echo "Falta PyGObject, GTK 4 o Libadwaita"; exit 1)

clean:
	rm -rf $(BUILD_DIR) $(DIST_DIR) $(SRC_DIR)/lex.yy.c
