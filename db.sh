#!/bin/sh
curl -X PUT http://127.0.0.1:5984/cmdb

curl -X PUT http://localhost:5984/cmdb/_design/service -d @service.json
curl -X PUT http://localhost:5984/cmdb/_design/project -d @project.json
