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

* How should we split the responsibilities between the teams? - We take care of IOT and parts of the backend that interact with IOT directly
* What data is sent between the various parts of the system?
  * IOT sends session key, light, humidity and temperature to backend.
  * IOT will also request session key from backend at the beginning of the session.
  * We should maybe add an endpoint for ending the session that sends the session key as well if we want to show session status on the frontend.
  * Maybe backend sends back some info about turning on a fan or a sound after it gets fresh information as well.
* What is the format of the data? How is it sent? - JSON data converted to standard units(i.e. °C) over REST API.
* How frequently is the data updated? - Fresh room parameters are sent every 1 minute.
* Do you need to mock parts of the system early on or will real data be available? - If we want to have a fan or a sound that’s triggered by backend, we will have to mock it until backend works.

\newpage
# MAL Interfacing contract

* How should we split the responsibilities between the teams? - We handle the backend, the database, and the ML model. We provide the API that connects the IOT hardware to the frontend.
* What data is send between the various parts of the system? - We receive temperature, humidity, and light from IOT. We send session keys to IOT and the frontend. We send ML insights and historical data to the frontend. We also send "action" commands (like turning on a fan or sound) back to IOT based on the sensor data we receive.
* What is the format of the data? How is it sent? - JSON data converted to standard units(i.e. °C) over REST API
* How frequently is the data updated? - Every 1 minute to match the IOT transmission.
* Do you need to mock parts of the system early on or will real data be available? - We need to mock the IOT sensor data immediately so we can train our ML model and test the API. This will also allow the frontend team to see data on their side before the IOT hardware is fully connected.

\newpage
# FrontEnd Interfacing contract

* How should we split the responsibilities between the teams? - FrontEnd is responsible for data visualization and user input collection - we will use  JavaScript + React
* What data is send between the various parts of the system? - We receive ML predictions/suggestions, current sensor values (CO₂, temperature, humidity, noise, light) and historical data from ML/IoT and showing current values, history, and predictions in the web app. We send data to backend : user commands- change LED color and user interactions (select room, preferences)
* What is the format of the data? How is it sent? - JSON data converted to standard units(i.e. °C) over REST API; standard http methods (GET requests)
* How frequently is the data updated? - Every 1 minute, dynamically updated UI based on IOT transmission:
  1. new data is received
  2. state updates
  3. React re-renders the relevant components
* Do you need to mock parts of the system early on or will real data be available? - yes, frontend will do mock API to build the UI component while the hardware and ML models are still in development stage. the mock will be based on the agreed JSON structure..
