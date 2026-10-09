import os, subprocess, sys, argparse

CLUSTER_NAME = os.getenv("CLUSTER_NAME", "flaskapp-cluster")
AWS_REGION   = os.getenv("AWS_REGION", "us-east-1")
NAMESPACE    = os.getenv("NAMESPACE", "flaskapp")
IMAGE_TAG    = os.getenv("IMAGE_TAG", "latest")
REGISTRY     = os.getenv("REGISTRY", "ghcr.io/hellojaviergarcia/flaskapp")

Y, G, R, N = '\033[1;33m', '\033[0;32m', '\033[0;31m', '\033[0m'

def run(cmd, cwd=None):
    try:
        subprocess.run(cmd, shell=True, check=True, cwd=cwd)
    except subprocess.CalledProcessError:
        print(f"{R}Error: {cmd}{N}"); sys.exit(1)

def tf(subcmd): run(f"terraform {subcmd} {'-auto-approve' if subcmd in ('apply','destroy') else ''}", cwd="terraform")

COMMANDS = {
    "build":           lambda: run(f"docker build -t {REGISTRY}:{IMAGE_TAG} ."),
    "push":            lambda: run(f"docker push {REGISTRY}:{IMAGE_TAG}"),
    "terraform-init":  lambda: tf("init"),
    "terraform-plan":  lambda: tf("plan"),
    "terraform-apply": lambda: tf("apply"),
    "terraform-destroy": lambda: tf("destroy"),
    "kubeconfig":      lambda: run(f"aws eks update-kubeconfig --region {AWS_REGION} --name {CLUSTER_NAME}"),
    "setup-cluster":   lambda: run("ansible-playbook ansible/setup-cluster.yaml --ask-become-pass"),
    "deploy-app":      lambda: [run(f"kubectl apply -f k8s/{f}") for f in ("deployment.yaml","service.yaml","cluster-issuer.yaml","ingress.yaml")],
    "health-check":    lambda: run("./scripts/health-check.sh"),
    "clean":           lambda: run("./scripts/cleanup.sh"),
    "logs":            lambda: run(f"kubectl logs -f deployment/flaskapp-deployment -n {NAMESPACE}"),
    "status":          lambda: run(f"kubectl get pods,svc,ingress -n {NAMESPACE}"),
}

def deploy():
    for cmd in ("terraform-apply", "kubeconfig", "setup-cluster", "deploy-app", "health-check"):
        COMMANDS[cmd]()

def main():
    p = argparse.ArgumentParser()
    sp = p.add_subparsers(dest="command")
    for cmd in COMMANDS: sp.add_parser(cmd)
    sp.add_parser("deploy")
    scale_p = sp.add_parser("scale")
    scale_p.add_argument("replicas", type=int)
    args = p.parse_args()

    if args.command == "scale":
        run(f"kubectl scale deployment flaskapp-deployment --replicas={args.replicas} -n {NAMESPACE}")
    elif args.command == "deploy":
        deploy()
    elif args.command in COMMANDS:
        COMMANDS[args.command]()
    else:
        p.print_help()

if __name__ == "__main__":
    main()
