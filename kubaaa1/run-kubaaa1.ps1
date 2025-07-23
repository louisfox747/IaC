# PowerShell script to run kubaaa1 Ansible playbook
# This script handles Kubernetes cluster connection testing

param(
    [string]$KubeconfigPath = "$env:USERPROFILE\.kube\config",
    [switch]$Verbose
)

Write-Host "=== Kubernetes Cluster Connection Test ===" -ForegroundColor Green
Write-Host "Timestamp: $(Get-Date)" -ForegroundColor Yellow

# Check if ansible is available
try {
    $ansibleVersion = ansible --version 2>$null
    if ($LASTEXITCODE -ne 0) {
        throw "Ansible not found"
    }
    Write-Host "✓ Ansible is available" -ForegroundColor Green
} catch {
    Write-Host "✗ Ansible is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Ansible: pip install ansible" -ForegroundColor Yellow
    exit 1
}

# Check if kubectl is available
try {
    $kubectlVersion = kubectl version --client=true --short 2>$null
    if ($LASTEXITCODE -ne 0) {
        throw "kubectl not found"
    }
    Write-Host "✓ kubectl is available" -ForegroundColor Green
} catch {
    Write-Host "✗ kubectl is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install kubectl and ensure it's in your PATH" -ForegroundColor Yellow
    exit 1
}

# Set KUBECONFIG environment variable if specified
if ($KubeconfigPath -and (Test-Path $KubeconfigPath)) {
    $env:KUBECONFIG = $KubeconfigPath
    Write-Host "✓ Using kubeconfig: $KubeconfigPath" -ForegroundColor Green
} elseif ($env:KUBECONFIG) {
    Write-Host "✓ Using existing KUBECONFIG: $env:KUBECONFIG" -ForegroundColor Green
} else {
    Write-Host "⚠ No kubeconfig specified, using default ~/.kube/config" -ForegroundColor Yellow
}

# Run the Ansible playbook
Write-Host "`n--- Running Ansible Playbook ---" -ForegroundColor Cyan

$ansibleArgs = @("kubaaa1.yml")
if ($Verbose) {
    $ansibleArgs += "-v"
}

try {
    & ansible-playbook @ansibleArgs
    if ($LASTEXITCODE -eq 0) {
        Write-Host "`n✓ Ansible playbook completed successfully!" -ForegroundColor Green
    } else {
        Write-Host "`n✗ Ansible playbook failed with exit code: $LASTEXITCODE" -ForegroundColor Red
        exit $LASTEXITCODE
    }
} catch {
    Write-Host "`n✗ Error running Ansible playbook: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

Write-Host "`n=== Connection Test Complete ===" -ForegroundColor Green
