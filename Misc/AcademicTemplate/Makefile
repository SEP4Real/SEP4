# Makefile for Academic Template
# Requires pandoc (optional: pagedjs-cli for professional PDFs)

# SRC is provided as an absolute path from VS Code task
SRC ?= handin.md
ABS_SRC := $(abspath $(SRC))

TEMPLATE_DIR := $(dir $(lastword $(MAKEFILE_LIST)))
ABS_TEMPLATE_DIR := $(abspath $(TEMPLATE_DIR))/

CSS := $(ABS_TEMPLATE_DIR)academic.css
BIB := $(ABS_TEMPLATE_DIR)bibliography.bib
TEMPLATE := $(ABS_TEMPLATE_DIR)template.html

# Output is in the same directory as the source file
OUT := $(basename $(ABS_SRC))

.PHONY: all clean html pdf

all: html

# Enhanced Pandoc Flags for Academic Reports:
# --template: Use our custom layout for cover and TOC
# --toc: Automatically generate TOC from headers
# --toc-depth: Include up to level 3 headers in TOC
# --embed-resources: Bundle all images and CSS into the HTML
# --mathjax: Best for HTML rendering of LaTeX
# --citeproc: Citations
# --highlight-style=tango: Clean, high-contrast academic theme for code
html: $(ABS_SRC) $(CSS) $(TEMPLATE)
	pandoc "$(ABS_SRC)" \
		--template="$(TEMPLATE)" \
		--toc \
		--toc-depth=3 \
		--standalone \
		--embed-resources \
		--mathml \
		--citeproc \
		--bibliography="$(BIB)" \
		-c "$(CSS)" \
		--lua-filter="$(ABS_TEMPLATE_DIR)pagebreak.lua" \
		--highlight-style=tango \
		-f markdown+task_lists+tex_math_dollars+raw_attribute \
		-o "$(OUT).html"
	@echo "Generated $(OUT).html using centralized template"

pdf: html
	@if command -v weasyprint > /dev/null; then \
		weasyprint "$(OUT).html" "$(OUT).pdf"; \
		echo "Generated $(OUT).pdf using WeasyPrint."; \
	elif command -v pagedjs-cli > /dev/null; then \
		pagedjs-cli "$(OUT).html" -o "$(OUT).pdf"; \
		echo "Generated $(OUT).pdf using pagedjs-cli."; \
	else \
		echo "Neither 'weasyprint' nor 'pagedjs-cli' found."; \
		exit 1; \
	fi

clean:
	rm -f "$(OUT).html" "$(OUT).pdf"
