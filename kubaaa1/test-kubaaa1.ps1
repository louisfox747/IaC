# Simple test script for kubaaa1 Ansible playbook
# This script tests Kubernetes connectivity without complex Ansible requirements

param(
    [string]$KubeconfigPath = "$env:USERPROFILE\.kube\config"
)

Write-Host "=== kubaaa1 - Kubernetes Connection Test ===" -ForegroundColor Green
Write-Host "Timestamp: $(Get-Date)" -ForegroundColor Yellow

# Check if kubectl is available
Write-Host "`nChecking prerequisites..." -ForegroundColor Cyan
try {
    $kubectlVersion = kubectl version --client=true 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ kubectl is available" -ForegroundColor Green
        Write-Host "  Version: $($kubectlVersion.Split("`n")[0])" -ForegroundColor Gray
    } else {
        throw "kubectl not found"
    }
} catch {
    Write-Host "✗ kubectl is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install kubectl and ensure it's in your PATH" -ForegroundColor Yellow
    exit 1
}

# Check kubeconfig
Write-Host "`nChecking kubeconfig..." -ForegroundColor Cyan
if ($KubeconfigPath -and (Test-Path $KubeconfigPath)) {
    $env:KUBECONFIG = $KubeconfigPath
    Write-Host "✓ Using kubeconfig: $KubeconfigPath" -ForegroundColor Green
} elseif ($env:KUBECONFIG -and (Test-Path $env:KUBECONFIG)) {
    Write-Host "✓ Using existing KUBECONFIG: $env:KUBECONFIG" -ForegroundColor Green
} else {
    Write-Host "✗ No valid kubeconfig found" -ForegroundColor Red
    Write-Host "Please ensure kubeconfig exists at: $KubeconfigPath" -ForegroundColor Yellow
    exit 1
}

# Test Kubernetes connection
Write-Host "`nTesting Kubernetes connection..." -ForegroundColor Cyan
try {
    $nodesResult = kubectl get nodes --no-headers 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Successfully connected to Kubernetes cluster!" -ForegroundColor Green
        Write-Host "`nCluster nodes:" -ForegroundColor Cyan
        kubectl get nodes
        
        Write-Host "`nCluster info:" -ForegroundColor Cyan
        kubectl cluster-info
        
        Write-Host "`n✓ kubaaa1 test completed successfully!" -ForegroundColor Green
    } else {
        throw "Connection failed"
    }
} catch {
    Write-Host "✗ Unable to connect to Kubernetes cluster" -ForegroundColor Red
    Write-Host "Please check:" -ForegroundColor Yellow
    Write-Host "  - Cluster is running and accessible" -ForegroundColor Yellow
    Write-Host "  - Network connectivity to cluster API server" -ForegroundColor Yellow
    Write-Host "  - Kubeconfig credentials are valid" -ForegroundColor Yellow
    Write-Host "  - RBAC permissions for cluster access" -ForegroundColor Yellow
    exit 1
}

Write-Host "`n=== kubaaa1 Test Complete ===" -ForegroundColor Green
