#!/bin/bash
# AWS EC2 Setup Script for MLOps Saylani Project
# Run this script locally to set up AWS infrastructure

set -e

echo "==> Step 1: Creating Security Group..."
SG_ID=$(aws ec2 create-security-group \
  --group-name mlops-saylani-sg \
  --description "Security group for MLOps Saylani app" \
  --query 'GroupId' \
  --output text)

echo "Security Group ID: $SG_ID"

echo "==> Step 2: Opening ports (22, 8000, 8501)..."
aws ec2 authorize-security-group-ingress \
  --group-id $SG_ID \
  --protocol tcp --port 22 --cidr 0.0.0.0/0

aws ec2 authorize-security-group-ingress \
  --group-id $SG_ID \
  --protocol tcp --port 8000 --cidr 0.0.0.0/0

aws ec2 authorize-security-group-ingress \
  --group-id $SG_ID \
  --protocol tcp --port 8501 --cidr 0.0.0.0/0

echo "==> Step 3: Creating Key Pair..."
aws ec2 create-key-pair \
  --key-name mlops-saylani-key \
  --query 'KeyMaterial' \
  --output text > mlops-saylani-key.pem

chmod 400 mlops-saylani-key.pem
echo "Key pair saved to mlops-saylani-key.pem"

echo "==> Step 4: Launching EC2 Instance (t3.medium)..."
INSTANCE_ID=$(aws ec2 run-instances \
  --image-id ami-0c02fb55956c7d316 \
  --instance-type t3.medium \
  --key-name mlops-saylani-key \
  --security-group-ids $SG_ID \
  --count 1 \
  --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=mlops-saylani}]' \
  --query 'Instances[0].InstanceId' \
  --output text)

echo "Instance ID: $INSTANCE_ID"
echo "Waiting for instance to start..."
aws ec2 wait instance-running --instance-ids $INSTANCE_ID

echo "==> Step 5: Getting Public IP..."
EC2_IP=$(aws ec2 describe-instances \
  --filters "Name=tag:Name,Values=mlops-saylani" \
  --query "Reservations[0].Instances[0].PublicIpAddress" \
  --output text)

echo ""
echo "=========================================="
echo "AWS Setup Complete!"
echo "=========================================="
echo "Instance ID: $INSTANCE_ID"
echo "Security Group: $SG_ID"
echo "Public IP: $EC2_IP"
echo ""
echo "Next steps:"
echo "1. Wait 2-3 minutes for instance to fully initialize"
echo "2. SSH into instance: ssh -i mlops-saylani-key.pem ec2-user@$EC2_IP"
echo "3. Run the setup commands from the guide"
echo ""
echo "Save this information:"
echo "EC2_IP=$EC2_IP" > aws-info.txt
echo "INSTANCE_ID=$INSTANCE_ID" >> aws-info.txt
echo "SG_ID=$SG_ID" >> aws-info.txt
echo "Saved to aws-info.txt"
