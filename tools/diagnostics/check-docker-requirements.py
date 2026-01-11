#!/usr/bin/env python3
"""
Quick Docker build test without actually building.
Validates Dockerfile and requirements before attempting full build.
"""

import subprocess
import sys
from pathlib import Path

def check_file_exists(filepath, description):
    """Check if required file exists."""
    if Path(filepath).exists():
        print(f"✅ {description}: {filepath}")
        return True
    else:
        print(f"❌ {description} MISSING: {filepath}")
        return False

def check_docker_installed():
    """Check if Docker is installed and running."""
    try:
        subprocess.run(["docker", "--version"], capture_output=True, check=True)
        print("✅ Docker is installed")
        return True
    except:
        print("❌ Docker is NOT installed or not in PATH")
        return False

def check_docker_running():
    """Check if Docker daemon is running."""
    try:
        subprocess.run(["docker", "ps"], capture_output=True, check=True, timeout=5)
        print("✅ Docker daemon is running")
        return True
    except:
        print("❌ Docker daemon is NOT running")
        print("   Start Docker Desktop or run: sudo systemctl start docker")
        return False

def check_docker_network():
    """Check if Docker container can reach the internet."""
    try:
        result = subprocess.run(
            ["docker", "run", "--rm", "alpine", "ping", "-c", "1", "8.8.8.8"],
            capture_output=True,
            timeout=10
        )
        if result.returncode == 0:
            print("✅ Docker network connectivity OK")
            return True
        else:
            print("⚠️  Docker network connectivity may be limited")
            return False
    except Exception as e:
        print(f"⚠️  Could not test Docker network: {e}")
        return None

def validate_requirements():
    """Check if requirements-backend.txt has proper syntax."""
    try:
        with open("requirements-backend.txt", "r") as f:
            lines = f.readlines()
            packages = [l.strip() for l in lines if l.strip() and not l.startswith("#")]
            print(f"✅ requirements-backend.txt has {len(packages)} packages")
            
            # Check for numpy version
            numpy_lines = [p for p in packages if p.startswith("numpy")]
            if numpy_lines:
                print(f"   └─ numpy version: {numpy_lines[0]}")
            return True
    except Exception as e:
        print(f"❌ Error reading requirements: {e}")
        return False

def main():
    print("\n" + "="*60)
    print("  Docker Build Pre-Flight Check")
    print("="*60 + "\n")

    checks = []

    # File checks
    print("📁 Required Files:")
    checks.append(check_file_exists("Dockerfile.firstperson", "Main Dockerfile"))
    checks.append(check_file_exists("Dockerfile.firstperson.resilient", "Resilient Dockerfile"))
    checks.append(check_file_exists("requirements-backend.txt", "Python requirements"))
    checks.append(check_file_exists("firstperson_backend.py", "FastAPI backend"))
    checks.append(check_file_exists("nginx.firstperson.conf", "Nginx config"))
    checks.append(check_file_exists("entrypoint.firstperson.sh", "Entrypoint script"))
    print()

    # Docker checks
    print("🐳 Docker Status:")
    docker_installed = check_docker_installed()
    docker_running = check_docker_running() if docker_installed else False
    docker_network = check_docker_network() if docker_running else False
    print()

    # Requirements check
    print("📦 Requirements:")
    validate_requirements()
    print()

    # Summary
    print("="*60)
    if all(checks) and docker_installed and docker_running:
        print("✅ All checks passed! Ready to build.")
        print("\nRun Docker build with:")
        print("  docker build -f Dockerfile.firstperson -t firstperson:latest .")
        print("\nOr use test script:")
        print("  Windows:  .\\test-docker-build.ps1")
        print("  Linux:    bash test-docker-build.sh")
        return 0
    else:
        print("⚠️  Some checks failed. Please fix issues before building.")
        if not all(checks):
            print("\nMissing required files - check workspace structure")
        if not docker_installed:
            print("\nDocker not installed - install Docker Desktop/Engine")
        if not docker_running:
            print("\nDocker not running - start Docker daemon")
        return 1

if __name__ == "__main__":
    sys.exit(main())
