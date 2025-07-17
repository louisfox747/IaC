#!/usr/bin/env python
"""
Kubernetes Pod Resource Usage Report
Provides detailed CPU and memory usage information for all pods in the cluster
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

def convert_cpu_to_millicores(cpu_value):
    """Convert CPU value to millicores for consistent reporting"""
    if not cpu_value:
        return 0
    
    cpu_str = str(cpu_value)
    if cpu_str.endswith('m'):
        return int(cpu_str[:-1])
    elif cpu_str.endswith('n'):
        return int(cpu_str[:-1]) / 1000000
    else:
        return int(float(cpu_str) * 1000)

def convert_memory_to_mb(memory_value):
    """Convert memory value to MB for consistent reporting"""
    if not memory_value:
        return 0
    
    memory_str = str(memory_value)
    if memory_str.endswith('Ki'):
        return int(memory_str[:-2]) / 1024
    elif memory_str.endswith('Mi'):
        return int(memory_str[:-2])
    elif memory_str.endswith('Gi'):
        return int(memory_str[:-2]) * 1024
    elif memory_str.endswith('Ti'):
        return int(memory_str[:-2]) * 1024 * 1024
    else:
        # Assume bytes
        return int(memory_str) / (1024 * 1024)

def get_pod_metrics(metrics_v1beta1, namespace, pod_name):
    """Get CPU and memory metrics for a specific pod"""
    try:
        pod_metrics = metrics_v1beta1.read_namespaced_pod_metrics(name=pod_name, namespace=namespace)
        
        total_cpu = 0
        total_memory = 0
        container_count = 0
        
        for container in pod_metrics.containers:
            container_count += 1
            if container.usage:
                if 'cpu' in container.usage:
                    total_cpu += convert_cpu_to_millicores(container.usage['cpu'])
                if 'memory' in container.usage:
                    total_memory += convert_memory_to_mb(container.usage['memory'])
        
        return {
            'cpu_millicores': total_cpu,
            'memory_mb': total_memory,
            'container_count': container_count
        }
    except Exception as e:
        return {
            'cpu_millicores': 0,
            'memory_mb': 0,
            'container_count': 0,
            'error': str(e)
        }

def get_pod_resource_limits(pod):
    """Get resource limits and requests for a pod"""
    total_cpu_request = 0
    total_cpu_limit = 0
    total_memory_request = 0
    total_memory_limit = 0
    
    for container in pod.spec.containers:
        if container.resources:
            # CPU requests
            if container.resources.requests and 'cpu' in container.resources.requests:
                total_cpu_request += convert_cpu_to_millicores(container.resources.requests['cpu'])
            
            # CPU limits
            if container.resources.limits and 'cpu' in container.resources.limits:
                total_cpu_limit += convert_cpu_to_millicores(container.resources.limits['cpu'])
            
            # Memory requests
            if container.resources.requests and 'memory' in container.resources.requests:
                total_memory_request += convert_memory_to_mb(container.resources.requests['memory'])
            
            # Memory limits
            if container.resources.limits and 'memory' in container.resources.limits:
                total_memory_limit += convert_memory_to_mb(container.resources.limits['memory'])
    
    return {
        'cpu_request_millicores': total_cpu_request,
        'cpu_limit_millicores': total_cpu_limit,
        'memory_request_mb': total_memory_request,
        'memory_limit_mb': total_memory_limit
    }

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
        
        # Create API clients
        core_v1 = client.CoreV1Api()
        print("✓ Successfully created Kubernetes API client")
        
        # Try to create metrics client
        try:
            from kubernetes.client import CustomObjectsApi
            custom_objects_api = CustomObjectsApi()
            print("✓ Successfully created Custom Objects API client for metrics")
            metrics_available = True
        except Exception as e:
            print(f"⚠️  Metrics API not available: {e}")
            metrics_available = False
        
        # Get all pods
        print("\n📊 Generating Pod Resource Usage Report...")
        print("=" * 100)
        
        pods = core_v1.list_pod_for_all_namespaces(watch=False)
        
        if not pods.items:
            print("No pods found in the cluster")
            return
        
        # Prepare report data
        pod_data = []
        total_cpu_usage = 0
        total_memory_usage = 0
        total_cpu_requests = 0
        total_cpu_limits = 0
        total_memory_requests = 0
        total_memory_limits = 0
        
        for pod in pods.items:
            namespace = pod.metadata.namespace
            name = pod.metadata.name
            status = pod.status.phase
            
            # Get resource limits and requests
            resource_limits = get_pod_resource_limits(pod)
            
            # Get actual usage (if metrics available)
            if metrics_available and status == "Running":
                try:
                    # Try to get pod metrics using custom objects API
                    pod_metrics = custom_objects_api.get_namespaced_custom_object(
                        group="metrics.k8s.io",
                        version="v1beta1",
                        namespace=namespace,
                        plural="pods",
                        name=name
                    )
                    
                    cpu_usage = 0
                    memory_usage = 0
                    
                    if 'containers' in pod_metrics:
                        for container in pod_metrics['containers']:
                            if 'usage' in container:
                                if 'cpu' in container['usage']:
                                    cpu_usage += convert_cpu_to_millicores(container['usage']['cpu'])
                                if 'memory' in container['usage']:
                                    memory_usage += convert_memory_to_mb(container['usage']['memory'])
                    
                    metrics_data = {
                        'cpu_usage_millicores': cpu_usage,
                        'memory_usage_mb': memory_usage,
                        'metrics_available': True
                    }
                    
                    total_cpu_usage += cpu_usage
                    total_memory_usage += memory_usage
                    
                except Exception as e:
                    metrics_data = {
                        'cpu_usage_millicores': 0,
                        'memory_usage_mb': 0,
                        'metrics_available': False,
                        'error': str(e)
                    }
            else:
                metrics_data = {
                    'cpu_usage_millicores': 0,
                    'memory_usage_mb': 0,
                    'metrics_available': False
                }
            
            # Calculate age
            from datetime import datetime, timezone
            now = datetime.now(timezone.utc)
            age = now - pod.metadata.creation_timestamp
            age_str = f"{age.days}d" if age.days > 0 else f"{age.seconds//3600}h"
            
            # Add to totals
            total_cpu_requests += resource_limits['cpu_request_millicores']
            total_cpu_limits += resource_limits['cpu_limit_millicores']
            total_memory_requests += resource_limits['memory_request_mb']
            total_memory_limits += resource_limits['memory_limit_mb']
            
            pod_data.append({
                'namespace': namespace,
                'name': name,
                'status': status,
                'age': age_str,
                'cpu_request': resource_limits['cpu_request_millicores'],
                'cpu_limit': resource_limits['cpu_limit_millicores'],
                'memory_request': resource_limits['memory_request_mb'],
                'memory_limit': resource_limits['memory_limit_mb'],
                'cpu_usage': metrics_data['cpu_usage_millicores'],
                'memory_usage': metrics_data['memory_usage_mb'],
                'metrics_available': metrics_data['metrics_available']
            })
        
        # Sort pods by namespace and name
        pod_data.sort(key=lambda x: (x['namespace'], x['name']))
        
        # Display detailed report
        print(f"Found {len(pod_data)} pods with resource information:\n")
        
        # Header
        print(f"{'NAMESPACE':<20} {'POD NAME':<35} {'STATUS':<12} {'AGE':<6} {'CPU REQ':<8} {'CPU LIM':<8} {'MEM REQ':<8} {'MEM LIM':<8} {'CPU USE':<8} {'MEM USE':<8}")
        print(f"{'':20} {'':35} {'':12} {'':6} {'(mCPU)':<8} {'(mCPU)':<8} {'(MB)':<8} {'(MB)':<8} {'(mCPU)':<8} {'(MB)':<8}")
        print("-" * 140)
        
        for pod in pod_data:
            cpu_req = f"{pod['cpu_request']}" if pod['cpu_request'] > 0 else "-"
            cpu_lim = f"{pod['cpu_limit']}" if pod['cpu_limit'] > 0 else "-"
            mem_req = f"{pod['memory_request']:.0f}" if pod['memory_request'] > 0 else "-"
            mem_lim = f"{pod['memory_limit']:.0f}" if pod['memory_limit'] > 0 else "-"
            cpu_use = f"{pod['cpu_usage']}" if pod['metrics_available'] and pod['cpu_usage'] > 0 else "N/A"
            mem_use = f"{pod['memory_usage']:.0f}" if pod['metrics_available'] and pod['memory_usage'] > 0 else "N/A"
            
            print(f"{pod['namespace']:<20} {pod['name']:<35} {pod['status']:<12} {pod['age']:<6} {cpu_req:<8} {cpu_lim:<8} {mem_req:<8} {mem_lim:<8} {cpu_use:<8} {mem_use:<8}")
        
        # Summary
        print("\n" + "=" * 100)
        print("📊 CLUSTER RESOURCE SUMMARY")
        print("=" * 100)
        print(f"Total Pods: {len(pod_data)}")
        print(f"Running Pods: {len([p for p in pod_data if p['status'] == 'Running'])}")
        print(f"Succeeded Pods: {len([p for p in pod_data if p['status'] == 'Succeeded'])}")
        print(f"Pending Pods: {len([p for p in pod_data if p['status'] == 'Pending'])}")
        print(f"Failed Pods: {len([p for p in pod_data if p['status'] == 'Failed'])}")
        
        print(f"\nRESOURCE REQUESTS:")
        print(f"  CPU Requests: {total_cpu_requests} mCPU ({total_cpu_requests/1000:.2f} CPU cores)")
        print(f"  Memory Requests: {total_memory_requests:.0f} MB ({total_memory_requests/1024:.2f} GB)")
        
        print(f"\nRESOURCE LIMITS:")
        print(f"  CPU Limits: {total_cpu_limits} mCPU ({total_cpu_limits/1000:.2f} CPU cores)")
        print(f"  Memory Limits: {total_memory_limits:.0f} MB ({total_memory_limits/1024:.2f} GB)")
        
        if metrics_available:
            print(f"\nCURRENT USAGE:")
            print(f"  CPU Usage: {total_cpu_usage} mCPU ({total_cpu_usage/1000:.2f} CPU cores)")
            print(f"  Memory Usage: {total_memory_usage:.0f} MB ({total_memory_usage/1024:.2f} GB)")
            
            if total_cpu_requests > 0:
                cpu_utilization = (total_cpu_usage / total_cpu_requests) * 100
                print(f"  CPU Utilization: {cpu_utilization:.1f}% of requests")
            
            if total_memory_requests > 0:
                memory_utilization = (total_memory_usage / total_memory_requests) * 100
                print(f"  Memory Utilization: {memory_utilization:.1f}% of requests")
        else:
            print(f"\n⚠️  Current usage metrics not available (metrics-server may not be installed)")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
