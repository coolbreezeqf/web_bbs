set -ex
pwd

source .env
PROJECT="web_bbs"
cp /var/www/$PROJECT/$PROJECT.conf /etc/supervisor/conf.d/$PROJECT.conf
cp /var/www/$PROJECT/$PROJECT.nginx /etc/nginx/sites-enabled/$PROJECT

pip3 install -r requirements.txt
supervisorctl restart $PROJECT
service nginx restart