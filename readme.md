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


# ����api
/api/v1/service/<service id>
## �鿴����
GET
## ��ӷ���
```
curl -X POST http://localhost:8005/api/v1/service/1.1.1.1:8080 -d 'name=hello'
```
# ���·���
```
curl -X PUT http://localhost:8005/api/v1/service/1.1.1.1:8080 -d 'name=world'
```
# ɾ������
ɾ����������
```
curl -X DELETE http://127.0.0.1:8005/api/v1/service/1.1.1.1:8080
```

ɾ���ֶ�
```
curl -X DELETE http://127.0.0.1:8005/api/v1/service/1.1.1.1:8080field=f1
```

ɾ��ĳ�����ֶ�
```
curl -X DELETE 'http://127.0.0.1:8005/api/v1/service/1.1.1.1:8080?field=f1&field=f2
```

# ��Ŀapi
/api/v1/project/<project id>

## �鿴

## �����Ŀ
```
curl -X POST http://localhost:8005/api/v1/project/������Ŀ -d 'name=hello'
```

## Ϊ��Ŀ��ӷ���

## ����

