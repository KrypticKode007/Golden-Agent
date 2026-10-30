import sys
import os

# Dynamically append the sister repository location to the environment path
sys.path.append(os.path.abspath("../Offline-Conscious-Drone-"))
from unified_conscious_agent import initialize_monolith_pipeline
