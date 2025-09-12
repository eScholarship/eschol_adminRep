#!/bin/bash

# Path to your CSV file
csv_file="etd_dept_report.txt"

# Loop through each line, extract the first column (ID), and run a command
while IFS=',' read -r id _; do
    # Skip header if needed
    if [[ "$id" == "id" ]]; then
        continue
    fi

    # Replace this with your actual command
    echo "Running command with ID: $id"
    erepredo index "$id"

done < "$csv_file"

