#!/bin/bash

# Exit on error
set -e

# Base directory of the repository
REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Checking dependencies..."
if ! command -v pandoc &> /dev/null; then
    echo "Error: 'pandoc' is not installed."
    echo "Please install pandoc (e.g. 'sudo apt install pandoc' on Debian/Ubuntu)."
    exit 1
fi

if ! command -v weasyprint &> /dev/null; then
    echo "Error: 'weasyprint' is not installed."
    echo "Please install weasyprint (e.g. 'pip install weasyprint' or check your PATH)."
    exit 1
fi

echo "Compiling Process Report..."
make -f "${REPO_DIR}/Misc/AcademicTemplate/Makefile" SRC="${REPO_DIR}/Documentation/ProcessReport/process-report.md" pdf
rm -f "${REPO_DIR}/Documentation/ProcessReport/process-report.html"

echo "Running Appendices Generator..."
python3 "${REPO_DIR}/Misc/AcademicTemplate/generate_appendices_list.py"

echo "Compiling Project Report..."
make -f "${REPO_DIR}/Misc/AcademicTemplate/Makefile" SRC="${REPO_DIR}/Documentation/ProjectReport/project-report.md" pdf
rm -f "${REPO_DIR}/Documentation/ProjectReport/project-report.html"

# Merge Reports into a single PDF
if command -v pdfunite &> /dev/null; then
    echo "Merging reports into a single PDF for final hand-in..."
    pdfunite "${REPO_DIR}/Documentation/ProjectReport/project-report.pdf" \
              "${REPO_DIR}/Documentation/ProcessReport/process-report.pdf" \
              "${REPO_DIR}/Documentation/StudyHelper_Final_Handin.pdf"
    echo "Merged report created: ${REPO_DIR}/Documentation/StudyHelper_Final_Handin.pdf"
else
    echo "Warning: 'pdfunite' is not installed. Reports could not be merged automatically."
    echo "Please install poppler-utils to enable merging."
fi

echo "----------------------------------------"
echo "Success! Reports compiled and intermediate HTML files cleaned up."
echo "Created:"
echo " - ${REPO_DIR}/Documentation/ProcessReport/process-report.pdf"
echo " - ${REPO_DIR}/Documentation/ProjectReport/project-report.pdf"
if [ -f "${REPO_DIR}/Documentation/StudyHelper_Final_Handin.pdf" ]; then
    echo " - ${REPO_DIR}/Documentation/StudyHelper_Final_Handin.pdf (Merged Hand-in File)"
fi
