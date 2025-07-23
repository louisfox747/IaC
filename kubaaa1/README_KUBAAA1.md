# kubaaa1 - Kubernetes Cluster Connection Ansible Playbook

## Overview
`kubaaa1` is an Ansible playbook designed to test and validate connections to Kubernetes clusters using kubeconfig files. This tool is essential for verifying cluster connectivity before running automated deployments or management tasks.

## Features
- ✅ Automatic kubeconfig detection and validation
- ✅ Kubernetes cluster connectivity testing
- ✅ Cross-platform support (Windows/Linux/macOS)
- ✅ Detailed error reporting and troubleshooting
- ✅ PowerShell wrapper script for Windows users
- ✅ Environment variable support for flexible configuration

## Prerequisites

### Required Software
1. **Python 3.6+**
2. **Ansible** - Install with: `pip install ansible`
3. **kubectl** - Kubernetes command-line tool
4. **Valid kubeconfig file** - Access to a Kubernetes cluster

### Installation Commands
```bash
# Install Ansible
pip install ansible

# Verify installations
ansible --version
kubectl version --client
```

## File Structure
```
kubaaa1/
├── kubaaa1.yml          # Main Ansible playbook
├── inventory.ini        # Ansible inventory configuration
├── ansible.cfg          # Ansible configuration file
├── run-kubaaa1.ps1     # PowerShell wrapper script (Windows)
└── README_KUBAAA1.md   # This documentation
```

## Usage

### Method 1: PowerShell Script (Windows - Recommended)
```powershell
# Basic usage
.\run-kubaaa1.ps1

# With custom kubeconfig path
.\run-kubaaa1.ps1 -KubeconfigPath "C:\path\to\your\kubeconfig"

# With verbose output
.\run-kubaaa1.ps1 -Verbose
```

### Method 2: Direct Ansible Command
```bash
# Linux/macOS/WSL
ansible-playbook kubaaa1.yml

# Windows PowerShell
ansible-playbook kubaaa1.yml
```

### Method 3: With Custom Kubeconfig
```bash
# Set environment variable
export KUBECONFIG="/path/to/your/kubeconfig"
ansible-playbook kubaaa1.yml

# Windows PowerShell
$env:KUBECONFIG = "C:\path\to\your\kubeconfig"
ansible-playbook kubaaa1.yml
```

## Configuration Options

### Environment Variables
- `KUBECONFIG` - Path to your kubeconfig file
- `ANSIBLE_CONFIG` - Path to ansible configuration file

### Kubeconfig Detection Priority
1. `KUBECONFIG` environment variable
2. Command-line parameter (PowerShell script)
3. Default: `~/.kube/config`

## Example Output
```yaml
PLAY [Connect to Kubernetes Cluster] ******************************************

TASK [Set kubeconfig environment variable] ********************************
ok: [localhost]

TASK [Ensure KUBECONFIG is accessible] ************************************
ok: [localhost]

TASK [Display kubeconfig being used] **************************************
ok: [localhost] => 
  msg: Using KUBECONFIG located at C:/Users/user/.kube/config

TASK [Test Kubernetes connection] *****************************************
ok: [localhost]

TASK [Display Kubernetes connection result] *******************************
ok: [localhost] => 
  msg: |-
    Kubernetes connection result: NAME                 STATUS   ROLES           AGE   VERSION
    control-plane-node       Ready    control-plane   45d   v1.28.2
    worker-node-1           Ready    <none>          45d   v1.28.2
    worker-node-2           Ready    <none>          45d   v1.28.2

PLAY RECAP *****************************************************************
localhost                  : ok=5    changed=0    unreachable=0    failed=0
```

## Troubleshooting

### Common Issues

#### 1. Ansible Not Found
```
✗ Ansible is not installed or not in PATH
```
**Solution:** Install Ansible using `pip install ansible`

#### 2. kubectl Not Found
```
✗ kubectl is not installed or not in PATH
```
**Solutions:**
- Install kubectl: [Official Installation Guide](https://kubernetes.io/docs/tasks/tools/)
- Ensure kubectl is in your system PATH

#### 3. Kubeconfig Not Found
```
KUBECONFIG file not found, please ensure it exists at /path/to/config
```
**Solutions:**
- Verify kubeconfig file exists and is readable
- Set correct path using `KUBECONFIG` environment variable
- Use `-KubeconfigPath` parameter with PowerShell script

#### 4. Connection Failed
```
Unable to connect to Kubernetes cluster. Please check the kubeconfig and credentials.
```
**Solutions:**
- Verify cluster is running and accessible
- Check network connectivity to cluster API server
- Validate kubeconfig credentials (tokens, certificates)
- Test connection manually: `kubectl get nodes`

#### 5. Permission Errors
```
Error from server (Forbidden): nodes is forbidden
```
**Solutions:**
- Ensure your kubeconfig has appropriate RBAC permissions
- Required permissions: `kubectl auth can-i get nodes`
- Contact cluster administrator for proper access

### Advanced Troubleshooting

#### Debug Mode
```bash
# Run with maximum verbosity
ansible-playbook kubaaa1.yml -vvvv
```

#### Manual kubectl Test
```bash
# Test kubectl directly
kubectl get nodes --kubeconfig /path/to/your/kubeconfig
kubectl cluster-info --kubeconfig /path/to/your/kubeconfig
```

#### Check Kubeconfig Content
```bash
# View current context
kubectl config current-context

# View all contexts
kubectl config get-contexts

# View cluster info
kubectl config view
```

## Integration Examples

### CI/CD Pipeline
```yaml
# GitHub Actions example
- name: Test Kubernetes Connection
  run: |
    ansible-playbook kubaaa1.yml
```

### Cron Job Monitoring
```bash
# Add to crontab for regular connectivity checks
0 */6 * * * /usr/bin/ansible-playbook /path/to/kubaaa1.yml >> /var/log/k8s-connectivity.log 2>&1
```

### Infrastructure as Code
```yaml
# Include in larger Ansible playbooks
- import_playbook: kubaaa1.yml
  tags: connectivity_test
```

## Security Considerations

1. **Kubeconfig Protection**
   - Never commit kubeconfig files to version control
   - Use secure storage for kubeconfig files
   - Regularly rotate cluster credentials

2. **Access Control**
   - Use least-privilege principle for cluster access
   - Monitor and audit cluster access logs
   - Use service accounts for automated tools

3. **Network Security**
   - Ensure secure network connections to cluster API
   - Use VPN or private networks when possible
   - Validate TLS certificates

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## Support

For issues and questions:
1. Check the troubleshooting section above
2. Review Ansible and kubectl documentation
3. Open an issue on the GitHub repository

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Changelog

### v1.0.0
- Initial release
- Basic Kubernetes connectivity testing
- PowerShell wrapper script
- Comprehensive error handling
- Cross-platform support
