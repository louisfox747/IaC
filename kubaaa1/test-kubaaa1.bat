@echo off
REM kubaaa1 - Kubernetes Connection Test (Batch Version)
echo === kubaaa1 - Kubernetes Connection Test ===
echo Timestamp: %date% %time%

REM Check if kubectl is available
echo.
echo Checking prerequisites...
kubectl version --client=true >nul 2>&1
if %errorlevel% neq 0 (
    echo X kubectl is not installed or not in PATH
    echo Please install kubectl and ensure it's in your PATH
    exit /b 1
) else (
    echo + kubectl is available
)

REM Check kubeconfig
echo.
echo Checking kubeconfig...
if exist "%USERPROFILE%\.kube\config" (
    set KUBECONFIG=%USERPROFILE%\.kube\config
    echo + Using kubeconfig: %KUBECONFIG%
) else if defined KUBECONFIG (
    if exist "%KUBECONFIG%" (
        echo + Using existing KUBECONFIG: %KUBECONFIG%
    ) else (
        echo X KUBECONFIG environment variable set but file not found: %KUBECONFIG%
        exit /b 1
    )
) else (
    echo X No valid kubeconfig found
    echo Please ensure kubeconfig exists at: %USERPROFILE%\.kube\config
    exit /b 1
)

REM Test Kubernetes connection
echo.
echo Testing Kubernetes connection...
kubectl get nodes --no-headers >nul 2>&1
if %errorlevel% neq 0 (
    echo X Unable to connect to Kubernetes cluster
    echo Please check:
    echo   - Cluster is running and accessible
    echo   - Network connectivity to cluster API server
    echo   - Kubeconfig credentials are valid
    echo   - RBAC permissions for cluster access
    exit /b 1
) else (
    echo + Successfully connected to Kubernetes cluster!
    echo.
    echo Cluster nodes:
    kubectl get nodes
    echo.
    echo Cluster info:
    kubectl cluster-info
    echo.
    echo + kubaaa1 test completed successfully!
)

echo.
echo === kubaaa1 Test Complete ===
