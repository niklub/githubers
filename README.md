# githubers

Scripts for getting developers info from GitHub

#### Install
```bash
pip3 install -r requirements.txt
```

#### Run
```bash
python3 get_users_info.py \
--stargazer-page https://github.com/awslabs/amazon-sagemaker-examples/stargazers \
--login my_github_login \
--password my_github_password \
--output-file stargazers.tsv
```