/usr/local/Cellar/couchdb/1.6.1_3/bin/couchdb

# init databases
```
./db.sh
```
test
```
curl http://localhost:5984/cmdb/_design/service/_view/list
curl http://localhost:5984/cmdb/_design/service/_list/get_service/list?name=tomcat
curl http://localhost:5984/cmdb/_design/project/_view/list?group=true
```

# 加载前端项目
```
git clone https://gitcafe.com/hudson/cmdb-front.git
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

