#!/bin/bash

# Commit script following Conventional Commits specification

# Error handling
set -e

# Colors for better readability
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if git is available
if ! command -v git &> /dev/null; then
    echo -e "${RED}Error: git is not installed${NC}"
    exit 1
fi

# Check if we're in a git repository
if ! git rev-parse --is-inside-work-tree &> /dev/null; then
    echo -e "${RED}Error: not in a git repository${NC}"
    exit 1
fi

# Check if there are any changes to commit
if [[ -z $(git status -s) ]]; then
    echo -e "${YELLOW}No changes to commit.${NC}"
    exit 0
fi

# Function to get commit input
get_commit_input() {
    # Show commit types with examples
    echo -e "\n${BLUE}Step 1/4: Select commit type${NC}"
    echo "Available types:"
    echo -e "  ${GREEN}feat${NC}     - New feature"
    echo -e "  ${GREEN}fix${NC}      - Bug fix"
    echo -e "  ${GREEN}docs${NC}     - Documentation"
    echo -e "  ${GREEN}style${NC}    - Code style"
    echo -e "  ${GREEN}refactor${NC} - Code changes"
    echo -e "  ${GREEN}perf${NC}     - Performance"
    echo -e "  ${GREEN}test${NC}     - Testing"
    echo -e "  ${GREEN}chore${NC}    - Maintenance"
    echo -e "  ${GREEN}ci${NC}       - CI/CD changes"

    # Get commit type
    while true; do
        read -r -p "Type> " commit_type
        commit_type=$(echo "$commit_type" | tr -d '[:space:]')
        if [[ " feat fix docs style refactor perf test chore ci " =~ " $commit_type " ]]; then
            break
        fi
        echo -e "${RED}Invalid type. Please select from the list above.${NC}"
    done

    # Get commit scope (optional)
    echo -e "\n${BLUE}Step 2/4: Enter scope${NC} ${YELLOW}(optional, press Enter to skip)${NC}"
    echo "Examples: ui, api, auth"
    read -r -p "Scope(Optional)> " commit_scope

    # Get commit subject
    echo -e "\n${BLUE}Step 3/4: Enter description${NC}"
    echo "Example: add login button to homepage"
    while true; do
        read -r -p "Description> " commit_subject
        if [[ -z "$commit_subject" ]]; then
            echo -e "${RED}Description cannot be empty. Please try again.${NC}"
        elif [[ ${#commit_subject} -gt 72 ]]; then
            echo -e "${RED}Description too long (max 72 chars). Please try again.${NC}"
        else
            break
        fi
    done

    # Get commit body (optional)
    echo -e "\n${BLUE}Step 4/4: Enter detailed description${NC} ${YELLOW}(optional, press Enter to skip)${NC}"
    read -r commit_body

    # Construct commit message
    if [[ -n "$commit_scope" ]]; then
        commit_message="${commit_type}(${commit_scope}): ${commit_subject}"
    else
        commit_message="${commit_type}: ${commit_subject}"
    fi

    if [[ -n "$commit_body" ]]; then
        commit_message="${commit_message}

${commit_body}"
    fi

    echo "$commit_message"
}

# Main commit process
echo -e "${BLUE}Current changes:${NC}"
git status
echo

# Get commit message
full_commit_message=$(get_commit_input)

# Confirm commit
echo -e "\n${BLUE}Review your commit message:${NC}"
echo -e "${GREEN}$full_commit_message${NC}"
read -r -p "Commit these changes? (y/N)> " confirm

if [[ "$confirm" =~ ^[Yy] ]]; then
    # Stage all changes
    git add . || { echo -e "${RED}Error: Failed to stage changes${NC}"; exit 1; }

    # Commit with the constructed message
    git commit -m "$full_commit_message" || { echo -e "${RED}Error: Failed to commit changes${NC}"; exit 1; }

    # Ask about pushing changes
    echo -e "\n${BLUE}Would you like to push these changes? (y/N)${NC}"
    read -r -p "Push> " should_push
    if [[ "$should_push" =~ ^[Yy] ]]; then
        current_branch=$(git branch --show-current)
        echo -e "${YELLOW}Pushing to ${current_branch}...${NC}"
        git push origin "$current_branch" || { echo -e "${RED}Error: Failed to push changes${NC}"; exit 1; }
        echo -e "${GREEN}Push successful!${NC}"
    fi

    echo -e "${GREEN}Commit successful!${NC}"
else
    echo -e "${YELLOW}Commit cancelled.${NC}"
fi
