#!/bin/bash

# Ignore broken pipe errors
trap '' PIPE

# Check if Node.js is installed, if not, install it
if ! command -v node &> /dev/null; then
    echo "Node.js is not installed. Installing Node.js... just using homebrew"
    if ! command -v brew &> /dev/null; then
        echo "homebrew is not installed. Installing homebrew..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    fi
    brew install node
fi

# Check Node.js version
NODE_VERSION=$(node -v | cut -d'v' -f2)
REQUIRED_VERSION="18.0.0"

if [ "$NODE_VERSION" != "$REQUIRED_VERSION" ]; then
    echo "Node.js version is not 18.0.0. Installing 18.0.0..."
    brew install node@18
    export PATH="/opt/homebrew/opt/node@18/bin:$PATH"
fi

cd frontend

# Check if yarn is installed, if not, install it
if ! command -v yarn &> /dev/null; then
    echo "yarn is not installed. Installing yarn..."
    npm install -g yarn
fi

# Install dependencies
echo "Installing dependencies..."
yarn install

# Start the app
echo "Starting the app..."
yarn dev
