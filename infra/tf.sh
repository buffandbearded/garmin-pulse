#!/usr/bin/env bash
# Run Terraform in a container on the Compose network (Git Bash on Windows).
cd "$(dirname "$0")/terraform" || exit 1
MSYS_NO_PATHCONV=1 docker run --rm --network repo_default \
  -v "$(pwd -W):/work" -w /work hashicorp/terraform:1.9 "$@"
