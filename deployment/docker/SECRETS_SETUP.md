# FortiGate Secrets Setup

This directory requires a `secrets/` subdirectory with the following files for FortiGate services:

## Required Secret Files

Create these files in `deployment/docker/secrets/`:

1. **fortigate_api_token.txt**
   - Contains your FortiGate API token
   - Example: `your_api_token_here`

2. **fortigate_password.txt**
   - Contains your FortiGate admin password
   - Example: `your_admin_password`

3. **fortiswitch_password.txt**
   - Contains your FortiSwitch admin password
   - Example: `your_fortiswitch_password`

## Setup Instructions

```bash
# Create the secrets directory
mkdir -p deployment/docker/secrets

# Add your actual credentials to these files
echo "your_fortigate_api_token" > deployment/docker/secrets/fortigate_api_token.txt
echo "your_admin_password" > deployment/docker/secrets/fortigate_password.txt
echo "your_fortiswitch_password" > deployment/docker/secrets/fortiswitch_password.txt
```

## Security Note

The `secrets/` directory is excluded from Git via `.gitignore` for security.
Never commit actual credentials to version control.
