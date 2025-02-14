#!/bin/bash

# Commit script following Conventional Commits specification

# Check if there are any changes to commit
if [[ -z $(git status -s) ]]; then
    echo "No changes to commit."
    exit 0
fi

# Function to get commit input
get_commit_input() {
    # Show commit types
    echo "Select commit type:"
    echo "feat:     New feature"
    echo "fix:      Bug fix"
    echo "docs:     Documentation changes"
    echo "style:    Code style changes"
    echo "refactor: Code refactoring"
    echo "perf:     Performance improvements"
    echo "test:     Adding or updating tests"
    echo "chore:    Maintenance tasks"
    echo "ci:       CI/CD changes"
    echo
    
    # Get commit type
    while true; do
        read -p "Type: " commit_type
        if [[ " feat fix docs style refactor perf test chore ci " =~ " $commit_type " ]]; then
            break
        fi
        echo "Invalid type. Please try again."
    done
    
    # Get commit subject
    echo
    read -p "Subject: " commit_subject
    
    # Get commit body
    echo
    echo "Enter commit body (optional, press Ctrl+D when finished):"
    echo "---"
    commit_body=$(cat)
    
    # Construct commit message
    commit_message="${commit_type}: ${commit_subject}"
    if [[ -n "$commit_body" ]]; then
        commit_message="${commit_message}

${commit_body}"
    fi
    
    echo "$commit_message"
}

# Main commit process
echo "Preparing to commit changes:"
git status
echo

# Get commit message
full_commit_message=$(get_commit_input)

# Confirm commit
echo -e "\nFull commit message:\n${full_commit_message}"
read -p "Confirm commit? (y/n): " confirm

if [[ "$confirm" == [yY] || "$confirm" == [yY][eE][sS] ]]; then
    # Stage all changes
    git add .
    
    # Commit with the constructed message
    git commit -m "$full_commit_message"
    
    echo "Commit successful!"
else
    echo "Commit cancelled."
fi
