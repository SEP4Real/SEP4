---
title: "Interfacing Contract"
date: "April 7, 2026"
author: "SEP4 Group 3"
course: "SEP4"
semester: "4th Semester"
institution: "VIA University College"
toc: false
---
# IOT Interfacing contract

### How should we split the responsibilities between the teams?
We take care of IOT and parts of the backend that interact with IOT directly.

### What data is sent between the various parts of the system?
* IOT sends session key, light, humidity and temperature to backend.
* IOT will also request session key from backend at the beginning of the session.
* We should maybe add an endpoint for ending the session that sends the session key as well if we want to show session status on the frontend.
* Maybe backend sends back some info about turning on a fan or a sound after it gets fresh information as well.

### What is the format of the data? How is it sent?
JSON data converted to standard units (i.e. °C) over REST API.

### How frequently is the data updated?
Fresh room parameters are sent every **1 minute**.

### Do you need to mock parts of the system early on or will real data be available?
If we want to have a fan or a sound that’s triggered by backend, we will have to mock it until backend works.

\newpage
# MAL Interfacing contract

### How should we split the responsibilities between the teams?
We handle the ML model and parts of backend related to retrieving data from the DB, giving predictions (giving access to the model via an API).

### What data is send between the various parts of the system?
We receive temperature, humidity, and light from IOT (subject to change based on what is available). We send back predictions/suggestions to the frontend (e.g. “turn on the fan”, “open the window”), and IoT (e.g. “turn on the fan”).

### What is the format of the data? How is it sent?
JSON data converted to standard units (i.e. °C) over REST API.

### How frequently is the data updated?
Every **1 minute** to match the IOT transmission.

### Do you need to mock parts of the system early on or will real data be available?
We need to mock the IOT sensor data immediately so we can train our ML model and test the API. This will also allow the frontend team to see data on their side before the IOT hardware is fully connected. We will also have to fill in gaps in case we want to use early data when not all sensors are available yet (e.g. if we only have temperature and humidity, we can fill in light based on MAL theory).

\newpage
# FrontEnd Interfacing contract

### How should we split the responsibilities between the teams?
FrontEnd is responsible for data visualization and user input collection — we will use **JavaScript + React**. FronEnd will also be responsible for baackend in case something is needed outside the mentioned scope of IOT and MAL teams (e.g. user authentication, user preferences, etc.). 

### What data is send between the various parts of the system?
We receive ML predictions/suggestions, current sensor values (CO₂, temperature, humidity, noise, light) and historical data from ML/IoT and showing current values, history, and predictions in the web app. We send data to backend: user commands (change LED color) and user interactions (select room, preferences).

### What is the format of the data? How is it sent?
JSON data converted to standard units (i.e. °C) over REST API; standard HTTP methods (GET requests).

### How frequently is the data updated?
Every **1 minute**, dynamically updated UI based on IOT transmission:
1. New data is received.
2. State updates.
3. React re-renders the relevant components.

### Do you need to mock parts of the system early on or will real data be available?
Yes, frontend will do mock API to build the UI component while the hardware and ML models are still in development stage. The mock will be based on the agreed JSON structure.
