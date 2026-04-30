---
title: "StudyHelper Architecture"
date: "April 29, 2026"
author: "SEP4 Group 3"
course: "SEP4"
semester: "4th Semester"
institution: "VIA University College"
---
# StudyHelper Architecture

StudyHelper is a distributed study-environment monitoring system. A physical IoT device measures room conditions, a backend stores measurements and sessions, an ML service predicts study suitability, and a React frontend visualizes current and historical conditions.

This document describes the implemented architecture in the repository, not only the intended design.

## System Context

```mermaid
flowchart LR
    Student[Student] --> Frontend[React frontend]
    Teacher[Teacher] --> Frontend
    IoT[IoT device<br/>Arduino/PlatformIO] --> IotApi[IoT backend<br/>ASP.NET Core]
    Frontend --> IotApi
    Frontend --> MalApi[MAL API<br/>FastAPI]
    MalApi --> Database[(PostgreSQL)]
    IotApi --> Database
```

## Container Architecture

The deployed system is described by `docker-compose.yml` and currently consists of four containers:

```mermaid
flowchart TB
    subgraph Coolify["Coolify deployment"]
        Frontend["frontend<br/>React + Vite, served on port 80"]
        IotApi["iot-api<br/>ASP.NET Core, exposes 8080 internally"]
        MalApi["mal-api<br/>FastAPI, exposes 8000 internally"]
        Postgres["postgres<br/>PostgreSQL 16"]
        Volume[(postgres_data volume)]
    end

    Frontend --> IotApi
    Frontend --> MalApi
    IotApi --> Postgres
    MalApi --> Postgres
    Postgres --> Volume
```

### Services

| Service      | Technology                                   | Responsibility                                                                | Source                   |
| ------------ | -------------------------------------------- | ----------------------------------------------------------------------------- | ------------------------ |
| `frontend` | React, Vite, Nginx/containerized static site | Dashboard, history, login/register UI                                         | `Frontend/`            |
| `iot-api`  | ASP.NET Core, Entity Framework Core, Npgsql  | Device registration, study sessions, sensor data persistence, database health | `IOT_backend/`         |
| `mal-api`  | FastAPI, scikit-learn, psycopg               | Model prediction, model metadata, database data collection for training       | `MAL/`                 |
| `postgres` | PostgreSQL 16 Alpine                         | Shared persistence for devices, sessions, and sensor data                     | `initdb/01_schema.sql` |
| IoT firmware | PlatformIO C                                 | Reads sensors, registers device/session, posts measurements, sends pulses     | `IOT/`                 |

## Runtime Data Flow

```mermaid
sequenceDiagram
    participant Device as IoT device
    participant Api as IoT API
    participant Db as PostgreSQL
    participant Ml as MAL API
    participant Ui as Frontend

    Device->>Api: POST /Device
    Api->>Db: Insert device if new
    Device->>Api: POST /Session
    Api->>Db: Create active session
    loop During study session
        Device->>Api: PATCH /Session/{id}/pulse
        Api->>Db: Update last_pulse_at
        Device->>Api: POST /Data
        Api->>Db: Store temperature, humidity, CO2, light
    end
    Ui->>Api: GET /Data
    Api->>Db: Read measurements
    Ui->>Ml: POST /predict
    Ml-->>Ui: Predicted rating
```

## Database Model

The current persistent model contains three tables:

```mermaid
erDiagram
    devices ||--o{ sessions : owns
    sessions ||--o{ data : contains

    devices {
        varchar public_key PK
    }

    sessions {
        bigint id PK
        varchar device_id FK
        timestamptz started_at
        timestamptz ended_at
        timestamptz last_pulse_at
        int study_quality
    }

    data {
        bigint id PK
        bigint session_id FK
        float temperature
        float humidity
        float co2_level
        float light_level
        timestamptz sent_at
    }
```

The schema is initialized both by `initdb/01_schema.sql` and by the ASP.NET Core startup initializer in `IOT_backend/DbConfig/DatabaseInitializer.cs`. This makes the database resilient during development and deployment, but the duplication should eventually be replaced by one migration strategy.

## Deployment View

The current deployment runs on Coolify. GitHub Actions triggers Coolify on pushes to `main` through `.github/workflows/deploy-coolify.yaml`.

```mermaid
flowchart LR
    Dev[Developer branch] --> PR[Pull request]
    PR --> Main[main]
    Main --> Actions[GitHub Actions]
    Actions --> Registry[GHCR images<br/>MAL/frontend where configured]
    Actions --> Coolify[Coolify webhook]
    Coolify --> Server[Production containers]
```
