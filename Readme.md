# Flaskapp Platform Engineering

A simple and automated project that deploys a Python Flask "Hello World!" application to an **AWS EKS** (Kubernetes) cluster using **GitOps**.

Everything is automated, from creating the infrastructure to building and deploying the app.

---

## 🛠️ Technologies Used

- **App**: Python, Flask, Docker
- **Infrastructure**: Terraform (IaC), AWS EKS
- **CI/CD**: GitHub Actions (Build, Test)
- **Deployment**: ArgoCD (GitOps) & Argo Rollouts (Canary)
- **Security**: Trivy (Docker scan) & Checkov (Terraform/Helm scan)
- **Observability**: Prometheus & Grafana

---

## 🚀 How It Works

1. **Infrastructure**: Terraform creates a VPC and an EKS cluster in AWS via a GitHub Actions workflow.
2. **CI Pipeline**: Whenever you push code, GitHub Actions runs tests (`pytest`), scans the Docker image for vulnerabilities, and pushes it to GitHub Container Registry (GHCR).
3. **CD Pipeline (GitOps)**: ArgoCD watches this repository and automatically deploys any new versions of the application to the Kubernetes cluster.

---

## 📋 Prerequisites

To deploy this yourself, you need:
1. An **AWS Account**.
2. The following **GitHub Secrets** configured in your repository:
   - `AWS_ACCESS_KEY_ID`
   - `AWS_SECRET_ACCESS_KEY`
   - `SMTP_APP_PASSWORD` (For Alertmanager email alerts)
   - `GRAFANA_ADMIN_PASSWORD` (For Grafana dashboard access)

---

## ▶️ Getting Started

You don't need to run anything locally. Everything is done through GitHub Actions:

1. **Deploy Infrastructure**: Go to the **Actions** tab on GitHub, select **Infrastructure Deploy**, and run it. This creates the AWS resources and installs ArgoCD.
2. **Deploy the App**: ArgoCD will automatically detect the configurations in the `argocd/` folder and deploy the app.
3. **Make Changes**: Modify `app.py`, commit, and push. The CI/CD pipeline will automatically test, build, and deploy your changes.
4. **Clean up**: When you are done, run the **Infrastructure Destroy** action to delete all AWS resources and avoid unexpected charges.

---

## 📁 Repository Structure

```text
├── .github/workflows/       # GitHub Actions pipelines (CI/CD, Infra Deploy/Destroy)
├── argocd/                  # ArgoCD deployment configurations
├── helm/flaskapp/           # Helm chart for the Kubernetes app
├── scripts/                 # Helpful bash scripts (bootstrap, deploy, monitor, etc.)
├── terraform/               # Terraform code to create AWS VPC & EKS
├── app.py                   # Python Flask Application ("Hello World!")
├── docker-compose.yml       # Local development setup
├── Dockerfile               # Docker configuration
├── manage.py                # Local management script
├── requirements.txt         # Python dependencies
├── test_app.py              # Unit tests
└── .trivyignore             # Ignored vulnerabilities for Trivy
```