import sys
import os

print("Current Working Directory:", os.getcwd())
print("Python Module Search Paths:")
for path in sys.path:
    print(path)
