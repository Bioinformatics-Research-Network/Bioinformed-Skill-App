FROM gitpod/workspace-full:latest

RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" && unzip awscliv2.zip
RUN sudo ./aws/install -i /usr/local/aws-cli -b /usr/local/bin
RUN aws --profile default configure set aws_access_key_id $AWS_ACCESS_KEY_ID && \
aws --profile default configure set aws_secret_access_key $AWS_SECRET_ACCESS_KEY 
RUN aws s3 cp s3://skill-assessment-app/secrets/.env.download.sh . && ./.env.download.sh

RUN pyenv install 3.10.4
RUN pyenv global 3.10.4
RUN python -m venv venv && source venv/bin/activate && pip install --upgrade -r requirements.txt 
