#!/usr/bin/env python
"""Simple test to verify ml_system structure is valid."""

import os
import sys
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent.parent))

print("\nValidating ML System Structure...\n")
print("="*70)

# Test 1: Check directories
print("\n1. CHECKING DIRECTORIES")
print("-"*70)

required_dirs = [
    "ml_system",
    "ml_system/config",
    "ml_system/training", 
    "ml_system/inference",
    "ml_system/learning",
    "ml_system/models/current",
    "ml_system/models/versions",
    "ml_system/data/datasets",
]

base = Path(__file__).parent.parent
all_dirs_ok = True

for d in required_dirs:
    p = base / d
    exists = p.exists()
    status = "OK" if exists else "MISSING"
    print(f"  {d:40} {status}")
    if not exists:
        all_dirs_ok = False

# Test 2: Check Python modules
print("\n2. CHECKING PYTHON MODULES")
print("-"*70)

modules_to_check = [
    "ml_system",
    "ml_system.config.settings",
    "ml_system.schemas",
    "ml_system.training.tokenizer",
    "ml_system.training.models",
    "ml_system.training.trainer",
    "ml_system.inference.engine",
    "ml_system.learning.orchestrator",
    "ml_system.api",
]

all_imports_ok = True

for module_name in modules_to_check:
    try:
        __import__(module_name)
        print(f"  {module_name:40} OK")
    except Exception as e:
        print(f"  {module_name:40} FAILED: {str(e)[:30]}")
        all_imports_ok = False

# Test 3: Check main API
print("\n3. CHECKING API")
print("-"*70)

api_ok = False
try:
    from ml_system.api import get_ml_system
    ml = get_ml_system()
    print(f"  get_ml_system()                      OK")
    print(f"  MLSystem instance created            OK")
    
    # Check methods exist
    methods = ['predict', 'submit_feedback', 'get_status', 'train']
    for method in methods:
        if hasattr(ml, method):
            print(f"    - {method}                         OK")
        else:
            print(f"    - {method}                         MISSING")
            all_imports_ok = False
    
    api_ok = True
except Exception as e:
    print(f"  API check failed: {e}")

# Test 4: Check config
print("\n4. CHECKING CONFIG")
print("-"*70)

config_ok = False
try:
    from ml_system.config.settings import CONFIG
    
    attrs = [
        ('base_dir', CONFIG.base_dir),
        ('data_dir', CONFIG.data_dir),
        ('models_dir', CONFIG.models_dir),
        ('confidence_threshold', CONFIG.confidence_threshold),
        ('min_feedback_for_retraining', CONFIG.min_feedback_for_retraining),
    ]
    
    for name, value in attrs:
        print(f"  CONFIG.{name:35} = {value}")
    
    config_ok = True
except Exception as e:
    print(f"  Config check failed: {e}")

# Summary
print("\n" + "="*70)
print("SUMMARY")
print("="*70)

all_ok = all_dirs_ok and all_imports_ok and api_ok and config_ok

print(f"\nDirectories:      {'OK' if all_dirs_ok else 'ISSUES'}")
print(f"Imports:          {'OK' if all_imports_ok else 'ISSUES'}")
print(f"API:              {'OK' if api_ok else 'ISSUES'}")
print(f"Config:           {'OK' if config_ok else 'ISSUES'}")

if all_ok:
    print("\n✅ Structure validation PASSED")
    print("\nYou can now:")
    print("  1. Train with ml_system.api.get_ml_system().train(...)")
    print("  2. Use backend endpoints /predict, /feedback, /learning-status")
    exit(0)
else:
    print("\n❌ Structure validation FAILED - see issues above")
    exit(1)
