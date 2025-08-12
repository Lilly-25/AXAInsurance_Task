#!/bin/bash
# GitHub Secrets Setup Script
# This script helps set up the required GitHub secrets for the CI/CD pipeline

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🔐 GitHub Secrets Setup for Titanic API${NC}"
echo "========================================"

# Check if GitHub CLI is installed
if ! command -v gh &> /dev/null; then
    echo -e "${RED}❌ GitHub CLI (gh) is not installed${NC}"
    echo "Please install it from: https://cli.github.com/"
    exit 1
fi

# Check if user is authenticated
if ! gh auth status &> /dev/null; then
    echo -e "${YELLOW}🔑 Please authenticate with GitHub CLI first${NC}"
    gh auth login
fi

echo -e "${GREEN}✅ GitHub CLI is ready${NC}"
echo

# Function to set secret if it doesn't exist
set_secret_if_not_exists() {
    local secret_name=$1
    local secret_value=$2
    local description=$3
    
    echo -e "${YELLOW}Setting secret: ${secret_name}${NC}"
    echo "Description: $description"
    
    # Try to set the secret
    if gh secret set "$secret_name" --body "$secret_value"; then
        echo -e "${GREEN}✅ Secret '$secret_name' set successfully${NC}"
    else
        echo -e "${RED}❌ Failed to set secret '$secret_name'${NC}"
    fi
    echo
}

# Function to set variable if it doesn't exist
set_variable_if_not_exists() {
    local var_name=$1
    local var_value=$2
    local description=$3
    
    echo -e "${YELLOW}Setting variable: ${var_name}${NC}"
    echo "Description: $description"
    
    # Try to set the variable
    if gh variable set "$var_name" --body "$var_value"; then
        echo -e "${GREEN}✅ Variable '$var_name' set successfully${NC}"
    else
        echo -e "${RED}❌ Failed to set variable '$var_name'${NC}"
    fi
    echo
}

# Set up test database secrets (required for CI/CD)
echo -e "${GREEN}🗄️ Setting up test database credentials...${NC}"
read -p "Enter test database username: " test_db_user
read -s -p "Enter test database password: " test_db_password
echo
read -p "Enter test database name: " test_db_name

set_secret_if_not_exists "TEST_DB_USER" "$test_db_user" "Test database username"
set_secret_if_not_exists "TEST_DB_PASSWORD" "$test_db_password" "Test database password"
set_secret_if_not_exists "TEST_DB_NAME" "$test_db_name" "Test database name"

# Set up production URL
echo -e "${GREEN}🌐 Setting up production configuration...${NC}"
read -p "Enter production URL (e.g., https://your-api.com): " production_url
if [ ! -z "$production_url" ]; then
    set_variable_if_not_exists "PRODUCTION_URL" "$production_url" "Production API URL for health checks"
fi

# Set up OpenShift flag
read -p "Enable OpenShift deployment? (y/N): " enable_openshift
if [[ $enable_openshift =~ ^[Yy]$ ]]; then
    set_variable_if_not_exists "OPENSHIFT_ENABLED" "true" "Enable OpenShift deployment"
else
    set_variable_if_not_exists "OPENSHIFT_ENABLED" "false" "Disable OpenShift deployment"
fi

echo -e "${GREEN}🎉 GitHub secrets setup completed!${NC}"
echo
echo -e "${YELLOW}📝 Next steps:${NC}"
echo "1. Push your code to trigger the CI/CD pipeline"
echo "2. Monitor the pipeline in the Actions tab"
echo "3. Check pipeline logs if any issues occur"
echo
echo -e "${GREEN}🚀 Your CI/CD pipeline is now ready to run!${NC}"
