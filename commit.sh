#!/bin/bash

# Commit script following Conventional Commits specification

# Check if there are any changes to commit
if [[ -z $(git status -s) ]]; then
    echo "No changes to commit."
    exit 0
fi

# Function to prompt for commit type
select_commit_type() {
    echo "Select commit type:"
    types=("feat" "fix" "docs" "style" "refactor" "perf" "test" "chore" "ci")
    select type in "${types[@]}"; do
        if [[ " ${types[@]} " =~ " ${type} " ]]; then
            echo "$type"
            return
        fi
        echo "Invalid selection. Please try again."
    done
}

# Function to prompt for scope
select_commit_scope() {
    read -p "Enter commit scope (optional, press Enter to skip): " scope
    echo "$scope"
}

# Function to get commit subject
get_commit_subject() {
    read -p "Enter commit subject (brief description): " subject
    echo "$subject"
}

# Function to get commit body
get_commit_body() {
    echo "Enter commit body (optional, press Ctrl+D when finished):"
    body=$(cat)
    echo "$body"
}

# Main commit process
echo "Preparing to commit changes:"
git status

# Select commit type
commit_type=$(select_commit_type)

# Select commit scope
commit_scope=$(select_commit_scope)

# Get commit subject
commit_subject=$(get_commit_subject)

# Prepare scope part
if [[ -n "$commit_scope" ]]; then
    scope_part="($commit_scope)"
else
    scope_part=""
fi

# Get commit body
echo "Commit body (optional):"
commit_body=$(get_commit_body)

# Construct full commit message
full_commit_message="${commit_type}${scope_part}: ${commit_subject}"
if [[ -n "$commit_body" ]]; then
    full_commit_message="${full_commit_message}

${commit_body}"
fi

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
