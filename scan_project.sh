#!/bin/bash

# Automatically determine the project directory based on current working directory
PROJECT_DIR="$(pwd)"

# Define the core files and directories you want to analyze
CORE_FILES=("execution_adapter.py" "tool_executor.py" "task_service_v2.py" "ops_agent.py")
CORE_DIRS=("execution" "agents" "core/task")

# Create a directory to store the output logs
OUTPUT_DIR="$PROJECT_DIR/project_analysis"
mkdir -p "$OUTPUT_DIR"

# Step 1: Scan project directories and list all files
echo "Scanning project directories for relevant files..."

for dir in "${CORE_DIRS[@]}"; do
  echo "Scanning directory: $PROJECT_DIR/$dir"
  find "$PROJECT_DIR/$dir" -type f -name "*.py" > "$OUTPUT_DIR/files_in_${dir//\//_}.txt"
done

# Step 2: Check if core files exist and output their content
echo "Checking for core files and generating summaries..."

for file in "${CORE_FILES[@]}"; do
  FILE_PATH=$(find "$PROJECT_DIR" -type f -name "$file")
  
  if [ -z "$FILE_PATH" ]; then
    echo "File not found: $file" >> "$OUTPUT_DIR/missing_files.log"
  else
    echo "Found file: $FILE_PATH"
    echo "Summary of $file:" >> "$OUTPUT_DIR/summaries.txt"
    head -n 20 "$FILE_PATH" >> "$OUTPUT_DIR/summaries.txt"  # Show the first 20 lines as a summary
    echo "----------------------------------" >> "$OUTPUT_DIR/summaries.txt"
  fi
done

# Step 3: Output the full project directory structure
echo "Generating full project directory structure..."

# Check if `tree` is installed, if not, use `find` instead
if command -v tree > /dev/null; then
  tree "$PROJECT_DIR" > "$OUTPUT_DIR/project_directory_structure.txt"
else
  find "$PROJECT_DIR" -type d > "$OUTPUT_DIR/project_directory_structure.txt"
fi

echo "Project directory analysis completed. Outputs saved in $OUTPUT_DIR"

# Optional: Print all the results to the terminal
cat "$OUTPUT_DIR/files_in_execution.txt"
cat "$OUTPUT_DIR/files_in_agents.txt"
cat "$OUTPUT_DIR/files_in_task.txt"
cat "$OUTPUT_DIR/summaries.txt"
