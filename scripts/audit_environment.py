#!/usr/bin/env python3
import sys
import importlib

def audit_requirements():
    """
    Checks the local Python environment for required core libraries
    and handles diagnostic output formatting.
    """
    critical_packages = [
        "fastapi",
        "uvicorn",
        "requests",
        "cryptography",
        "psutil",
        "pytest"
    ]
    
    print("[+] Initializing Dependency Environment Audit...")
    missing_count = 0
    
    for package in critical_packages:
        try:
            mod = importlib.import_module(package)
            version = getattr(mod, "__version__", "Unknown Version")
            print(f"    -> [PASSED] Found module: {package:<15} (Version: {version})")
        except ImportError:
            print(f"    -> [FAILED] Missing core dependency: {package}")
            missing_count += 1
            
    if missing_count > 0:
        print(f"\n[-] Audit complete: {missing_count} dependencies are uninstalled.")
        print("    Run: pip install -r requirements.txt")
        sys.exit(1)
    else:
        print("\n[+] Success: Local environment is fully synchronized and compliant.")

if __name__ == "__main__":
    audit_requirements()
  
