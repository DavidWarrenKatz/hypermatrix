#!/bin/bash

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

# Import the parameters from config.py (relative to the script's directory)
eval "$(python3 "$SCRIPT_DIR/../../../export_config.py")"

# Define the file paths
filtered_bam_list="$filtered_list"
missing_prefixes="$output_directory/missing_prefixes.txt"
temp_file="$output_directory/filtered_bam_list_updated.txt"

# Check if any symbolic links already exist in the output directory
if ls "$output_directory"/*.bam &>/dev/null; then
    echo "Symbolic links already exist in $output_directory. Skipping filtering and symbolic link creation steps."
else
    # Check if missing_prefixes.txt exists and is not empty
    if [[ -s "$missing_prefixes" ]]; then
        # Read missing prefixes into an array
        readarray -t missing < "$missing_prefixes"

        # Create a temporary file to store updated prefixes
        : > "$temp_file"  # Create or clear the file if it exists

        # Process each prefix in the filtered_bam_list.txt
        while IFS= read -r prefix; do
            # Check if the current prefix is in the missing prefixes list
            if [[ ! " ${missing[*]} " =~ " ${prefix} " ]]; then
                echo "$prefix" >> "$temp_file"
            fi
        done < "$filtered_bam_list"

        # Move the updated list back to the original file
        mv "$temp_file" "$filtered_bam_list"

        echo "Updated $filtered_bam_list by removing prefixes listed in $missing_prefixes."
    else
        echo "$missing_prefixes does not exist or is empty. No changes made to $filtered_bam_list."
    fi

    # Create symbolic links to BAM files in the output directory based on the filtered list
    while read -r identifier; do
        if [ ! -L "$output_directory/$identifier.bam" ]; then
            ln -s "$bam_directory/$identifier.$reference_genome.calmd.bam" "$output_directory/$identifier.bam"
        fi
    done < "$filtered_list"
    echo "Symbolic links created in $output_directory based on $filtered_list."
fi





