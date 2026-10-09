import os
import subprocess
import argparse
import sys

# Default variables (equivalent to Makefile)
CLUSTER_NAME = os.getenv("CLUSTER_NAME", "flaskapp-cluster")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
NAMESPACE = os.getenv("NAMESPACE", "flaskapp")
IMAGE_TAG = os.getenv("IMAGE_TAG", "latest")
REGISTRY = os.getenv("REGISTRY", "ghcr.io/hellojaviergarcia/flaskapp")

# Terminal colors
YELLOW = '\033[1;33m'
GREEN = '\033[0;32m'
RED = '\033[0;31m'
NC = '\033[0m' # No Color

def run_command(command, cwd=None, exit_on_error=True):
    """Executes a command in the terminal and handles errors."""
    try:
        subprocess.run(command, shell=True, check=True, cwd=cwd)
    except subprocess.CalledProcessError as e:
        print(f"{RED}Error executing: {command}{NC}")
        if exit_on_error:
            sys.exit(1)

def build():
    """Builds the Docker image."""
    print(f"{YELLOW}Building Docker image...{NC}")
    run_command(f"docker build -t {REGISTRY}:{IMAGE_TAG} .")
    print(f"{GREEN}Image built successfully{NC}")

def push():
    """Pushes the Docker image to the registry."""
    print(f"{YELLOW}Pushing image to registry...{NC}")
    run_command(f"docker push {REGISTRY}:{IMAGE_TAG}")
    print(f"{GREEN}Image pushed successfully{NC}")

def terraform_init():
    """Initializes Terraform."""
    print(f"{YELLOW}Initializing Terraform...{NC}")
    run_command("terraform init", cwd="terraform")
    print(f"{GREEN}Terraform initialized{NC}")

def terraform_plan():
    """Plans the Terraform deployment."""
    print(f"{YELLOW}Planning Terraform deployment...{NC}")
    run_command("terraform plan", cwd="terraform")
    print(f"{GREEN}Terraform plan completed{NC}")

def terraform_apply():
    """Applies the Terraform configuration."""
    print(f"{YELLOW}Applying Terraform configuration...{NC}")
    run_command("terraform apply -auto-approve", cwd="terraform")
    print(f"{GREEN}Infrastructure deployed{NC}")

def terraform_destroy():
    """Destroys the Terraform infrastructure."""
    print(f"{YELLOW}Destroying Terraform infrastructure...{NC}")
    run_command("terraform destroy -auto-approve", cwd="terraform")
    print(f"{GREEN}Infrastructure destroyed{NC}")

def kubeconfig():
    """Updates the kubeconfig configuration."""
    print(f"{YELLOW}Updating kubeconfig...{NC}")
    run_command(f"aws eks update-kubeconfig --region {AWS_REGION} --name {CLUSTER_NAME}")
    print(f"{GREEN}Kubeconfig updated{NC}")

def setup_cluster():
    """Sets up cluster components with Ansible."""
    print(f"{YELLOW}Setting up cluster components...{NC}")
    run_command("ansible-playbook ansible/setup-cluster.yaml --ask-become-pass")
    print(f"{GREEN}Cluster setup completed{NC}")

def deploy_app():
    """Deploys the application to Kubernetes."""
    print(f"{YELLOW}Deploying application...{NC}")
    run_command("kubectl apply -f k8s/deployment.yaml")
    run_command("kubectl apply -f k8s/service.yaml")
    run_command("kubectl apply -f k8s/cluster-issuer.yaml")
    run_command("kubectl apply -f k8s/ingress.yaml")
    print(f"{GREEN}Application deployed{NC}")

def health_check():
    """Executes the health check."""
    print(f"{YELLOW}Performing health check...{NC}")
    run_command("./scripts/health-check.sh")

def deploy():
    """Full deployment (infrastructure + application)."""
    terraform_apply()
    kubeconfig()
    setup_cluster()
    deploy_app()
    print(f"{GREEN}Full deployment completed{NC}")
    health_check()

def clean():
    """Cleans up all resources."""
    print(f"{YELLOW}Cleaning up resources...{NC}")
    run_command("./scripts/cleanup.sh")
    print(f"{GREEN}Cleanup completed{NC}")

def logs():
    """Displays the application logs."""
    print(f"{YELLOW}Viewing application logs...{NC}")
    run_command(f"kubectl logs -f deployment/flaskapp-deployment -n {NAMESPACE}")

def scale(replicas):
    """Scales the application to the desired number of replicas."""
    print(f"{YELLOW}Scaling application to {replicas} replicas...{NC}")
    run_command(f"kubectl scale deployment flaskapp-deployment --replicas={replicas} -n {NAMESPACE}")
    print(f"{GREEN}Application scaled{NC}")

def status():
    """Displays the application status."""
    print(f"{YELLOW}Application Status:{NC}")
    run_command(f"kubectl get pods,svc,ingress -n {NAMESPACE}")

def main():
    parser = argparse.ArgumentParser(description="Flaskapp Application Management in Python")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    subparsers.add_parser("build", help="Builds the Docker image")
    subparsers.add_parser("push", help="Pushes the Docker image to the registry")
    subparsers.add_parser("terraform-init", help="Initializes Terraform")
    subparsers.add_parser("terraform-plan", help="Plans the Terraform deployment")
    subparsers.add_parser("terraform-apply", help="Applies the Terraform configuration")
    subparsers.add_parser("terraform-destroy", help="Destroys the Terraform infrastructure")
    subparsers.add_parser("kubeconfig", help="Updates kubeconfig")
    subparsers.add_parser("setup-cluster", help="Sets up the cluster with Ansible")
    subparsers.add_parser("deploy-app", help="Deploys the application to k8s")
    subparsers.add_parser("deploy", help="Full deployment (infra + app)")
    subparsers.add_parser("health-check", help="Health check")
    subparsers.add_parser("clean", help="Cleans up all resources")
    subparsers.add_parser("logs", help="Displays the app logs")
    subparsers.add_parser("status", help="Displays the application status")
    
    scale_parser = subparsers.add_parser("scale", help="Scales the application")
    scale_parser.add_argument("replicas", type=int, help="Number of replicas")

    args = parser.parse_args()

    # Map the command to the function
    commands = {
        "build": build,
        "push": push,
        "terraform-init": terraform_init,
        "terraform-plan": terraform_plan,
        "terraform-apply": terraform_apply,
        "terraform-destroy": terraform_destroy,
        "kubeconfig": kubeconfig,
        "setup-cluster": setup_cluster,
        "deploy-app": deploy_app,
        "deploy": deploy,
        "health-check": health_check,
        "clean": clean,
        "logs": logs,
        "status": status,
    }

    if args.command == "scale":
        scale(args.replicas)
    elif args.command in commands:
        commands[args.command]()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
