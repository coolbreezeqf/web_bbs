pwd

git checkout dev
git pull

source .env

pip install -r requirements.txt
supervisorctl restart web_bbs