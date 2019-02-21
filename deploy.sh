# 1. 拉代码到 /var/www/web21
# 2. 执行 bash deploy.sh

set -ex

# 装载环境变量
if [ ! -f ".env" ];then
    source .env
fi

# 系统设置
apt-get install -y zsh curl ufw
# sh -c "$(curl -fsSL https://raw.githubusercontent.com/robbyrussell/oh-my-zsh/master/tools/install.sh)"
ufw allow 22
ufw allow 80
ufw allow 443
ufw allow 465
ufw default deny incoming
ufw default allow outgoing
ufw status verbose
ufw -f enable

# 装依赖
apt-get install -y git supervisor nginx python3-pip mysql-server redis-server
pip3 install jinja2 flask gevent gunicorn pymysql flask_sqlalchemy flask_mail redis

# 设置密码
# mysql -e "UPDATE mysql.user SET authentication_string=PASSWORD('web13123') WHERE User='root';"
# 正确设置密码验证方式
# mysql -e "UPDATE mysql.user SET plugin='mysql_native_password' WHERE User='root';"
# 删除测试用户和测试数据库
mysql -e "DELETE FROM mysql.user WHERE User='';"
mysql -e "DELETE FROM mysql.user WHERE User='root' AND Host NOT IN ('localhost', '127.0.0.1', '::1');"
mysql -e "DROP DATABASE IF EXISTS test;"
mysql -e "DELETE FROM mysql.db WHERE Db='test' OR Db='test\\_%';"

# 删掉 nginx default 设置
rm -f /etc/nginx/sites-enabled/default
rm -f /etc/nginx/sites-available/default

cp /var/www/web_bbs/web_bbs.conf /etc/supervisor/conf.d/web_bbs.conf
# 不要再 sites-available 里面放任何东西
cp /var/www/web_bbs/web_bbs.nginx /etc/nginx/sites-enabled/web_bbs
chmod -R o+rwx /var/www/web_bbs

# 初始化
cd /var/www/web_bbs
python3 reset.py

# 重启服务器
service supervisor restart
service nginx restart

echo 'succsss'
echo 'ip'
hostname -I