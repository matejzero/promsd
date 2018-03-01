# Prometheus service discovery

Simple prometheus service discovery written in Python. It has a simple RESTful API for manipulating targets, jobs and labels. It uses SQlite DB for saving data and exports them to YAML file, which can be ingested by Prometheus File SD.

## API

### GET /api/v1/targets/
**Description**: List all targets

**URL parameters**: none

**Response codes**:

| Code |     Description      |
|------|----------------------|
|  200 | Successful operation |

**Example**:
```
$ curl http://localhost:5000/api/v1/targets/
[
  {
    "id": 1,
    "job": "node",
    "labels": {
      "env": "prod",
      "severity": "critical"
    },
    "target": "target1.example.org"
  },
  {
    "id": 2,
    "job": "mysql",
    "labels": {},
    "target": "target2.example.org"
  }
]
```

### GET /api/v1/targets/{targetID}/
**Description**: Find target by ID

**URL parameters**: 

| Name     | Type     | Required | Description          |
| -------- | -------- | -------- | -------------------- |
| targetId | integer  | yes      | Target ID number     |

**Response codes**:

| Code |     Description      |
|------|----------------------|
|  200 | Successful operation |
|  404 | Target not found     |

**Example**:
```
$ curl http://localhost:5000/api/v1/targets/1/
{
  "id": 1,
  "job": "node",
  "labels": {
    "env": "prod",
    "severity": "critical"
  },
  "target": "target1.example.org"
}
```

### POST /api/v1/targets/
**Description**: Add new target

**URL parameters**:

**Body parameters**:

|  Name  |  Type  | Required |         Description          |
|--------|--------|----------|------------------------------|
| target | string | yes      | Target's FQDN address        |
| job    | string | yes      | Job name for the target      |
| labels | hash   | no       | Additional labels for target |

**Response codes**:

| Code |                  Description                   |
|------|------------------------------------------------|
|  201 | Target added                                   |
|  400 | Document not a valid JSON                      |
|  409 | Target already exists                          |
|  422 | JSON document not valid (missing/wrong fields) |

**Example**:
```
curl -i -H "Content-Type: application/json" -X POST http://localhost:5000/api/v1/targets -d '{
  "target": "target3.example.org",
  "job": "node",
  "labels": {
    "env": "prod",
    "severity": "critical"
  }
}'

{
  "id": 3,
  "job": "node",
  "labels": {
    "env": "prod",
    "severity": "critical"
  },
  "target": "target3.example.org"
}
```


### PUT /api/v1/targets/{targetId}/
**Description**: Create or update target with ID.

**URL parameters**:

| Name     | Type     | Required | Description          |
| -------- | -------- | -------- | -------------------- |
| targetId | integer  | yes      | Target ID number     |

**Body parameters**:

|  Name  |  Type  | Required |         Description          |
|--------|--------|----------|------------------------------|
| target | string | yes      | Target's FQDN address        |
| job    | string | yes      | Job name for the target      |
| labels | hash   | no       | Additional labels for target |

**Response codes**:

| Code |                  Description                   |
|------|------------------------------------------------|
|  200 | Target updated                                 |
|  201 | Target added                                   |
|  400 | Document not a valid JSON                      |
|  409 | Target already exists                          |
|  422 | JSON document not valid (missing/wrong fields) |

**Example**:
```
curl -H "Content-Type: application/json" -X PUT http://localhost:5000/api/v1/targets/10/ -d '{
  "target": "target10.example.org",
  "job": "node",
  "labels": {
    "env": "prod"
  }
}'

{
  "id": 10,
  "job": "node",
  "labels": {
    "env": "prod"
  },
  "target": "target10.exampl.eorg"
}
```

### DELETE /api/v1/targets/{targetId}/
**Description**: Delete a target

**URL parameters**:

| Name     | Type     | Required | Description          |
| -------- | -------- | -------- | -------------------- |
| targetId | integer  | yes      | Target ID number     |

**Body parameters**:

**Response codes**:

| Code |                  Description                   |
|------|------------------------------------------------|
|  204 | Target deleted                                 |
|  404 | Target with this ID doesnt exists                                   |

**Example**:
```
$ curl -H "Content-Type: application/json" -X DELETE http://localhost:5000/api/v1/targets/1/
```
