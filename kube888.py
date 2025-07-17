#!/usr/bin/env python
"""
Kubernetes Pod Sequential Restart Script
Restarts all pods in sequence, ensuring each pod is running before proceeding to the next
WARNING: This is for testing environments only!
"""

import sys
import subprocess
import os
import site
import importlib
import time

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

def wait_for_pod_ready(core_v1, namespace, pod_name, timeout=300):
    """Wait for a pod to be in Running state"""
    print(f"    Waiting for pod {pod_name} to be ready...")
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        try:
            pod = core_v1.read_namespaced_pod(name=pod_name, namespace=namespace)
            if pod.status.phase == "Running":
                # Check if all containers are ready
                if pod.status.container_statuses:
                    all_ready = all(container.ready for container in pod.status.container_statuses)
                    if all_ready:
                        print(f"    ✓ Pod {pod_name} is ready")
                        return True
                else:
                    # If no container statuses, assume ready if running
                    print(f"    ✓ Pod {pod_name} is ready")
                    return True
            elif pod.status.phase == "Succeeded":
                print(f"    ✓ Pod {pod_name} completed successfully")
                return True
        except Exception as e:
            print(f"    ⏳ Checking pod status: {e}")
        
        time.sleep(5)
    
    print(f"    ❌ Timeout waiting for pod {pod_name} to be ready")
    return False

def restart_pod(core_v1, namespace, pod_name):
    """Restart a pod by deleting it (if managed by a controller)"""
    try:
        print(f"  🔄 Restarting pod: {namespace}/{pod_name}")
        
        # Delete the pod
        core_v1.delete_namespaced_pod(name=pod_name, namespace=namespace)
        print(f"    ✓ Pod {pod_name} deleted")
        
        # Wait a moment for the pod to be recreated
        time.sleep(10)
        
        # Wait for the new pod to be ready
        # Note: The new pod might have a different name, so we need to find it
        max_retries = 30
        for retry in range(max_retries):
            try:
                pods = core_v1.list_namespaced_pod(namespace=namespace)
                for pod in pods.items:
                    if pod.metadata.name.startswith(pod_name.split('-')[0]):
                        if pod.status.phase == "Running" or pod.status.phase == "Succeeded":
                            print(f"    ✓ New pod {pod.metadata.name} is ready")
                            return True
                time.sleep(5)
            except Exception as e:
                print(f"    ⏳ Waiting for new pod: {e}")
                time.sleep(5)
        
        print(f"    ❌ Failed to confirm new pod is ready")
        return False
        
    except Exception as e:
        print(f"    ❌ Error restarting pod {pod_name}: {e}")
        return False

def main():
    """Main function"""
    print("🚨 WARNING: This script will restart ALL pods in the cluster!")
    print("🚨 This is intended for TEST ENVIRONMENTS ONLY!")
    print("=" * 60)
    
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
        
        # Get all pods
        print("\n📋 Getting list of all pods...")
        pods = core_v1.list_pod_for_all_namespaces(watch=False)
        
        if not pods.items:
            print("No pods found in the cluster")
            return
        
        # Filter out system-critical pods for safety
        system_namespaces = ["kube-system"]
        restartable_pods = []
        
        for pod in pods.items:
            # Skip system pods and completed/succeeded pods
            if (pod.metadata.namespace not in system_namespaces and 
                pod.status.phase in ["Running", "Pending"]):
                restartable_pods.append(pod)
        
        print(f"Found {len(restartable_pods)} restartable pods (excluding system-critical pods)")
        
        if not restartable_pods:
            print("No restartable pods found")
            return
        
        # Display pods to be restarted
        print("\n📝 Pods to be restarted:")
        for i, pod in enumerate(restartable_pods, 1):
            print(f"  {i}. {pod.metadata.namespace}/{pod.metadata.name} ({pod.status.phase})")
        
        # Confirmation
        print(f"\n⚠️  About to restart {len(restartable_pods)} pods sequentially")
        print("Press Ctrl+C to cancel or wait 10 seconds to proceed...")
        try:
            time.sleep(10)
        except KeyboardInterrupt:
            print("\n❌ Operation cancelled by user")
            sys.exit(0)
        
        # Restart pods sequentially
        print("\n🔄 Starting sequential pod restart...")
        print("=" * 60)
        
        successful_restarts = 0
        failed_restarts = 0
        
        for i, pod in enumerate(restartable_pods, 1):
            namespace = pod.metadata.namespace
            pod_name = pod.metadata.name
            
            print(f"\n[{i}/{len(restartable_pods)}] Processing pod: {namespace}/{pod_name}")
            
            if restart_pod(core_v1, namespace, pod_name):
                successful_restarts += 1
                print(f"    ✅ Successfully restarted pod {pod_name}")
            else:
                failed_restarts += 1
                print(f"    ❌ Failed to restart pod {pod_name}")
            
            # Small delay between restarts
            if i < len(restartable_pods):
                print(f"    ⏳ Waiting 15 seconds before next pod...")
                time.sleep(15)
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 RESTART SUMMARY")
        print("=" * 60)
        print(f"✅ Successfully restarted: {successful_restarts}")
        print(f"❌ Failed to restart: {failed_restarts}")
        print(f"📝 Total processed: {len(restartable_pods)}")
        
        if failed_restarts > 0:
            print("\n⚠️  Some pods failed to restart. Check the logs above for details.")
        else:
            print("\n🎉 All pods restarted successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
