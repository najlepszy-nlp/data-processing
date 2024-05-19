# Data Processing Module

### Running API localy with docker

```bash
# Start
docker compose up -d

# Stop
docker compose down
```

### Endpoints

Swagger docs available at `http://localhost:8080/docs`.

- `GET http://localhost:8080/`

   Returns `{"status": "up"}` if API's healthy.

- `GET http://localhost:8080/data?skip=<skip>&limit=<limit>`

   Returns processed data with pagination in json format.

- `POST http://localhost:8080/processing`
   
   Perfoms the reprocessing of input data.
