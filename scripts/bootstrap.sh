#!/bin/bash

set -e

echo "Starting Wisecow Cluster Bootstrap..."

# 1. Install ArgoCD
echo "Installing ArgoCD..."
kubectl create namespace argocd --dry-run=client -o yaml | kubectl apply -f -
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml --server-side --force-conflicts

# 2. Pre-install Prometheus ServiceMonitor CRD (required for NGINX metrics)
echo "Pre-installing Prometheus ServiceMonitor CRD..."
kubectl apply -f https://raw.githubusercontent.com/prometheus-operator/prometheus-operator/v0.74.0/example/prometheus-operator-crd/monitoring.coreos.com_servicemonitors.yaml --server-side || true

# 3. Install Ingress Nginx Controller
echo "Installing Ingress Nginx Controller..."
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx || true
helm repo update
helm upgrade --install ingress-nginx ingress-nginx/ingress-nginx \
  --namespace ingress-nginx --create-namespace \
  --set controller.metrics.enabled=true \
  --set controller.metrics.serviceMonitor.enabled=true \
  --set controller.metrics.serviceMonitor.additionalLabels.release="prometheus" \
  --wait

# 4. Wait for ArgoCD to be ready
echo "Waiting for ArgoCD to be ready..."
kubectl wait --for=condition=ready pod --all -n argocd --timeout=600s

# 5. Apply GitOps Applications
echo "Deploying Wisecow App and Prometheus Stack via ArgoCD..."
kubectl apply -f argocd/prometheus-application.yaml
kubectl apply -f argocd/wisecow-application.yaml
kubectl apply -f argocd/argocd-ingress.yaml

echo "Bootstrap Complete!"
echo ""
echo "Waiting for AWS Load Balancer..."
LB_URL=""
while [ -z "$LB_URL" ]; do
  sleep 5
  LB_URL=$(kubectl get svc ingress-nginx-controller -n ingress-nginx -o jsonpath='{.status.loadBalancer.ingress[0].hostname}' 2>/dev/null || true)
done

ARGOCD_PW=$(kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" 2>/dev/null | base64 -d || echo "Not ready yet")

echo "=========================================================================="
echo " SUCCESS! Load Balancer: $LB_URL"
echo " ArgoCD Admin Password: $ARGOCD_PW"
echo "=========================================================================="
