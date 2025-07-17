#!/usr/bin/env python
"""
Kubernetes Pod Scanner - Last 12 Hours
Lists pods created in the last 12 hours from the cluster
"""

import sys
import subprocess
import os
import site
import importlib

def install_and_import_kubernetes():
    """Install kubernetes module and handle import issues"""
    try:
        # First try to import
        import kubernetes
        from kubernetes import client, config
        from kubernetes.client.rest import ApiException
        print("✓ Kubernetes module already available")
        return client, config, ApiException
    except ImportError:
        print("❌ Kubernetes module not found. Installing...")
        
        # Install the module
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "--user", "kubernetes"])
            print("✓ Kubernetes module installed successfully")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install kubernetes: {e}")
            sys.exit(1)
        
        # Force reload of site packages
        importlib.invalidate_caches()
        site.main()
        
        # Try to import again
        try:
            import kubernetes
            from kubernetes import client, config
            from kubernetes.client.rest import ApiException
            print("✓ Successfully imported kubernetes after installation")
            return client, config, ApiException
        except ImportError as e:
            print(f"❌ Still unable to import kubernetes: {e}")
            print("📝 Debug info:")
            print(f"   Python path: {sys.path}")
            print(f"   Site packages: {site.getsitepackages()}")
            
            # Try adding user site packages to path
            user_site = site.getusersitepackages()
            if user_site not in sys.path:
                sys.path.insert(0, user_site)
                print(f"   Added user site to path: {user_site}")
            
            # One more try
            try:
                import kubernetes
                from kubernetes import client, config
                from kubernetes.client.rest import ApiException
                print("✓ Successfully imported kubernetes after path fix")
                return client, config, ApiException
            except ImportError as e:
                print(f"❌ Final import attempt failed: {e}")
                sys.exit(1)

def main():
    """Main function"""
    # Install and import kubernetes
    client, config, ApiException = install_and_import_kubernetes()
    
    try:
        # Load kubeconfig - try both possible paths
        config_paths = [
            r"c:\n8n\vke5.yaml",
            "/tmp/repository_2_11/vke5.yaml",
            "vke5.yaml"
        ]
        
        kubeconfig_loaded = False
        for config_path in config_paths:
            try:
                config.load_kube_config(config_file=config_path)
                print(f"✓ Successfully loaded kubeconfig from {config_path}")
                kubeconfig_loaded = True
                break
            except Exception:
                continue
        
        if not kubeconfig_loaded:
            print("❌ Failed to load kubeconfig from any path")
            print("📝 Tried paths:")
            for path in config_paths:
                exists = os.path.exists(path)
                print(f"   {path} - {'EXISTS' if exists else 'NOT FOUND'}")
            sys.exit(1)
        
        # Create API client
        core_v1 = client.CoreV1Api()
        print("✓ Successfully created Kubernetes API client")
        
        # List pods
        print("\nScanning Kubernetes cluster for pods created in the last 12 hours...")
        print("=" * 80)
        
        pods = core_v1.list_pod_for_all_namespaces(watch=False)
        
        if not pods.items:
            print("No pods found in the cluster")
            return
        
        # Filter pods created in the last 12 hours
        from datetime import datetime, timezone, timedelta
        now = datetime.now(timezone.utc)
        twelve_hours_ago = now - timedelta(hours=12)
        
        recent_pods = []
        for pod in pods.items:
            creation_time = pod.metadata.creation_timestamp
            if creation_time >= twelve_hours_ago:
                recent_pods.append(pod)
        
        if not recent_pods:
            print("No pods found created in the last 12 hours")
            return
        
        print(f"Found {len(recent_pods)} pods created in the last 12 hours:\n")
        
        # Format and display pod information
        print(f"{'NAMESPACE':<20} {'NAME':<40} {'STATUS':<15} {'AGE'}")
        print("-" * 80)
        
        for pod in recent_pods:
            namespace = pod.metadata.namespace
            name = pod.metadata.name
            status = pod.status.phase
            creation_time = pod.metadata.creation_timestamp
            
            # Calculate age (simple representation)
            age = now - creation_time
            if age.days > 0:
                age_str = f"{age.days}d"
            elif age.seconds >= 3600:
                age_str = f"{age.seconds//3600}h"
            else:
                age_str = f"{age.seconds//60}m"
            
            print(f"{namespace:<20} {name:<40} {status:<15} {age_str}")
        
        print(f"\nTotal recent pods: {len(recent_pods)}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
