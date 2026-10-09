import os, subprocess, sys

# Config from environment variables with default values
CLUSTER_NAME = os.getenv("CLUSTER_NAME", "flaskapp-cluster")
AWS_REGION   = os.getenv("AWS_REGION", "us-east-1")
NAMESPACE    = os.getenv("NAMESPACE", "flaskapp")
IMAGE_TAG    = os.getenv("IMAGE_TAG", "latest")
REGISTRY     = os.getenv("REGISTRY", "ghcr.io/hellojaviergarcia/flaskapp")

def run(cmd, cwd=None):
    """Runs a shell command, exits with error if it fails."""
    try:
        subprocess.run(cmd, shell=True, check=True, cwd=cwd)
    except subprocess.CalledProcessError:
        print(f"Error: {cmd}"); sys.exit(1)

def tf(sub):
    """Shortcut for terraform commands; appends -auto-approve on apply/destroy."""
    run(f"terraform {sub} {'-auto-approve' if sub in ('apply','destroy') else ''}", cwd="terraform")

# Command dictionary: each key is the CLI command name
# and its value is a lambda function that executes it
COMMANDS = {
    # Docker
    "build":             lambda: run(f"docker build -t {REGISTRY}:{IMAGE_TAG} ."),
    "push":              lambda: run(f"docker push {REGISTRY}:{IMAGE_TAG}"),

    # Terraform (infrastructure)
    "terraform-init":    lambda: tf("init"),
    "terraform-plan":    lambda: tf("plan"),
    "terraform-apply":   lambda: tf("apply"),
    "terraform-destroy": lambda: tf("destroy"),

    # Kubernetes / AWS
    "kubeconfig":        lambda: run(f"aws eks update-kubeconfig --region {AWS_REGION} --name {CLUSTER_NAME}"),
    "setup-cluster":     lambda: run("ansible-playbook ansible/setup-cluster.yaml --ask-become-pass"),
    "deploy-app":        lambda: [run(f"kubectl apply -f k8s/{f}") for f in ("deployment.yaml","service.yaml","cluster-issuer.yaml","ingress.yaml")],

    # Full deploy: chains all steps in order
    "deploy":            lambda: [COMMANDS[c]() for c in ("terraform-apply","kubeconfig","setup-cluster","deploy-app","health-check")],

    # Utilities
    "health-check":      lambda: run("./scripts/health-check.sh"),
    "clean":             lambda: run("./scripts/cleanup.sh"),
    "logs":              lambda: run(f"kubectl logs -f deployment/flaskapp-deployment -n {NAMESPACE}"),
    "status":            lambda: run(f"kubectl get pods,svc,ingress -n {NAMESPACE}"),

    # Scales the deployment; replica count comes from sys.argv[2]
    "scale":             lambda: run(f"kubectl scale deployment flaskapp-deployment --replicas={sys.argv[2]} -n {NAMESPACE}"),
}

# Entry point: reads the first argument as the command
cmd = sys.argv[1] if len(sys.argv) > 1 else ""
if cmd in COMMANDS:
    COMMANDS[cmd]()
else:
    # If command not found, print available ones
    print(f"Commands: {', '.join(COMMANDS)}")
