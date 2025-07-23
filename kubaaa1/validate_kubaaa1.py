#!/usr/bin/env python3
"""
Python script to validate kubaaa1.yml Ansible playbook syntax
This script checks YAML syntax and basic Ansible playbook structure
"""

import yaml
import sys
import os
from datetime import datetime

def validate_yaml_syntax(filename):
    """Validate YAML syntax"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            yaml_content = yaml.safe_load_all(f)
            playbooks = list(yaml_content)
            print(f"✓ YAML syntax is valid for {filename}")
            return True, playbooks
    except yaml.YAMLError as e:
        print(f"✗ YAML syntax error in {filename}: {e}")
        return False, None
    except FileNotFoundError:
        print(f"✗ File not found: {filename}")
        return False, None

def validate_playbook_structure(playbooks):
    """Validate basic Ansible playbook structure"""
    if not playbooks:
        print("✗ No playbook content found")
        return False
    
    # Handle both single playbook and list of playbooks
    if isinstance(playbooks, list) and len(playbooks) > 0:
        playbook = playbooks[0]  # First playbook
    else:
        playbook = playbooks
    
    # Check required fields
    required_fields = ['name', 'hosts', 'tasks']
    for field in required_fields:
        if field not in playbook:
            print(f"✗ Missing required field: {field}")
            return False
    
    print(f"✓ Playbook structure is valid")
    print(f"  - Name: {playbook['name']}")
    print(f"  - Hosts: {playbook['hosts']}")
    print(f"  - Tasks: {len(playbook['tasks'])} tasks found")
    
    # Validate tasks
    task_names = []
    for i, task in enumerate(playbook['tasks']):
        if 'name' not in task:
            print(f"✗ Task {i+1} missing name")
            return False
        task_names.append(task['name'])
    
    print(f"✓ All {len(task_names)} tasks have names")
    return True

def validate_kubectl_tasks(playbooks):
    """Validate kubectl-related tasks"""
    playbook = playbooks[0]
    kubectl_tasks = []
    
    for task in playbook['tasks']:
        if 'command' in task and 'kubectl' in task['command']:
            kubectl_tasks.append(task['name'])
    
    print(f"✓ Found {len(kubectl_tasks)} kubectl tasks:")
    for task_name in kubectl_tasks:
        print(f"  - {task_name}")
    
    return len(kubectl_tasks) > 0

def main():
    """Main validation function"""
    print("=== kubaaa1.yml Validation Tool ===")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print()
    
    filename = "kubaaa1.yml"
    
    # Check if file exists
    if not os.path.exists(filename):
        print(f"✗ {filename} not found in current directory")
        print("Please run this script from the kubaaa1 directory")
        sys.exit(1)
    
    # Validate YAML syntax
    print("1. Validating YAML syntax...")
    yaml_valid, playbooks = validate_yaml_syntax(filename)
    if not yaml_valid:
        sys.exit(1)
    
    # Validate playbook structure
    print("\n2. Validating playbook structure...")
    structure_valid = validate_playbook_structure(playbooks)
    if not structure_valid:
        sys.exit(1)
    
    # Validate kubectl tasks
    print("\n3. Validating kubectl tasks...")
    kubectl_valid = validate_kubectl_tasks(playbooks)
    if not kubectl_valid:
        print("⚠ No kubectl tasks found - this may be intentional")
    
    # Summary
    print("\n" + "="*50)
    print("✓ kubaaa1.yml validation completed successfully!")
    print("The playbook appears to be syntactically correct and well-structured.")
    print("="*50)

if __name__ == "__main__":
    main()
