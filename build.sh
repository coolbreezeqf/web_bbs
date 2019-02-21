set -ex
pwd

source .env

cp /var/www/web_bbs/web_bbs.conf /etc/supervisor/conf.d/web_bbs.conf
cp /var/www/web_bbs/web_bbs.nginx /etc/nginx/sites-enabled/web_bbs

pip3 install -r requirements.txt
supervisorctl restart web_bbs
service nginx restart