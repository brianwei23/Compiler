import os
import subprocess
import sys

# Check if rat25s_parser.py exists
if not os.path.exists("rat25s_parser.py"):
    print("Error: rat25s_parser.py not found in the current directory")
    sys.exit(1)

# List of test files to run
test_files = [
    "test_case1.txt",
    "test_case2.txt",
    "test_case3.txt"
]

# Run each test file
for test_file in test_files:
    if not os.path.exists(test_file):
        print(f"Warning: Test file {test_file} not found, skipping")
        continue
    
    output_file = f"output_{test_file.replace('.txt', '')}.txt"
    print(f"Running parser on {test_file} -> {output_file}")
    
    # Run the parser with the test file
    cmd = ["python", "rat25s_parser.py", test_file, output_file]
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(f"Success: {result.stdout}")
    except subprocess.CalledProcessError as e:
        print(f"Error running parser: {e}")
        print(f"Output: {e.stdout}")
        print(f"Error: {e.stderr}")
    except Exception as e:
        print(f"Unexpected error: {e}")
    
    print("-" * 50)

print("All tests completed")