# Build and Deployment

## Building the application

Once you have installed all the dependencies, you can proceed with building the application.

### Backend Application
For the backend python/django application, navigate to the project directory and run the following command to build the application:

1. Navigate to the project directory: `cd Group10/`
2. Install the backend dependencies: `poetry install`
3. Run the server: `poetry run python manage.py runserver`

To run test cases on the backend application

```
python manage.py test
```

Building/Checking backend in CI/CD pipeline:

* There exists a job name `code-test` in which the backend application gets build and tested
* The section in `before-script` installs all the dependencies in the docker environment.
* The `script` block runs the script for checking the backend application with all the basics runtime checks and test operations.
* The backend application is then deployed on the Virtual Machine (Instance/Server)
* It belongs to the `deploy` stage and uses the `alpine:latest` Docker image.
* Configuration setup includes changing SSH key permissions and installing the `openssh-client` package. The main script connects to a server via SSH, executing the `deploy_prod.sh` script.

The `deploy_prod.sh` looks like this 

```
#!/bin/bash

INSTANCE_PASS="password"
PROJECT_DIR="/home/deployer/Group10"

# Change to project directory or exit if unsuccessful
cd "$PROJECT_DIR" || { echo "Failed to change directory. Exiting."; exit 1; }

echo "Directory changed to $PROJECT_DIR"

# Switch to the main branch and pull the latest changes
git checkout main
git pull origin main

# Reset local changes to match the main branch
git reset --hard origin/main

# Install project dependencies using Poetry
python3 -m poetry install

# Reload systemd daemon to apply changes
echo "$INSTANCE_PASS" | sudo -S systemctl daemon-reload

# Restart Gunicorn socket and service
echo "$INSTANCE_PASS" | sudo -S systemctl restart gunicorn.socket gunicorn.service

# Check Nginx configuration and restart Nginx
echo "$INSTANCE_PASS" | sudo -S nginx -t && sudo -S systemctl restart nginx
```

If you go to your VM host with respective port you can see your backend code running.

### Frontend Application
For the frontend React application, navigate to the project directory and run the following commands to install the required dependencies:

1. Navigate to the frontend directory: `cd static/refactor-ui`
2. Install the frontend dependencies: `yarn install`
3. Build the frontend: `yarn start`

Building frontend application in CI/CD pipeline:

* There exists a job name `app-build` in which the frontend application gets build
* The section in `before-script` installs all the dependencies in the docker environment which are there in `package.json`.
* The `script` block runs the script for building the application with the command `yarn build`.
* The frontend application is then deployed on the Virtual Machine (Instance/Server)
* The script uses SCP (`scp` command) to securely copy the contents of the `$FRONTEND_BUILD_PATH` on the local machine to a specified destination on a remote server (`$SERVER_USER@$SERVER_IP:$INSTANCE_BUILD_PATH`). This is done using the SSH private key specified in `$SSH_PRIVATE_KEY`. The `-o StrictHostKeyChecking=no` flag disables strict host key checking for the SCP and SSH commands.
* Then it runs the `deploy_prod.sh` again to update the instance with the latest build.

To check whether the frontend application has been successfully deployed, you can navigate to the URL of the of host server.

By following the steps outlined in this document, you should be able to build and deploy your web application using GitLab CI/CD.

[**Go back to README.md**](../README.md)