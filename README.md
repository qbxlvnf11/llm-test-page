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
docker build --build-arg SERVER_PORT={SERVER_PORT} -t api_server_env -f Dockerfile.server .
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