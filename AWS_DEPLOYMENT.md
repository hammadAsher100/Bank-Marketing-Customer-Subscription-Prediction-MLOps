# AWS Deployment Guide - MLOps Saylani

## Quick Start

### Prerequisites
- Docker installed and running
- AWS CLI v2 configured (`aws configure`)
- DockerHub account (hammadasher)

### Step 1: Push Images to DockerHub

**⚠️ IMPORTANT:** The API image is very large (2.69GB). Choose one of these methods:

#### Method A: Use PowerShell Retry Script (Windows - Recommended)
```powershell
.\push-to-dockerhub.ps1
```
This script will retry failed pushes automatically.

#### Method B: Manual Push
```bash
# Login to DockerHub
docker login

# Push frontend (small, fast)
docker push hammadasher/mlops-saylani-frontend:latest

# Push API (large, may take 10-30 minutes)
docker push hammadasher/mlops-saylani-api:latest
```

#### Method C: Skip Push - Build on EC2 Instead (Fastest)
Skip this step entirely and build directly on EC2 (see Alternative Deployment below).

### Step 2: Set Up AWS Infrastructure

Run the automated setup script:

```bash
bash aws-setup.sh
```

This will:
- Create security group with ports 22, 8000, 8501 open
- Create SSH key pair (`mlops-saylani-key.pem`)
- Launch t3.medium EC2 instance
- Save connection info to `aws-info.txt`

**Important:** Keep `mlops-saylani-key.pem` safe and never commit it!

### Step 3: Configure EC2 Instance

SSH into your instance:

```bash
# Get IP from aws-info.txt or run:
EC2_IP=$(aws ec2 describe-instances \
  --filters "Name=tag:Name,Values=mlops-saylani" \
  --query "Reservations[0].Instances[0].PublicIpAddress" \
  --output text)

ssh -i mlops-saylani-key.pem ec2-user@$EC2_IP
```

Inside EC2, run:

```bash
# Install Docker
sudo yum update -y
sudo yum install -y docker
sudo service docker start
sudo usermod -a -G docker ec2-user

# Install Docker Compose
sudo mkdir -p /usr/local/lib/docker/cli-plugins
sudo curl -SL https://github.com/docker/compose/releases/latest/download/docker-compose-linux-x86_64 \
  -o /usr/local/lib/docker/cli-plugins/docker-compose
sudo chmod +x /usr/local/lib/docker/cli-plugins/docker-compose

# Log out and back in for Docker group to take effect
exit
```

SSH back in:

```bash
ssh -i mlops-saylani-key.pem ec2-user@$EC2_IP
```

### Step 4: Deploy Application

```bash
# Create deployment directory
mkdir mlops-saylani && cd mlops-saylani

# Create docker-compose.yml
cat > docker-compose.yml << 'EOF'
services:
  api:
    image: hammadasher/mlops-saylani-api:latest
    container_name: mlops-api
    ports:
      - "8000:8000"
    environment:
      - SPARK_DRIVER_MEMORY=512m
      - SPARK_EXECUTOR_MEMORY=512m
    restart: unless-stopped

  frontend:
    image: hammadasher/mlops-saylani-frontend:latest
    container_name: mlops-frontend
    ports:
      - "8501:8501"
    environment:
      - API_URL=http://api:8000
    depends_on:
      - api
    restart: unless-stopped
EOF

# Pull and start containers
docker compose pull
docker compose up -d

# Check status
docker compose ps
docker compose logs --tail=50
```

### Step 5: Access Your Application

Open in browser:
- **API Documentation:** `http://YOUR_EC2_IP:8000/docs`
- **Streamlit Dashboard:** `http://YOUR_EC2_IP:8501`

## Alternative Deployment: Build Directly on EC2 (Recommended for Large Images)

This is the **fastest and most reliable** method for deploying large Docker images.

### Why Build on EC2?
- ✅ No need to upload 2.69GB to DockerHub
- ✅ No need to download from DockerHub to EC2
- ✅ Faster deployment (5-10 minutes vs 30-60 minutes)
- ✅ No network timeout issues

### Steps:

1. **SSH into EC2** (after completing AWS setup):
```bash
ssh -i mlops-saylani-key.pem ec2-user@YOUR_EC2_IP
```

2. **Run the automated build script**:
```bash
# Download and run the build script
curl -O https://raw.githubusercontent.com/hammadAsher100/MLOps-Saylani/main/build-on-ec2.sh
bash build-on-ec2.sh
```

Or manually:

```bash
# Clone repository
git clone https://github.com/hammadAsher100/MLOps-Saylani.git
cd MLOps-Saylani

# Build images (takes 5-10 minutes)
docker build -f Dockerfile.api -t hammadasher/mlops-saylani-api:latest .
docker build -f Dockerfile.frontend -t hammadasher/mlops-saylani-frontend:latest .

# Start services
docker compose up -d

# Check status
docker compose ps
docker compose logs --tail=50
```

3. **Access your application**:
- API: `http://YOUR_EC2_IP:8000/docs`
- Frontend: `http://YOUR_EC2_IP:8501`

## Automated Redeployment

Use the `deploy.sh` script for future updates:

```bash
# From your local machine
./deploy.sh YOUR_EC2_IP
```

This will:
1. Push latest images to DockerHub
2. SSH into EC2
3. Pull and restart containers

## Monitoring

```bash
# View logs
docker compose logs -f

# Check container status
docker compose ps

# Restart services
docker compose restart

# Stop services
docker compose down
```

## Troubleshooting

### API container exits immediately
```bash
docker compose logs api
# Check for missing model files or memory issues
```

### Port not accessible
```bash
# Verify security group
aws ec2 describe-security-groups --group-names mlops-saylani-sg
```

### Out of memory
```bash
# Upgrade to t3.large or reduce Spark memory
# Edit docker-compose.yml:
# SPARK_DRIVER_MEMORY=256m
# SPARK_EXECUTOR_MEMORY=256m
```

### Streamlit hangs
Ensure `--server.headless=true` is in Dockerfile.frontend CMD

## Cleanup

To remove all AWS resources:

```bash
# Terminate instance
aws ec2 terminate-instances --instance-ids YOUR_INSTANCE_ID

# Delete security group (after instance terminates)
aws ec2 delete-security-group --group-id YOUR_SG_ID

# Delete key pair
aws ec2 delete-key-pair --key-name mlops-saylani-key
rm mlops-saylani-key.pem
```

## Cost Estimate

- **t3.medium:** ~$0.0416/hour (~$30/month if running 24/7)
- **Data transfer:** Minimal for testing
- **Total:** ~$30-40/month

Consider stopping the instance when not in use to save costs:

```bash
# Stop instance
aws ec2 stop-instances --instance-ids YOUR_INSTANCE_ID

# Start instance
aws ec2 start-instances --instance-ids YOUR_INSTANCE_ID
```
