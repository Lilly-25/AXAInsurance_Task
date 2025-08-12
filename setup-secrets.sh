#!/bin/bash
# GitHub Secrets Setup Helper
# Run this after setting up secrets in GitHub

echo "🔐 GitHub Secrets Setup Guide"
echo "=============================="
echo ""
echo "Go to: https://github.com/Lilly-25/AXAInsurance_Task/settings/secrets/actions"
echo ""
echo "Add these secrets:"
echo "==================="
echo "TEST_DB_USER: postgres"
echo "TEST_DB_PASSWORD: secure_test_password123"
echo "TEST_DB_NAME: titanic_test"
echo ""
echo "Optional:"
echo "========="
echo "SLACK_WEBHOOK: https://hooks.slack.com/your/webhook/url"
echo ""
echo "After adding secrets, your CI/CD pipeline will work correctly!"
echo ""
echo "Check pipeline status: https://github.com/Lilly-25/AXAInsurance_Task/actions"
