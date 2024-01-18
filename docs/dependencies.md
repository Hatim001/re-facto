# Dependencies

## Installation of Dependencies

### Python

We are using Python - 3.11.4 for our project. The project is compatible with any python version above 3.10

#### To download python we will be using `pyenv`

Install dependencies
```
> sudo apt-get update
> sudo apt-get install git curl libssl-dev libreadline-dev zlib1g-dev
```

Clone `pyenv` repository
```
> git clone https://github.com/pyenv/pyenv.git ~/.pyenv
```

Add pyenv to bashrc or zshrc
```
> echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc
> echo 'export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc
> echo 'eval "$(pyenv init --path)"' >> ~/.bashrc
source ~/.bashrc
```

#### Install Python with `pyenv`

Install basic dependencies
```
> sudo apt-get install -y build-essential libssl-dev zlib1g-dev libbz2-dev \
libreadline-dev libsqlite3-dev wget curl llvm libncurses5-dev libncursesw5-dev \
xz-utils tk-dev libffi-dev liblzma-dev python3-openssl git
```

```
# Install Python 3.11.4
> pyenv install 3.11.4

# Set global Python version
> pyenv global 3.11.4
```

### Poetry
It is a python package package and dependency manager. Its acts just like a virtual environment for the project. To read more about poetry, click [here](https://python-poetry.org/)

```
# Install poetry
> curl -sSL https://install.python-poetry.org | python3 -

# Add poetry to your shell config (bash or zsh)
> echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

### Node (using `nvm`)
We will be using node v19 or greater for our frontend application. To install node we will be using [nvm](https://github.com/nvm-sh/nvm)

#### To install nvm
```
# Install NVM
> curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.38.0/install.sh | bash

# Add NVM to your shell config (bash or zsh)
> echo 'export NVM_DIR="$HOME/.nvm"' >> ~/.bashrc
> echo '[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"' >> ~/.bashrc
> echo '[ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"' >> ~/.bashrc
> source ~/.bashrc
```

#### Install node using nvm
```
# Install Node 19
> nvm install 19

# Set default Node version
> nvm alias default 19
```


#### GitLab Runner
To install your own GitLab Runner instance, follow the official documentation: https://docs.gitlab.com/runner/install/  
A private GitLab runner is recommended to ensure the security and reliability of your CI/CD pipeline.
By using a private runner, you can have more control over the environment and resources used for your builds.  
After installation, verify runner is installed by running:  

```
gitlab-runner --version  
```

### Usage

Once the server is running, you can access the backend application at `http://localhost:8000/` and the frontend application on `http://localhost:3000/`.