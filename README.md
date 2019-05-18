# githubers

Scripts for getting developers info from GitHub

#### Install
```bash
pip3 install -r requirements.txt
```

#### Run
```bash
python3 stargazers.py --repos https://github.com/josephmisiti/awesome-machine-learning https://github.com/tensorflow/models \
--login my_github_login \
--password my_github_password \
--output-file stargazers.tsv
```