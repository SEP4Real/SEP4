#!/bin/bash
# Setup script for CI/CD environments (Ubuntu/Debian)

# 1. Install Pandoc for MD to HTML
sudo apt-get update && sudo apt-get install -y pandoc

# 2. Install WeasyPrint and its dependencies
sudo apt-get install -y python3-pip python3-setuptools python3-wheel python3-cffi libcairo2 libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf2.0-0 libffi-dev shared-mime-info

# 3. Install WeasyPrint via Pip
pip3 install weasyprint --user

# Add to path if needed (standard for many CIs)
export PATH=$PATH:~/.local/bin

# 4. Verify installation
pandoc --version
weasyprint --version
