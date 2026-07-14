# Project Structure

Organize your services in a project.

## Create a Project

```bash
evo init my-api
cd my-api
```

## Project Structure

```
my-api/
├── evoid.toml              # Project config
├── services/
│   ├── api/
│   │   ├── evoid.toml      # Service config
│   │   └── main.py         # Service code
│   └── worker/
│       ├── evoid.toml
│       └── main.py
└── shared/
    └── __init__.py         # Shared models
```

## Add a Service

```bash
evo service new worker
```

## List Services

```bash
evo service list
```

Output:
```
Services:
  api                  port=8000   adapter=asgi
  worker               port=8001   adapter=asgi
```

## Run a Service

```bash
evo service run api
```

## Run All Services

```bash
evo run
```

## Why Project Structure? 🤔

- ✅ **Organization** — One folder per service
- ✅ **Isolation** — Each service has its own config
- ✅ **Scalability** — Add services without touching others
- ✅ **Teamwork** — Multiple devs can work on different services

**Project = Collection of services.** 🏗️
