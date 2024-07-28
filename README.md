# Media Player

A simple media player using flask and Gstreamer with WebRTCsink

## Environment Variables

Before running the project, you need to set up some environment variables. These variables are essential for configuring the database and application settings. You can define these variables in a `.env` file located at the root of your project directory.

Here is an example of what the `.env` file should look like:

```
POSTGRES_USER=username
POSTGRES_PASSWORD=password
POSTGRES_DB=db
COMPOSE_FILE=docker-compose.yml:compose.dev.yml
FLASK_PORT=5000
```

### Explanation of Environment Variables

- `POSTGRES_USER`: This sets the username for your PostgreSQL database. For development, you can use `testusr`.
- `POSTGRES_PASSWORD`: This sets the password for your PostgreSQL database user. For development, you can use `password`.
- `POSTGRES_DB`: This specifies the name of your PostgreSQL database. For development, you can use `testdb`.
- `COMPOSE_FILE`: This defines the Docker Compose files to be used. In this case, `docker-compose.yml:compose.dev.yml` is specified for development configuration. For production, we will use only `docker-compose.yml` and for testing we will use `docker-compose.yml:compose.test.yml`
- `FLASK_PORT`: This sets the port on which your Flask application will run. The default is `5000`.

### Steps to Set Up the Environment Variables

1. Create a file named `.env` in the root of your project directory.
2. Copy and paste the example environment variables into the `.env` file.
3. Save the file.

Once you have set up the `.env` file, you can proceed with running the project using Docker Compose or your preferred method.