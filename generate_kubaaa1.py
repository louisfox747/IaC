#!/usr/bin/env python3
"""
Python script to generate kubaaa1.yml Ansible playbook for Kubernetes connectivity testing
This script creates a comprehensive Ansible playbook for testing K8s cluster connections
"""

import os
import sys
import yaml
from datetime import datetime

def create_kubaaa1_playbook():
    """Generate the kubaaa1.yml Ansible playbook"""
    
    # Define the playbook structure
    playbook_data = [
        {
            'name': 'kubaaa1 - Connect to Kubernetes Cluster',
            'hosts': 'localhost',
            'gather_facts': False,
            'vars': {
                'kubeconfig_default': '{{ ansible_env.HOME }}/.kube/config',
                'kubeconfig_windows': '{{ ansible_env.USERPROFILE }}\\.kube\\config'
            },
            'tasks': [
                {
                    'name': 'Display kubaaa1 banner',
                    'debug': {
                        'msg': [
                            '=== kubaaa1 - Kubernetes Cluster Connection Test ===',
                            'Timestamp: {{ ansible_date_time.iso8601 }}',
                            'Target: {{ inventory_hostname }}',
                            '======================================================'
                        ]
                    }
                },
                {
                    'name': 'Detect operating system',
                    'set_fact': {
                        'is_windows': '{{ ansible_os_family == "Windows" }}'
                    }
                },
                {
                    'name': 'Set kubeconfig path for Linux/macOS',
                    'set_fact': {
                        'kubeconfig_path': '{{ lookup("env", "KUBECONFIG") or kubeconfig_default }}'
                    },
                    'when': 'not is_windows'
                },
                {
                    'name': 'Set kubeconfig path for Windows',
                    'set_fact': {
                        'kubeconfig_path': '{{ lookup("env", "KUBECONFIG") or kubeconfig_windows }}'
                    },
                    'when': 'is_windows'
                },
                {
                    'name': 'Display kubeconfig path being used',
                    'debug': {
                        'msg': 'Using kubeconfig: {{ kubeconfig_path }}'
                    }
                },
                {
                    'name': 'Check if kubeconfig file exists',
                    'stat': {
                        'path': '{{ kubeconfig_path }}'
                    },
                    'register': 'kubeconfig_stat'
                },
                {
                    'name': 'Fail if kubeconfig file not found',
                    'fail': {
                        'msg': [
                            'KUBECONFIG file not found at: {{ kubeconfig_path }}',
                            'Please ensure the kubeconfig file exists and is readable.',
                            'You can set the KUBECONFIG environment variable to specify a different path.'
                        ]
                    },
                    'when': 'not kubeconfig_stat.stat.exists'
                },
                {
                    'name': 'Check if kubectl is available',
                    'command': 'kubectl version --client=true',
                    'register': 'kubectl_version_check',
                    'ignore_errors': True,
                    'changed_when': False
                },
                {
                    'name': 'Fail if kubectl is not available',
                    'fail': {
                        'msg': [
                            'kubectl is not installed or not in PATH.',
                            'Please install kubectl and ensure it is available in your system PATH.',
                            'Installation guide: https://kubernetes.io/docs/tasks/tools/'
                        ]
                    },
                    'when': 'kubectl_version_check.rc != 0'
                },
                {
                    'name': 'Display kubectl version',
                    'debug': {
                        'msg': 'kubectl version: {{ kubectl_version_check.stdout_lines[0] }}'
                    },
                    'when': 'kubectl_version_check.rc == 0'
                },
                {
                    'name': 'Test Kubernetes cluster connection',
                    'command': 'kubectl get nodes --kubeconfig "{{ kubeconfig_path }}"',
                    'register': 'kubectl_nodes_result',
                    'ignore_errors': True,
                    'changed_when': False
                },
                {
                    'name': 'Display connection success message',
                    'debug': {
                        'msg': [
                            '✓ Successfully connected to Kubernetes cluster!',
                            '{{ kubectl_nodes_result.stdout }}'
                        ]
                    },
                    'when': 'kubectl_nodes_result.rc == 0'
                },
                {
                    'name': 'Get cluster information',
                    'command': 'kubectl cluster-info --kubeconfig "{{ kubeconfig_path }}"',
                    'register': 'kubectl_cluster_info',
                    'ignore_errors': True,
                    'changed_when': False,
                    'when': 'kubectl_nodes_result.rc == 0'
                },
                {
                    'name': 'Display cluster information',
                    'debug': {
                        'msg': [
                            'Cluster Information:',
                            '{{ kubectl_cluster_info.stdout }}'
                        ]
                    },
                    'when': 'kubectl_nodes_result.rc == 0 and kubectl_cluster_info.rc == 0'
                },
                {
                    'name': 'Get current context',
                    'command': 'kubectl config current-context --kubeconfig "{{ kubeconfig_path }}"',
                    'register': 'kubectl_current_context',
                    'ignore_errors': True,
                    'changed_when': False,
                    'when': 'kubectl_nodes_result.rc == 0'
                },
                {
                    'name': 'Display current context',
                    'debug': {
                        'msg': 'Current context: {{ kubectl_current_context.stdout }}'
                    },
                    'when': 'kubectl_nodes_result.rc == 0 and kubectl_current_context.rc == 0'
                },
                {
                    'name': 'Display connection failure message',
                    'debug': {
                        'msg': [
                            '✗ Failed to connect to Kubernetes cluster',
                            'Error output: {{ kubectl_nodes_result.stderr }}',
                            'Please check:',
                            '  - Cluster is running and accessible',
                            '  - Network connectivity to cluster API server',
                            '  - Kubeconfig credentials are valid and not expired',
                            '  - RBAC permissions for cluster access',
                            '  - Firewall settings allowing cluster communication'
                        ]
                    },
                    'when': 'kubectl_nodes_result.rc != 0'
                },
                {
                    'name': 'Fail if unable to connect to Kubernetes cluster',
                    'fail': {
                        'msg': [
                            'Unable to connect to Kubernetes cluster.',
                            'Please review the error messages above and troubleshoot accordingly.'
                        ]
                    },
                    'when': 'kubectl_nodes_result.rc != 0'
                },
                {
                    'name': 'Display success summary',
                    'debug': {
                        'msg': [
                            '=== kubaaa1 Connection Test Summary ===',
                            '✓ Kubeconfig found and accessible',
                            '✓ kubectl is available and working',
                            '✓ Successfully connected to Kubernetes cluster',
                            '✓ Cluster information retrieved successfully',
                            '==========================================='
                        ]
                    },
                    'when': 'kubectl_nodes_result.rc == 0'
                }
            ]
        }
    ]
    
    return playbook_data

