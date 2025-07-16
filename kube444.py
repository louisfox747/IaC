#!/usr/bin/env python
# Windows-compatible Python script for scanning Kubernetes pods

import sys
import traceback
import subprocess
import os

# Check and install dependencies
def check_and_install_dependencies():
    """Check if kubernetes module is available and install if missing"""
    try:
        import kubernetes
        print("✓ Kubernetes module is available")
        return True
    except ImportError:
        print("❌ Kubernetes module not found. Attempting to install...")
        try:
            # Try to install kubernetes module
            subprocess.check_call([sys.executable, "-m", "pip", "install", "kubernetes"])
            print("✓ Kubernetes module installed successfully")
            return True
        except subprocess.CalledProcessError:
            print("❌ Failed to install kubernetes module")
            print("Please install it manually with: pip install kubernetes")
            return False
        except Exception as e:
            print(f"❌ Error during installation: {e}")
            return False

# Import kubernetes modules after checking dependencies
if not check_and_install_dependencies():
    print("\n🔧 Manual installation instructions:")
    print("1. Install the kubernetes Python package:")
    print("   pip install kubernetes")
    print("2. Or install from requirements.txt if available:")
    print("   pip install -r requirements.txt")
    print("3. For system-wide installation:")
    print("   sudo pip install kubernetes")
    sys.exit(1)

try:
    from kubernetes import client, config
    from kubernetes.client.rest import ApiException
except ImportError as e:
    print(f"❌ Still unable to import kubernetes module: {e}")
    sys.exit(1)


def main():
    """Main function to connect to Kubernetes cluster and list pods"""
    
    # Load kubeconfig explicitly as specified in the task
    try:
        config.load_kube_config(config_file=r"c:\n8n\vke5.yaml")
        print("Successfully loaded kubeconfig from c:\\n8n\\vke5.yaml")
    except ApiException as e:
        print(f"Kubernetes API Exception while loading kubeconfig:")
        print(f"HTTP Status: {e.status}")
        print(f"Reason: {e.reason}")
        print(f"Body: {e.body}")
        sys.exit(1)
    except Exception as e:
        print(f"Failed to load kubeconfig: {e}")
        print("\nFull traceback:")
        print(traceback.format_exc())
        sys.exit(1)
    
    # Instantiate CoreV1Api client
    try:
        core_v1 = client.CoreV1Api()
        print("Successfully created Kubernetes API client")
    except ApiException as e:
        print(f"Kubernetes API Exception while creating client:")
        print(f"HTTP Status: {e.status}")
        print(f"Reason: {e.reason}")
        print(f"Body: {e.body}")
        sys.exit(1)
    except Exception as e:
        print(f"Failed to create Kubernetes API client: {e}")
        print("\nFull traceback:")
        print(traceback.format_exc())
        sys.exit(1)
    
    # Get list of all pods across all namespaces
    try:
        print("\nScanning Kubernetes cluster for pods...")
        print("=" * 80)
        
        # List all pods in all namespaces
        pods = core_v1.list_pod_for_all_namespaces(watch=False)
        
        if not pods.items:
            print("No pods found in the cluster")
            return
        
        print(f"Found {len(pods.items)} pods in the cluster:\n")
        
        # Format and display pod information
        print(f"{'NAMESPACE':<20} {'NAME':<40} {'STATUS':<15} {'AGE'}")
        print("-" * 80)
        
        for pod in pods.items:
            namespace = pod.metadata.namespace
            name = pod.metadata.name
            status = pod.status.phase
            creation_time = pod.metadata.creation_timestamp
            
            # Calculate age (simple representation)
            from datetime import datetime, timezone
            now = datetime.now(timezone.utc)
            age = now - creation_time
            age_str = f"{age.days}d" if age.days > 0 else f"{age.seconds//3600}h"
            
            print(f"{namespace:<20} {name:<40} {status:<15} {age_str}")
        
        print(f"\nTotal pods: {len(pods.items)}")
        
    except ApiException as e:
        print(f"\nKubernetes API Exception while listing pods:")
        print(f"HTTP Status: {e.status}")
        print(f"Reason: {e.reason}")
        print(f"Body: {e.body}")
        if hasattr(e, 'headers') and e.headers:
            print(f"Headers: {e.headers}")
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error while listing pods: {e}")
        print("\nFull traceback:")
        print(traceback.format_exc())
        sys.exit(1)


if __name__ == "__main__":
    main()
