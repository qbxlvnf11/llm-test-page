### - Set Configuration

<details>
<summary>Set Configuration Procedure</summary>

1.  **Create a `.env` file** in the root of the project directory.

2.  **Set the environment variable** inside the `.env` file. Add the following line and replace the placeholder with the absolute path to your Google Cloud service account JSON key.

    ```ini
    # .env
    GOOGLE_APPLICATION_CREDENTIALS_PATH="/path/to/your/service-account-key.json"
    ```

</details>


### - Run Server

<details>
<summary>Server Execution Procedure</summary>

1. Create Docker Network in Server

```
docker network create api_server_network
```

2. Build Server Docker Env

```
docker build --build-arg SERVER_PORT={SERVER_PORT} -t api_server_env -f Dockerfile .
```

3. Run Server Docker Container 

```
export PUBLIC_IP=$(curl -s ifconfig.me)
docker run --rm -d --name api_server -p {SERVER_PORT}:{SERVER_PORT} --network api_server_network -e PUBLIC_IP=$PUBLIC_IP api_server_env
```

4. Check Real-Time Logs

```
docker logs -f api_server
```

</details>

### - GCP Cloud Run (SDK Shell)

<details>
<summary>Set Configuration Procedure</summary>

1. Preparation

```
gcloud auth login
gcloud config set project [GCP_PROJECT_ID]
# Checking Docker Build 
docker build --build-arg SERVER_PORT={SERVER_PORT} -t api_server_env -f Dockerfile .
```

2. Push the image to Google Container Registry (GCR) or Artifact Registry

```
# Region settings (Check if asia-south3 is supported by GCR; most use asia.gcr.io)
gcloud config set compute/region asia-south3
# Docker authentication
gcloud auth configure-docker
# Image tagging and pushing
docker tag api_server_env asia.gcr.io/[GCP_PROJECT_ID]/api_server_env:latest
docker push asia.gcr.io/[GCP_PROJECT_ID]/api_server_env:latest
```

3. Deploy to Cloud Run

```
gcloud run deploy api-server \
  --image asia.gcr.io/[GCP_PROJECT_ID]/api_server_env:latest \
  --platform managed \
  --region asia-south1 \
  --allow-unauthenticated
```

4. Grant permission to expose the Cloud Run service to the external Internet so that anyone can access it.

* If you encounter permission issues such as "Error: Forbidden Your client does not have permission to get URL from this server," modify the iam.allowedPolicyMemberDomains organization policy.

```
gcloud beta run services add-iam-policy-binding api-server --region=asia-south1 --member=allUsers --role=roles/run.invoker
```

</details>