def write_kubaaa1_playbook(playbook_data, output_file='kubaaa1.yml'):
    """Write the playbook data to YAML file"""
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            # Write header comment
            f.write(f"# kubaaa1.yml - Kubernetes Cluster Connection Test\n")
            f.write(f"# Generated by Python script on {datetime.now().isoformat()}\n")
            f.write(f"# This Ansible playbook tests connectivity to Kubernetes clusters\n")
            f.write(f"---\n")
            
            # Write the YAML content
            yaml.dump(playbook_data, f, 
                     default_flow_style=False, 
                     allow_unicode=True,
                     sort_keys=False,
                     indent=2)
            
        print(f"✓ Successfully created {output_file}")
        return True
        
    except Exception as e:
        print(f"✗ Error writing playbook file: {e}")
        return False

def create_inventory_file():
    """Create inventory.ini file"""
    inventory_content = """# Ansible inventory for kubaaa1 playbook
[local]
localhost ansible_connection=local

[local:vars]
ansible_python_interpreter=python3
"""
    
    try:
        with open('inventory.ini', 'w', encoding='utf-8') as f:
            f.write(inventory_content)
        print("✓ Successfully created inventory.ini")
        return True
    except Exception as e:
        print(f"✗ Error creating inventory file: {e}")
        return False

def create_ansible_config():
    """Create ansible.cfg file"""
    config_content = """[defaults]
inventory = inventory.ini
host_key_checking = False
deprecation_warnings = False
stdout_callback = yaml
timeout = 30
gathering = explicit

[ssh_connection]
ssh_args = -o ControlMaster=auto -o ControlPersist=60s
"""
    
    try:
        with open('ansible.cfg', 'w', encoding='utf-8') as f:
            f.write(config_content)
        print("✓ Successfully created ansible.cfg")
        return True
    except Exception as e:
        print(f"✗ Error creating ansible config: {e}")
        return False

def main():
    """Main function to generate kubaaa1 files"""
    print("=== kubaaa1 Ansible Playbook Generator ===")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print()
    
    # Check if PyYAML is available
    try:
        import yaml
        print("✓ PyYAML library available")
    except ImportError:
        print("✗ PyYAML library not found. Installing...")
        os.system("pip install PyYAML")
        try:
            import yaml
            print("✓ PyYAML installed successfully")
        except ImportError:
            print("✗ Failed to install PyYAML. Please install manually: pip install PyYAML")
            sys.exit(1)
    
    # Generate playbook
    print("\nGenerating kubaaa1.yml playbook...")
    playbook_data = create_kubaaa1_playbook()
    
    # Write files
    success = True
    success &= write_kubaaa1_playbook(playbook_data)
    success &= create_inventory_file()
    success &= create_ansible_config()
    
    if success:
        print("\n✓ All kubaaa1 files generated successfully!")
        print("\nGenerated files:")
        print("  - kubaaa1.yml (Main Ansible playbook)")
        print("  - inventory.ini (Ansible inventory)")
        print("  - ansible.cfg (Ansible configuration)")
        print("\nUsage:")
        print("  ansible-playbook kubaaa1.yml")
        print("  ansible-playbook kubaaa1.yml -v  # Verbose output")
    else:
        print("\n✗ Some files failed to generate. Please check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
