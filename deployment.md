# Azure Container Registry Instance
- Create an ACS instance
- Get access keys for your instance under Settings->Access Keys
- Use this password for login


# Build Docker Imgae
docker build -t tbvision.azurecr.io/tbvision:v1 .

docker login tbvision.azurecr.io

docker push tbvision.azurecr.io/tbvision:v1 