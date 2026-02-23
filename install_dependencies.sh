#!/bin/bash

# This script installs required dependencies for the project.

# How to run this script:
## chmod +x install_dependencies.sh
## ./install_dependencies.sh

echo "Welcome to the installation script for the project."
echo "This script will install the required dependencies for the project, including Python, Pip, Git, Make, and Maven."
echo "Please ensure you have the necessary permissions to install software on your system."

# Ensure the Project is up-to-date
echo "Pulling the latest changes from the repository..."
git pull
echo "The project is up-to-date."

# Ensure Git submodules are initialized and updated
echo "Initializing and updating Git submodules..."
git submodule init
git submodule update
echo "Git submodules are up-to-date."

# Detect OS
OS=""
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
   OS="Linux"
elif [[ "$OSTYPE" == "darwin"* ]]; then
   OS="MacOS"
elif [[ "$OSTYPE" == "msys"* ]] || [[ "$OSTYPE" == "cygwin"* ]] || [[ "$OSTYPE" == "win32" ]]; then
   OS="Windows"
else
   echo "Unsupported OS."
   exit 1
fi

echo "Detected OS: $OS"

# Function to check if a command exists
command_exists() {
   command -v "$1" &> /dev/null
}

# Install Python and Pip
install_python_pip() {
   if command_exists python3 && command_exists pip3; then
      echo "Python and Pip are already installed."
   else
      echo "Installing Python and Pip..."
      case "$OS" in
         Linux)
            sudo apt update
            sudo apt install python3 python3-pip python3-venv -y
            ;;
         MacOS)
            # Install Python 3 using Homebrew
            brew install python
            # Ensure pip and venv are also installed with Python
            python3 -m ensurepip --upgrade
            python3 -m pip install --upgrade pip
            python3 -m pip install virtualenv
            ;;
         Windows)
            # Check if Python is installed using Chocolatey
            if ! command_exists python; then
               echo "Installing Python using Chocolatey..."
               echo "This requires Chocolatey to be installed."
               choco install python --params "/InstallDir:C:\Python39" -y
            fi
            # Ensure pip is installed
            if ! command_exists pip; then
               echo "Installing pip..."
               curl -sS https://bootstrap.pypa.io/get-pip.py | python
            fi
            # Install virtualenv
            pip install --user virtualenv
            ;;
      esac
      echo "Python and Pip installation complete."
   fi
}

# Install Make
install_make() {
   if command_exists make; then
      echo "Make is already installed."
   else
      echo "Installing Make..."
      case "$OS" in
         Linux)
            sudo apt update
            sudo apt install make -y
            ;;
         MacOS)
            brew install make
            ;;
         Windows)
            echo "Please install Make as part of a Unix-like environment (e.g., Cygwin or WSL) or download from https://www.gnu.org/software/make/#download."
            ;;
      esac
      echo "Make installation complete."
   fi
}


# Run installation functions
install_python_pip
install_make

echo "Please, check for any errors in the installation process in the log messages above."
echo "All required dependencies should now be installed."
