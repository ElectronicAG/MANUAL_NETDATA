#!/bin/bash
# clean_latex.sh - Elimina archivos temporales de LaTeX en el directorio actual (y subdirectorios)

find . \( \
    -name "*.aux" -o \
    -name "*.bbl" -o \
    -name "*.bcf" -o \
    -name "*.blg" -o \
    -name "*.fdb_latexmk" -o \
    -name "*.fls" -o \
    -name "*.log" -o \
    -name "*.out" -o \
    -name "*.run.xml" -o \
    -name "*.synctex.gz" -o \
    -name "*.bbl-SAVE-ERROR" -o \
    -name "*.bcf-SAVE-ERROR" -o \
    -name "*.toc" \
\) -type f -print -delete

echo "Limpieza completada."