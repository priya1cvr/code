#!/bin/bash

# Input YAML file
INPUT_FILE="test.yml"
OUTPUT_FILE="updated_test.yml"

# Initialize variables
inside_outputs=0
inside_job=0
add_policy=0

# Process the input YAML file
awk '
{
    if ($0 ~ /outputs:/) {
        inside_outputs = 1
        inside_job = 1
    }

    if (inside_outputs == 1 && $0 ~ /stage: intermediate_dataset/) {
        add_policy = 1
    }

    # If we are at the end of an outputs section, reset the flags
    if (inside_outputs == 1 && $0 ~ /^ *- job:/) {
        inside_outputs = 0
        inside_job = 0
        add_policy = 0
    }

    # Print the current line
    print $0

    # If we need to add the policy after stage: intermediate_dataset
    if (add_policy == 1 && $0 ~ /stage: intermediate_dataset/) {
        print "      policy:"
        print "        retention_days: 30"
        add_policy = 0
    }

}
' "$INPUT_FILE" > "$OUTPUT_FILE"

echo "Updated YAML saved to $OUTPUT_FILE"
