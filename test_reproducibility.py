"""
Reproducibility Verification Script
Runs main.py 3 consecutive times and asserts identical output hashes.
"""

import hashlib
import subprocess
import os

def get_file_hash(filepath):
    hasher = hashlib.sha256()
    with open(filepath, 'rb') as f:
        hasher.update(f.read())
    return hasher.hexdigest()

def main():
    print("Testing Reproducibility across 3 independent executions...")
    hashes = []
    
    for i in range(1, 4):
        # Run main.py
        result = subprocess.run(["python", "main.py"], capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Run {i} failed: {result.stderr}")
            return
        
        h = get_file_hash("output.csv")
        hashes.append(h)
        print(f"Run {i}: output.csv SHA256 = {h}")
        
    if len(set(hashes)) == 1:
        print("\n[VERIFICATION PASSED] All 3 runs produced 100% BIT-FOR-BIT IDENTICAL outputs!")
        with open("reproducibility_proof.txt", "w") as f:
            f.write("Reproducibility Verification Result:\n")
            f.write("=" * 45 + "\n")
            f.write("Runs: 3\n")
            f.write(f"Run 1 SHA256: {hashes[0]}\n")
            f.write(f"Run 2 SHA256: {hashes[1]}\n")
            f.write(f"Run 3 SHA256: {hashes[2]}\n")
            f.write("Status: PASSED (Exact Match across all runs)\n")
    else:
        print("\n[VERIFICATION FAILED] Hashes do not match!")

if __name__ == "__main__":
    main()
