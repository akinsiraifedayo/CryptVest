#!/bin/bash

# Script to source .bashrc

# Define the path to your .bashrc file
BASHRC_FILE=~/.bashrc

# Check if the .bashrc file exists
if [ -f "$BASHRC_FILE" ]; then
    # Source the .bashrc file
    source "$BASHRC_FILE"
    echo "Successfully sourced $BASHRC_FILE"
else
    echo "$BASHRC_FILE does not exist."
fi

