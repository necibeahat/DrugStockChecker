#!/usr/bin/env python3
"""Verification script to check project setup."""

import sys
from pathlib import Path

def check_dependencies():
    """Check if all required dependencies are available."""
    required_packages = [
        'strands',
        'chromadb', 
        'streamlit',
        'pandas',
        'boto3',
        'pydantic',
        'pytest',
        'hypothesis'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✓ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"✗ {package}")
    
    return len(missing_packages) == 0

def check_project_structure():
    """Check if project structure is correct."""
    required_dirs = [
        'src/agents',
        'src/tools', 
        'src/data_processing',
        'src/frontend',
        'src/models',
        'src/config',
        'tests',
        'data'
    ]
    
    missing_dirs = []
    
    for dir_path in required_dirs:
        if Path(dir_path).exists():
            print(f"✓ {dir_path}/")
        else:
            missing_dirs.append(dir_path)
            print(f"✗ {dir_path}/")
    
    return len(missing_dirs) == 0

def check_config_files():
    """Check if configuration files exist."""
    required_files = [
        'requirements.txt',
        'pyproject.toml',
        'pytest.ini',
        '.env.example',
        'README.md',
        'setup.py'
    ]
    
    missing_files = []
    
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"✓ {file_path}")
        else:
            missing_files.append(file_path)
            print(f"✗ {file_path}")
    
    return len(missing_files) == 0

def main():
    """Main verification function."""
    print("🔍 Verifying Pharmaceutical Intelligence Chatbot Setup")
    print("=" * 60)
    
    print("\n📦 Checking Dependencies:")
    deps_ok = check_dependencies()
    
    print("\n📁 Checking Project Structure:")
    structure_ok = check_project_structure()
    
    print("\n📄 Checking Configuration Files:")
    config_ok = check_config_files()
    
    print("\n" + "=" * 60)
    
    if deps_ok and structure_ok and config_ok:
        print("✅ Project setup verification PASSED!")
        print("\nNext steps:")
        print("1. Copy .env.example to .env and configure your settings")
        print("2. Start ChromaDB: chroma run --host localhost --port 8000")
        print("3. Run data ingestion: python -m src.data_processing.ingest")
        print("4. Start the chatbot: streamlit run src/frontend/app.py")
        return 0
    else:
        print("❌ Project setup verification FAILED!")
        print("Please fix the missing components above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())