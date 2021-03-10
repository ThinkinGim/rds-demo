# About this Repo
This repo will offer the method to be able to bootstrap your cdk-pipelines project written by Python language. It([AWS Developer Blog: CDK Pipelines](https://aws.amazon.com/ko/blogs/developer/cdk-pipelines-continuous-delivery-for-aws-cdk-applications/)) would say a game changer to manage whole life cycle of your software development because it provide you the mechanism to handle from provisioning infrastructure to business application.

# Bootstrapping cdk-pipelines
1. To make sure CDK runtime environment is available

    ``` bash
    # Installing aws cli: https://docs.aws.amazon.com/cli/  latest/userguide/install-cliv2-linux. html#cliv2-linux-install
    $ curl "https://awscli.amazonaws.com/   awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
    $ unzip awscliv2.zip
    $ sudo ./aws/install

    $ sudo npm install -g npm && sudo npm install -g aws-cdk
    $ cdk --version
    ```

2. Python virtual environment

    Python AWS CDK applications require Python 3.6 or later.
    ``` bash
    $ sudo apt-get update && sudo apt-get -y upgrade
    $ sudo apt install build-essential zlib1g-dev libncurses5-dev libgdbm-dev libnss3-dev libssl-dev libreadline-dev libffi-dev wget

    $ wget https://www.python.org/ftp/python/3.8.6/Python-3.8.6.tar.xz
    $ tar -xf Python-3.8.6.tar.xz
    $ cd Python-3.8.6
    $ ./configure --enable-optimizations
    $ make
    $ sudo make altinstall
    $ python3.8 --version
    ```

    To activate a virtualenv:
    ``` bash
    $ python -m venv .env
    $ source .env/bin/activate
    ```
    
    To install the required dependencies:
    ``` bash
    $ pip install --upgrade pip && pip install -r requirements.txt
    ```

3. Prerequisites

4. example command to synth and deploy cdk-pipelines of this

    ``` bash
    $ cdk -c secret_name=my_secret -c region=ap-northeast-2 synth
    ```