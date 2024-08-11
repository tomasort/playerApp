#!/bin/sh

# Enable strict error handling
set -o errexit  # Exit on any command failure
set -o pipefail # Exit if any command in a pipeline fails
set -o nounset  # Exit on use of uninitialized variables

# Execute the command provided as arguments to the script
exec "$@"