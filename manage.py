import os
import subprocess
import argparse
import sys

# Variables por defecto (equivalentes a las del Makefile)
CLUSTER_NAME = os.getenv("CLUSTER_NAME", "wisecow-cluster")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
NAMESPACE = os.getenv("NAMESPACE", "wisecow")
IMAGE_TAG = os.getenv("IMAGE_TAG", "latest")
REGISTRY = os.getenv("REGISTRY", "ghcr.io/anuragstark/wisecow")

# Colores para la terminal
YELLOW = '\033[1;33m'
GREEN = '\033[0;32m'
RED = '\033[0;31m'
NC = '\033[0m' # No Color

def run_command(command, cwd=None, exit_on_error=True):
    """Ejecuta un comando en la terminal y maneja errores."""
    try:
        subprocess.run(command, shell=True, check=True, cwd=cwd)
    except subprocess.CalledProcessError as e:
        print(f"{RED}Error ejecutando: {command}{NC}")
        if exit_on_error:
            sys.exit(1)

def build():
    """Construye la imagen de Docker."""
    print(f"{YELLOW}Building Docker image...{NC}")
    run_command(f"docker build -t {REGISTRY}:{IMAGE_TAG} .")
    print(f"{GREEN}Image built successfully{NC}")

def push():
    """Sube la imagen de Docker al registro."""
    print(f"{YELLOW}Pushing image to registry...{NC}")
    run_command(f"docker push {REGISTRY}:{IMAGE_TAG}")
    print(f"{GREEN}Image pushed successfully{NC}")

def terraform_init():
    """Inicializa Terraform."""
    print(f"{YELLOW}Initializing Terraform...{NC}")
    run_command("terraform init", cwd="terraform")
    print(f"{GREEN}Terraform initialized{NC}")

def terraform_plan():
    """Planifica el despliegue de Terraform."""
    print(f"{YELLOW}Planning Terraform deployment...{NC}")
    run_command("terraform plan", cwd="terraform")
    print(f"{GREEN}Terraform plan completed{NC}")

def terraform_apply():
    """Aplica la configuración de Terraform."""
    print(f"{YELLOW}Applying Terraform configuration...{NC}")
    run_command("terraform apply -auto-approve", cwd="terraform")
    print(f"{GREEN}Infrastructure deployed{NC}")

def terraform_destroy():
    """Destruye la infraestructura de Terraform."""
    print(f"{YELLOW}Destroying Terraform infrastructure...{NC}")
    run_command("terraform destroy -auto-approve", cwd="terraform")
    print(f"{GREEN}Infrastructure destroyed{NC}")

def kubeconfig():
    """Actualiza la configuración de kubeconfig."""
    print(f"{YELLOW}Updating kubeconfig...{NC}")
    run_command(f"aws eks update-kubeconfig --region {AWS_REGION} --name {CLUSTER_NAME}")
    print(f"{GREEN}Kubeconfig updated{NC}")

def setup_cluster():
    """Configura los componentes del cluster con Ansible."""
    print(f"{YELLOW}Setting up cluster components...{NC}")
    run_command("ansible-playbook ansible/setup-cluster.yaml --ask-become-pass")
    print(f"{GREEN}Cluster setup completed{NC}")

def deploy_app():
    """Despliega la aplicación en Kubernetes."""
    print(f"{YELLOW}Deploying application...{NC}")
    run_command("kubectl apply -f k8s/deployment.yaml")
    run_command("kubectl apply -f k8s/service.yaml")
    run_command("kubectl apply -f k8s/cluster-issuer.yaml")
    run_command("kubectl apply -f k8s/ingress.yaml")
    print(f"{GREEN}Application deployed{NC}")

def health_check():
    """Ejecuta el chequeo de salud."""
    print(f"{YELLOW}Performing health check...{NC}")
    run_command("./scripts/health-check.sh")

def deploy():
    """Despliegue completo (infraestructura + aplicación)."""
    terraform_apply()
    kubeconfig()
    setup_cluster()
    deploy_app()
    print(f"{GREEN}Full deployment completed{NC}")
    health_check()

def clean():
    """Limpia todos los recursos."""
    print(f"{YELLOW}Cleaning up resources...{NC}")
    run_command("./scripts/cleanup.sh")
    print(f"{GREEN}Cleanup completed{NC}")

def logs():
    """Muestra los logs de la aplicación."""
    print(f"{YELLOW}Viewing application logs...{NC}")
    run_command(f"kubectl logs -f deployment/wisecow-deployment -n {NAMESPACE}")

def scale(replicas):
    """Escala la aplicación al número de réplicas deseado."""
    print(f"{YELLOW}Scaling application to {replicas} replicas...{NC}")
    run_command(f"kubectl scale deployment wisecow-deployment --replicas={replicas} -n {NAMESPACE}")
    print(f"{GREEN}Application scaled{NC}")

def status():
    """Muestra el estado de la aplicación."""
    print(f"{YELLOW}Application Status:{NC}")
    run_command(f"kubectl get pods,svc,ingress -n {NAMESPACE}")

def main():
    parser = argparse.ArgumentParser(description="Wisecow Application Management en Python")
    subparsers = parser.add_subparsers(dest="command", help="Comandos disponibles")

    subparsers.add_parser("build", help="Construye la imagen de Docker")
    subparsers.add_parser("push", help="Sube la imagen de Docker al registro")
    subparsers.add_parser("terraform-init", help="Inicializa Terraform")
    subparsers.add_parser("terraform-plan", help="Planifica el despliegue de Terraform")
    subparsers.add_parser("terraform-apply", help="Aplica la configuración de Terraform")
    subparsers.add_parser("terraform-destroy", help="Destruye la infraestructura de Terraform")
    subparsers.add_parser("kubeconfig", help="Actualiza kubeconfig")
    subparsers.add_parser("setup-cluster", help="Configura el cluster con Ansible")
    subparsers.add_parser("deploy-app", help="Despliega la aplicación en k8s")
    subparsers.add_parser("deploy", help="Despliegue completo (infra + app)")
    subparsers.add_parser("health-check", help="Chequeo de salud")
    subparsers.add_parser("clean", help="Limpia todos los recursos")
    subparsers.add_parser("logs", help="Muestra los logs de la app")
    subparsers.add_parser("status", help="Muestra el estado de la aplicación")
    
    scale_parser = subparsers.add_parser("scale", help="Escala la aplicación")
    scale_parser.add_argument("replicas", type=int, help="Número de réplicas")

    args = parser.parse_args()

    # Mapear el comando a la función
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
