# 安装cmdb
## 后端项目
```
git clone https://gitcafe.com/hudson/cmdb.git
cd cmdb
python setup.py install
```
## 前端项目
```
cd cmdb
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


# api

## database 数据库
/api/v1/<database>

### 创建数据库
数据库名只能以小写字母开头,内容必须是字母数字和`-`,`_`
```
curl -X POST http://localhost:8005/api/v1/database/couch-test
{"ok":true}
```
### 查看所有数据库
```
curl http://localhost:8005/api/v1/cmdb
["cmdb", "couch-test"]
```
### 删除数据库
```
curl -X DELETE http://localhost:8005/api/v1/database/couch-test
{"ok":true}
```
## service 服务
/api/v1/<database>/service/<service id>
### 查看服务

```
curl http://localhost:8005/api/v1/cmdb/service/1.1.1.1:8080'
{"name": "tomcat", "ip": "1.1.1.1", "_rev": "229-688a685b088505c1bb8afe94c0458b4f", "_id": "1.1.1.1:8080", "type": "service", "port": "8080"}
```

### 添加服务
```
curl -X POST http://localhost:8005/api/v1/cmdb/service/1.1.1.1:8080 -d 'name=hello'
{"ok":true,"id":"1.1.1.2:8080","rev":"1-356d10b7a0f931b32c1b9820e3c23781"}
```
服务的名称必须是`ip:port`的形式，如果服务的端口是`2181,3306,8080,11211,22201或者61616`可以不用在body中指定name字段

name字段是服务的名称

### 更新服务
```
curl -X PUT http://localhost:8005/api/v1/cmdb/service/1.1.1.1:8080 -d '{"_rev":"1-356d10b7a0f931b32c1b9820e3c23781","name"="hello"}'
{"ok":true,"id":"1.1.1.2:8080","rev":"2-1bc1ba6164085b23887a7570d4b184ce"}
```
### 删除服务
删除整个服务
```
curl -X DELETE http://127.0.0.1:8005/api/v1/cmdb/service/1.1.1.1:8080
{"ok": true}
```

## project项目
### 查看项目
GET /api/v1/service/<project id>
### 添加项目
```
curl -X POST http://localhost:8005/api/v1/project/测试项目 -d 'field=hello'
```
项目id(项目名称)不可以重名

项目id支持中文，但是需要对uri转义
### 更新项目
```
curl -X POST http://localhost:8005/api/v1/project/测试项目 -d 'field=world'
```

项目中使用`services`字段来关联服务，字段值是服务id组成的数组

为项目添加服务
```
curl -X PUT http://localhost:8005/api/v1/project/测试项目 -d 'services=["1.1.1.1:8080","2.2.2.2:9090"]'
```

### 删除项目
```
curl -X DELETE http://localhost:8005/api/v1/project/测试项目
```