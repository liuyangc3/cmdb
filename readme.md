/usr/local/Cellar/couchdb/1.6.1_3/bin/couchdb

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