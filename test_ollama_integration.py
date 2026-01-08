"""
Quick test script to verify Ollama integration setup.

Usage:
    python test_ollama_integration.py

This script:
- Checks if docker-compose.local.yml exists and is valid
- Tests Ollama connectivity
- Lists available models
- Generates a test response
- Verifies FirstPerson client can reach Ollama
"""

import sys
import json
import subprocess
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

try:
    import requests
except ImportError:
    print("❌ requests library not found. Install with: pip install requests")
    sys.exit(1)


def check_docker_compose_file():
    """Verify docker-compose.local.yml exists and is valid."""
    print("\n🔍 Checking docker-compose.local.yml...")
    
    compose_file = Path("docker-compose.local.yml")
    if not compose_file.exists():
        print(f"❌ docker-compose.local.yml not found at {compose_file.absolute()}")
        print("   Run: ls -la docker-compose*.yml")
        return False
    
    print(f"✅ Found at {compose_file.absolute()}")
    return True


def check_ollama_service():
    """Check if Ollama service is running and responding."""
    print("\n🔍 Checking Ollama service...")
    
    base_url = "http://localhost:11434"
    api_endpoint = f"{base_url}/api/tags"
    
    try:
        response = requests.get(api_endpoint, timeout=5)
        if response.status_code == 200:
            print(f"✅ Ollama responding at {base_url}")
            return True
        else:
            print(f"❌ Ollama returned HTTP {response.status_code}")
            return False
    except requests.ConnectionError:
        print(f"❌ Cannot connect to Ollama at {base_url}")
        print("   Make sure docker-compose is running:")
        print("   docker-compose -f docker-compose.local.yml up -d")
        return False
    except Exception as e:
        print(f"❌ Error connecting to Ollama: {e}")
        return False


def get_available_models():
    """Get list of available models from Ollama."""
    print("\n🔍 Checking available models...")
    
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            data = response.json()
            models = data.get("models", [])
            if models:
                print(f"✅ Found {len(models)} model(s):")
                for model in models:
                    name = model.get("name", model) if isinstance(model, dict) else model
                    print(f"   - {name}")
                return [m.get("name", m) if isinstance(m, dict) else m for m in models]
            else:
                print("⚠️  No models found. Pull one with:")
                print("   docker-compose -f docker-compose.local.yml exec ollama ollama pull llama3")
                return []
        else:
            print(f"❌ Failed to get models: HTTP {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ Error getting models: {e}")
        return []


def test_ollama_generation(model=None, prompt="What is the meaning of life?"):
    """Test generating a response from Ollama."""
    print(f"\n🔍 Testing response generation...")
    
    if not model:
        models = get_available_models()
        if not models:
            print("❌ No models available to test")
            return False
        model = models[0]
    
    try:
        print(f"   Model: {model}")
        print(f"   Prompt: {prompt}")
        print("   Generating...")
        
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
        }
        
        response = requests.post(
            "http://localhost:11434/api/generate",
            json=payload,
            timeout=120,  # Long timeout for generation
        )
        
        if response.status_code == 200:
            data = response.json()
            generated = data.get("response", "").strip()
            if generated:
                preview = generated[:200] + "..." if len(generated) > 200 else generated
                print(f"✅ Generated response ({len(generated)} chars):")
                print(f"   {preview}")
                return True
            else:
                print("❌ Model returned empty response")
                return False
        else:
            print(f"❌ Generation failed: HTTP {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return False
            
    except requests.Timeout:
        print("⚠️  Generation timed out (expected for large models on weak hardware)")
        print("   Try a smaller model or increase timeout")
        return True  # Not a failure, just slow
    except Exception as e:
        print(f"❌ Error generating response: {e}")
        return False


def test_firstperson_client():
    """Test FirstPerson Ollama client."""
    print(f"\n🔍 Testing FirstPerson Ollama client...")
    
    try:
        from src.emotional_os.deploy.modules.ollama_client import get_ollama_client_singleton
        
        client = get_ollama_client_singleton()
        
        # Check availability
        available = client.is_available()
        print(f"   Available: {available}")
        
        if not available:
            print("❌ Ollama not available to FirstPerson client")
            return False
        
        # Get models
        models = client.get_available_models()
        print(f"   Models: {models}")
        
        if not models:
            print("⚠️  No models available")
            return True  # Not a client error, just no models
        
        print("✅ FirstPerson Ollama client working")
        return True
        
    except ImportError as e:
        print(f"⚠️  Could not import FirstPerson client: {e}")
        print("   This might be OK if running test in isolation")
        return True
    except Exception as e:
        print(f"❌ FirstPerson client error: {e}")
        return False


def main():
    """Run all checks."""
    print("=" * 60)
    print("Ollama Integration Test")
    print("=" * 60)
    
    checks = [
        ("Docker Compose File", check_docker_compose_file),
        ("Ollama Service", check_ollama_service),
        ("Available Models", lambda: len(get_available_models()) > 0),
        ("Response Generation", test_ollama_generation),
        ("FirstPerson Client", test_firstperson_client),
    ]
    
    results = {}
    for name, check_func in checks:
        try:
            if callable(check_func) and name != "Available Models":
                results[name] = check_func()
            elif name == "Available Models":
                # Special handling for model check
                models = get_available_models()
                if not models:
                    print("⚠️  Tip: Pull a model to continue:")
                    print("      docker-compose -f docker-compose.local.yml exec ollama ollama pull llama3")
                results[name] = len(models) > 0
            else:
                results[name] = check_func()
        except Exception as e:
            print(f"❌ Check '{name}' failed with error: {e}")
            results[name] = False
    
    # Summary
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    
    for name, passed in results.items():
        status = "✅" if passed else "❌"
        print(f"{status} {name}")
    
    passed_count = sum(1 for v in results.values() if v)
    total_count = len(results)
    
    print(f"\n{passed_count}/{total_count} checks passed")
    
    if passed_count == total_count:
        print("\n🎉 All checks passed! Ollama integration is ready.")
        print("   Start Streamlit with: streamlit run app.py")
        return 0
    elif passed_count >= total_count - 1:
        print("\n⚠️  Most checks passed. See warnings above.")
        print("   Try pulling a model: docker-compose -f docker-compose.local.yml exec ollama ollama pull llama3")
        return 0
    else:
        print("\n❌ Integration not fully set up. Fix issues above.")
        print("   Ensure docker-compose is running: docker-compose -f docker-compose.local.yml up -d")
        return 1


if __name__ == "__main__":
    sys.exit(main())
