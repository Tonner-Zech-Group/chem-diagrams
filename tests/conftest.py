import sys
import os

# Ensure the src directory is on the path so pytest can find chemdiagrams
# without requiring an editable install.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
