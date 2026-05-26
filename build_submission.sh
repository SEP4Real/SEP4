#!/usr/bin/env bash

# Exit on error
set -e

# Base directory of the repository
REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "================================================================="
echo "         StudyHelper Final submission build & packaging"
echo "================================================================="
echo

# 1. Compile and Merge Reports
echo "Step 1: Compiling reports and merging into primary PDF..."
"${REPO_DIR}/compile_docs.sh"
echo "Done Step 1."
echo

# 2. Export PNG Diagrams to PDF
echo "Step 2: Exporting PNG diagrams to PDF..."
if [ -f "${REPO_DIR}/Misc/AcademicTemplate/export_diagrams.py" ]; then
    python3 "${REPO_DIR}/Misc/AcademicTemplate/export_diagrams.py"
else
    echo "Warning: export_diagrams.py not found at expected path. Skipping PNG-to-PDF conversion."
fi
echo "Done Step 2."
echo

# 3. Create Staging Directory for ZIP
echo "Step 3: Assembling ZIP file with requested structure..."
STAGING_DIR="${REPO_DIR}/build_staging"

# Clean up staging if it exists
rm -rf "${STAGING_DIR}"
mkdir -p "${STAGING_DIR}/Appendices"
mkdir -p "${STAGING_DIR}/source_code"

# Copy final handin PDF to root of ZIP
if [ -f "${REPO_DIR}/Documentation/StudyHelper_Final_Handin.pdf" ]; then
    cp "${REPO_DIR}/Documentation/StudyHelper_Final_Handin.pdf" "${STAGING_DIR}/StudyHelper_Final_Handin.pdf"
else
    echo "Error: StudyHelper_Final_Handin.pdf not found. Cannot package submission."
    exit 1
fi

# Copy appendices contents
if [ -d "${REPO_DIR}/Documentation/Appendices" ]; then
    # Use cp -r while avoiding errors if the directory is empty (except for README)
    cp -r "${REPO_DIR}/Documentation/Appendices/"* "${STAGING_DIR}/Appendices/" || true
fi

# Copy source code files and folders (excluding documentation and caches)
echo "Copying source code folders..."
for dir in API Frontend IOT IOT_backend MAL initdb; do
    if [ -d "${REPO_DIR}/${dir}" ]; then
        cp -r "${REPO_DIR}/${dir}" "${STAGING_DIR}/source_code/"
    fi
done

echo "Copying root-level files..."
for file in README.md compile_docs.sh build_submission.sh .env.example docker-compose.yml docker-compose.local.yml .gitignore .gitattributes; do
    if [ -f "${REPO_DIR}/${file}" ]; then
        cp "${REPO_DIR}/${file}" "${STAGING_DIR}/source_code/"
    fi
done

# Clean up build caches / environment dirs inside staging to keep zip small
rm -rf "${STAGING_DIR}/source_code/Frontend/node_modules"
rm -rf "${STAGING_DIR}/source_code/MAL/.venv"
rm -rf "${STAGING_DIR}/source_code/MAL/__pycache__"

# Create the final ZIP from within the staging directory
ZIP_NAME="StudyHelper_Final_Handin.zip"
ZIP_PATH="${REPO_DIR}/${ZIP_NAME}"
if [ -f "${ZIP_PATH}" ]; then
    echo "Removing old submission ZIP file: ${ZIP_NAME}"
    rm -f "${ZIP_PATH}"
fi

echo "Compressing files into ${ZIP_NAME}..."
(cd "${STAGING_DIR}" && zip -r "${ZIP_PATH}" . \
    -x "*/node_modules/*" \
    -x "*/.venv/*" \
    -x "*/.pytest_cache/*" \
    -x "*/.pio/*" \
    -x "*/dist/*" \
    -x "*/build/*" \
    -x "*/.git/*" \
    -x "*/__pycache__/*" \
    -x "*.pyc" \
    -x "*.pyo" \
    -x "*/.DS_Store" \
    -x "*.swp")

# Clean up staging directory
rm -rf "${STAGING_DIR}"

echo "Done Step 3."
echo

echo "================================================================="
echo "Build Successful!"
echo "Created Hand-in Deliverables:"
echo " 1. PRIMARY FILE (PDF):"
echo "    -> ${REPO_DIR}/Documentation/StudyHelper_Final_Handin.pdf"
echo " 2. APPENDICES & SOURCE CODE (ZIP):"
echo "    -> ${ZIP_PATH}"
echo "================================================================="
echo "Both files are now located in your workspace and ready for upload!"

