#!/usr/bin/env python3
"""
Kubernetes Deployment Enumeration Report
Connects to a remote Kubernetes cluster and enumerates all deployments across namespaces
"""

import sys
import traceback
from datetime import datetime, timezone, timedelta
from kubernetes import client, config
from kubernetes.client.rest import ApiException


def main():
    """Main function to connect to Kubernetes cluster and enumerate all deployments"""
    
    # Load kubeconfig explicitly as specified in kube444.py
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
    
    # Instantiate AppsV1Api client
    try:
        apps_v1 = client.AppsV1Api()
        print("Successfully created Kubernetes AppsV1Api client")
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
    
    # Get list of all deployments across all namespaces using AppsV1Api
    try:
        print("\nEnumerating all deployments across namespaces...")
        print("=" * 80)
        
        # Use AppsV1Api().list_deployment_for_all_namespaces() to get V1Deployment objects
        deployments = apps_v1.list_deployment_for_all_namespaces(watch=False)
        
        if not deployments.items:
            print("No deployments found in the cluster")
            return
        
        print(f"Found {len(deployments.items)} deployments across the cluster:\n")
        
        # Format and display deployment information
        print(f"{'NAMESPACE':<20} {'NAME':<40} {'REPLICAS':<10} {'READY':<8} {'AVAILABLE':<10} {'AGE'}")
        print("-" * 105)
        
        now = datetime.now(timezone.utc)
        namespace_stats = {}
        
        for deployment in deployments.items:
            namespace = deployment.metadata.namespace
            name = deployment.metadata.name
            replicas = deployment.spec.replicas or 0
            ready_replicas = deployment.status.ready_replicas or 0
            available_replicas = deployment.status.available_replicas or 0
            creation_time = deployment.metadata.creation_timestamp
            
            # Count deployments by namespace
            namespace_stats[namespace] = namespace_stats.get(namespace, 0) + 1
            
            # Calculate age
            age = now - creation_time
            if age.days > 0:
                age_str = f"{age.days}d {age.seconds//3600}h"
            elif age.seconds >= 3600:
                age_str = f"{age.seconds//3600}h {(age.seconds%3600)//60}m"
            else:
                age_str = f"{age.seconds//60}m"
            
            print(f"{namespace:<20} {name:<40} {replicas:<10} {ready_replicas:<8} {available_replicas:<10} {age_str}")
        
        print(f"\n=== DEPLOYMENT ENUMERATION RESULTS ===")
        print(f"Total deployments found: {len(deployments.items)}")
        print(f"Deployments found across {len(namespace_stats)} namespaces:")
        
        # Log deployments by namespace
        for namespace, count in sorted(namespace_stats.items()):
            print(f"  - {namespace}: {count} deployment(s)")
        
        print(f"\nReport generated at: {now.strftime('%Y-%m-%d %H:%M:%S UTC')}")
        
    except ApiException as e:
        print(f"\nKubernetes API Exception while listing deployments:")
        print(f"HTTP Status: {e.status}")
        print(f"Reason: {e.reason}")
        print(f"Body: {e.body}")
        if hasattr(e, 'headers') and e.headers:
            print(f"Headers: {e.headers}")
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error while listing deployments: {e}")
        print("\nFull traceback:")
        print(traceback.format_exc())
        sys.exit(1)


if __name__ == "__main__":
    main()
