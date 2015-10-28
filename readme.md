# 安装cmdb
## 后端项目
```
git clone https://gitcafe.com/hudson/cmdb.git
cd cmdb
python setup.py build
python setup.py install
```
## 前端项目
```
git clone https://gitcafe.com/hudson/cmdb-front.git
```
## 安装数据库
使用 couchdb 作为后端数据库,安装依赖
```
sudo yum -y install autoconf
sudo yum -y install autoconf-archive
sudo yum -y install automake
sudo yum -y install curl-devel
sudo yum -y install erlang-asn1
sudo yum -y install erlang-erts
sudo yum -y install erlang-eunit
sudo yum -y install erlang-os_mon
sudo yum -y install erlang-xmerl
sudo yum -y install help2man
sudo yum -y install js-devel
sudo yum -y install libicu-devel
sudo yum -y install libtool
sudo yum -y install perl-Test-Harness
```
下载
```
wget http://mirrors.hust.edu.cn/apache/couchdb/source/1.6.1/apache-couchdb-1.6.1.tar.gz
tar xzf apache-couchdb-1.6.1.tar.gz
cd apache-couchdb-1.6.1
./configure --with-erlang=/usr/lib64/erlang/usr/include/
make && sudo make install
```
### 启动
Linux
```
sudo adduser -r -d /usr/local/var/lib/couchdb couchdb
sudo chown -R couchdb /usr/local/var/lib/couchdb
sudo chown -R couchdb /usr/local/var/log/couchdb
sudo chown -R couchdb /usr/local/etc/couchdb/local.ini
sudo chown -R couchdb /usr/local/var/run/couchdb

sudo -u couchdb /usr/local/bin/couchdb -b

or
/usr/local/etc/init.d/couchdb start
```
MacOS
```
/usr/local/Cellar/couchdb/1.6.1_3/bin/couchdb
```

### 初始化
建库,desgin
```
./db.sh
```
test
```
curl http://localhost:5984/cmdb/_design/service/_view/list
curl http://localhost:5984/cmdb/_design/service/_list/get_service/list?name=tomcat
curl http://localhost:5984/cmdb/_design/project/_view/list?group=true
```


# 服务api
/api/v1/service/<service id>
## 查看服务
GET
## 添加服务
```
curl -X POST http://localhost:8005/api/v1/service/1.1.1.1:8080 -d 'name=hello'
```
# 更新服务
```
curl -X PUT http://localhost:8005/api/v1/service/1.1.1.1:8080 -d 'name=world'
```
# 删除服务
删除整个服务
```
curl -X DELETE http://127.0.0.1:8005/api/v1/service/1.1.1.1:8080
```

删除字段
```
curl -X DELETE http://127.0.0.1:8005/api/v1/service/1.1.1.1:8080field=f1
```

删除某几个字段
```
curl -X DELETE 'http://127.0.0.1:8005/api/v1/service/1.1.1.1:8080?field=f1&field=f2
```

# 项目api
/api/v1/project/<project id>

## 查看

## 添加项目
```
curl -X POST http://localhost:8005/api/v1/project/测试项目 -d 'name=hello'
```

## 为项目添加服务

## 更新

