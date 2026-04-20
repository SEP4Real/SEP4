---
title: "Project Report – [Your Project Title]"
date: "[Month] [Day], [Year]"
author: "SEP4 Group 3"
course: "SEP4"
semester: "4th Semester"
institution: "VIA University College"
---

<!-- ============================================================
  PROJECT REPORT — VIA Engineering Guidelines 2024 + SEP4 Requirements
  
  STRUCTURE (mandated by SEP4 requirements document):
  
    Introduction
    Analysis                     ← one coherent unit (shared)
    Design Overview              ← shared, includes cloud architecture
      ├─ IoT Design              ┐
      ├─ ML Data Exploration     ├─ branches here
      └─ Frontend Design         ┘
      ├─ IoT Implementation      ┐
      ├─ ML Preprocessing        ├─ still branched
      └─ Frontend Implementation ┘
      ├─ IoT CI/CD               ┐
      ├─ ML Models               ├─ still branched
      └─ Frontend CI/CD          ┘
      ├─ IoT Test                ┐
      └─ Frontend Test           ┘
    Results and Discussion       ← merges back together
    Conclusions
    Future Work
  
  FORMALITIES:
  - Max 60 pages (1 page = 2400 characters)
  - Each section must list its AUTHORS
  - APA references throughout
  - Objective academic tone (no first-person — that goes in Process Report)
  - All claims supported by evidence and citations
  - Submit: report PDF, source code, repo links, 30-min video demo
  ============================================================ -->

# Abstract

<!-- Write LAST, even though it appears first. ~150–250 words.
     Cover: problem, approach (IoT + ML + Frontend + Cloud), key technical choices, results.
     No citations needed. -->

*Authors: [Name, Name, Name]*

[Concise summary of the entire project. State the problem being solved, the three-part
technical approach (embedded IoT on ATmega2560, machine learning pipeline, React web
frontend), the cloud infrastructure, and the main results. Should stand alone as a
paragraph that lets a reader decide whether to read further.]

# 1. Introduction

<!-- Sets the stage for the entire report. Must include the problem statement from
     your Project Description. Shared section — one coherent voice for the whole group.
     Consider environmental, social, economic, and technological significance. -->

*Authors: [Name, Name, Name]*

## 1.1 Background and Motivation

[Describe the domain context. What real-world problem does the system address?
Why is an IoT-based solution with machine learning relevant here?
Who are the stakeholders and what do they need?]

## 1.2 Problem Statement

<!-- Paste or adapt directly from your approved Project Description. -->

[State the specific problem the project addresses. Be precise about what is currently
missing or suboptimal, and what a successful solution would look like.]

## 1.3 Project Objectives

[Enumerate concrete, verifiable goals. These will be evaluated against in Results
and Discussion. Tie them to the three system components where relevant.

Example format:
- The IoT device shall measure [sensors] and transmit data to the cloud backend.
- The cloud backend shall store sensor data and expose a RESTful API.
- The ML component shall predict/classify [outcome] using sensor data.
- The frontend shall retrieve and display live and historical sensor data responsively.]

## 1.4 Scope and Delimitations

[Define the boundaries. What is explicitly in scope for each component?
What has been consciously left out, and why? Important given the 60-page limit.]

## 1.5 Related Work

[Survey existing IoT, ML, and web solutions relevant to your domain. Cite with APA.
How does your system differ from or build on existing approaches?]

# 2. Analysis

<!-- ONE COHERENT UNIT — shared across all three sub-teams.
     The entire group contributes to and agrees on this section.
     Must include: user stories, domain model, system-level requirements.
     Do NOT branch here — one list of user stories, one domain model, etc. -->

*Authors: [Name, Name, Name]*

## 2.1 Domain Model

[Describe the key concepts and relationships in the problem domain.
Reference the domain model diagram:]

<!-- ![Domain Model](../../Documentation/Analysis/domain_model.svg) -->

[Walk through the most important entities and associations.
Justify the key modelling decisions.]

## 2.2 User Stories

<!-- Present ALL user stories as a single shared backlog.
     Format: "As a [role], I want to [action], so that [benefit]." -->

| ID   | User Story                                                  | Priority   | Component      |
| :--- | :---------------------------------------------------------- | :--------- | :------------- |
| US01 | As a [user], I want to [action], so that [benefit].         | Must have  | IoT / Cloud    |
| US02 | As a [user], I want to [action], so that [benefit].         | Should     | Frontend       |
| US03 | As a [user], I want to [action], so that [benefit].         | Could      | ML             |

## 2.3 System Requirements

[Derive functional and non-functional requirements from the user stories.
Cross-cutting requirements (security, DevOps, performance) belong here.]

| ID    | Requirement Description                                      | Type            | Source |
| :---- | :----------------------------------------------------------- | :-------------- | :----- |
| FR01  | [Functional requirement]                                     | Functional      | US01   |
| NFR01 | IoT–cloud communication shall be encrypted.                  | Non-functional  | Security |
| NFR02 | The frontend shall be responsive at 576px, 768px, 1200px.   | Non-functional  | US02   |
| NFR03 | The system shall be deployed using containers.               | Non-functional  | DevOps |

## 2.4 System Sequence Diagrams

[Include SSDs for the key use cases that span the full system.
Show the messages exchanged between IoT device, cloud, ML pipeline, and frontend.]

<!-- ![SSD: [Use Case Name]](../../Documentation/Analysis/ssds/ssd_use_case.svg) -->

# 3. Design

## 3.1 Design Overview

<!-- SHARED section — written as one coherent unit BEFORE branching.
     Present the overall system architecture and cloud design here. -->

*Authors: [Name, Name, Name]*

### 3.1.1 System Architecture

[Describe the overall architecture: IoT device → Cloud backend → Frontend,
with the ML pipeline integrated into or alongside the cloud layer.
Reference the architecture diagram:]

<!-- ![System Architecture](../../Documentation/Design/architecture.svg) -->

[Justify the key architectural decisions: why this decomposition, how components
communicate (protocols, data formats), and how data flows end-to-end.]

### 3.1.2 Cloud Architecture

<!-- Required by SEP4: must use public cloud hosting, containers, and serverless. -->

[Describe the cloud infrastructure:
- **Hosting provider**: which provider and why (AWS, Azure, GCP, etc.)?
- **Containerisation**: how are services packaged and deployed (Docker, Compose, K8s)?
- **Serverless workloads**: which parts run as serverless functions, and why those parts?
- **Database**: what database system is used, and how is it hosted/managed?
- **RESTful API**: overall API design, endpoint structure, data formats (JSON).]

### 3.1.3 Security Design

<!-- SEP4 requires: encryption for IoT–cloud (symmetric or asymmetric),
     and JWT (or equivalent) protection for frontend-facing API endpoints. -->

[Describe the security architecture:
- **IoT–cloud encryption**: which scheme was chosen (TLS, AES, RSA) and why?
- **API authentication**: how are endpoints protected (JWT, API keys)?
- **Key and certificate management**: how are secrets handled in the project?
- Any additional security considerations for your specific domain.]

### 3.1.4 DevOps Strategy

<!-- All projects must: unit test, use distributed Git with branches/tags,
     set up automated regression testing via GitHub/GitLab CI, and use containers.
     Pair-programming commits must list both names in the commit message. -->

[Describe the overall DevOps plan:
- **Git workflow**: branching model (e.g. Gitflow, trunk-based), tagging conventions,
  commit message standard, pair-programming naming convention.
- **CI/CD overview**: what events trigger pipelines, what gates exist before merging.
- **Container strategy**: what is containerised, which base images are used.
- **Testing overview**: how unit and regression testing is organised across all components.

Reference the repository: [GitHub/GitLab URL]]

## 3.2 IoT Design

*Authors: [Name, Name]*

<!-- Design of the embedded C application on ATmega2560 + WiFi. -->

### 3.2.1 Hardware Architecture

[Describe the physical setup: ATmega2560 MCU, WiFi module, and all connected sensors
and actuators. Explain interface decisions (I2C, SPI, UART, ADC, GPIO, PWM).
Reference a hardware block diagram:]

<!-- ![Hardware Block Diagram](../../Documentation/Design/IoT/hardware_block.svg) -->

| Component             | Interface  | Purpose                         |
| :-------------------- | :--------- | :------------------------------ |
| Air temperature sensor| [I2C/ADC]  | [What is measured]              |
| Air humidity sensor   | [I2C/ADC]  | [What is measured]              |
| Soil humidity sensor  | [ADC]      | [What is measured]              |
| Light sensor          | [ADC]      | [What is measured]              |
| Proximity sensor      | [...]      | [What is detected]              |
| PIR sensor            | [GPIO]     | [What is detected]              |
| Servo motor           | [PWM]      | [What it controls]              |
| Water pump            | [GPIO]     | [What it controls]              |
| 7-segment display     | [...]      | [What it displays]              |
| LEDs                  | [GPIO]     | [Indicator purpose]             |

### 3.2.2 Embedded Software Architecture

[Describe the software architecture of the C application:
- Module/task decomposition
- Communication protocol chosen for cloud uplink (MQTT, HTTP) and justification
- Data serialisation format for sensor payloads
- Scheduling approach (superloop, cooperative, interrupt-driven)]

<!-- ![Embedded Software Architecture](../../Documentation/Design/IoT/sw_architecture.svg) -->

## 3.3 Machine Learning — Data Exploration

*Authors: [Name, Name]*

<!-- Design phase for ML: understanding the data before modelling. -->

### 3.3.1 Data Sources and Collection Strategy

[What data is used? Where does it come from (live IoT feed, public dataset, synthetic)?
What sensor readings are features? What is the prediction/classification target?
How much data is available, and over what time period?]

### 3.3.2 Exploratory Data Analysis

[Describe findings from exploring the raw data:
- Data shape and volume
- Feature distributions (reference plots)
- Missing values and outliers identified
- Correlations between features and target variable]

<!-- ![Feature Distributions](../../Documentation/Design/ML/eda_distributions.png) -->

### 3.3.3 ML Problem Formulation

[Precisely define the ML task:
- Classification, regression, or clustering — and why?
- What is the target variable?
- What input features are selected as relevant?
- What does a useful/successful prediction look like in this context?]

## 3.4 Frontend Design

*Authors: [Name, Name]*

<!-- Design of the React web application. -->

### 3.4.1 UI/UX Design

[Describe the user interface design:
- Target users and their primary tasks
- Navigation structure and information architecture
- Key screens/views and their purpose]

<!-- Include wireframes or mockups:
![Wireframe: Dashboard](../../Documentation/Design/Frontend/wireframe_dashboard.png) -->

### 3.4.2 Component Architecture

[Describe the React component hierarchy. How is the application decomposed?
What state management approach is used (useState, Context API, Redux, Zustand)?
How does the app communicate with the backend API (fetch, axios, React Query)?]

<!-- ![Component Diagram](../../Documentation/Design/Frontend/component_diagram.svg) -->

### 3.4.3 Responsiveness Strategy

<!-- Required: must adapt well to 576px, 768px, and 1200px screen widths. -->

[Describe the responsive design approach:
- CSS framework or approach (Tailwind, Bootstrap, CSS Grid/Flexbox)
- Breakpoints used and how layouts reflow at each
- Specifically address the three mandatory widths: 576px, 768px, 1200px]

## 3.5 IoT Implementation

*Authors: [Name, Name]*

### 3.5.1 Sensor and Actuator Drivers

[Describe the C driver implementations for each sensor and actuator.
What libraries or register-level access was used?
Highlight non-trivial decisions (interrupt-driven vs polling, calibration logic).]

```c
/* Include a representative driver or communication function.
   Annotate the non-obvious parts. */
```

### 3.5.2 Cloud Communication Implementation

[How is the WiFi/network communication implemented in C?
Describe the connection setup, data serialisation, and transmission logic.
How are network failures, timeouts, and retries handled?]

### 3.5.3 Main Application Logic

[Describe the main loop and how sensor sampling, actuator control, display updates,
and network transmission are orchestrated. How are timing requirements met?]

## 3.6 Machine Learning — Preprocessing and Pipeline

*Authors: [Name, Name]*

### 3.6.1 Data Cleaning

[Describe all preprocessing steps applied to raw sensor data:
- Handling missing values (imputation strategy or row removal)
- Outlier detection method and treatment
- Feature engineering (derived features, rolling averages, time-based features)
- Normalisation or standardisation applied, and why]

### 3.6.2 Feature Selection

[Which features were selected for the model and on what basis?
Were feature selection techniques applied (correlation threshold, importance ranking)?
What was excluded and why?]

### 3.6.3 Data Split and Validation Strategy

[How was data split into train/validation/test sets?
What cross-validation approach is used?
How was data leakage prevented (especially important for time-series sensor data)?]

## 3.7 Frontend Implementation

*Authors: [Name, Name]*

### 3.7.1 Core Features Implementation

[Describe how the key features were built:
- Fetching, parsing, and displaying live sensor data from the REST API
- Historical data visualisation (charts/graphs — which library: Recharts, Chart.js, D3?)
- User interactions and controls for managing the system
- Any state management patterns worth highlighting]

```jsx
/* Include a representative React component illustrating a key implementation
   decision — e.g. a data-fetching hook, a chart component, or an API call. */
```

### 3.7.2 API Integration

[How does the frontend communicate with the backend?
Describe error handling, loading states, polling vs websocket decisions,
and how ML predictions are retrieved and displayed.]

### 3.7.3 Hosting and Deployment

<!-- Required: must be hosted and accessible online. -->

[Describe how the React app is built and hosted. Where is it deployed?
How is the deployment triggered (manual push, CI/CD pipeline)?
Provide the live URL if applicable.]

## 3.8 IoT CI/CD

*Authors: [Name, Name]*

<!-- DevOps checklist — address all four points:
     1. General DevOps considerations and planning
     2. Which tools were used and why (or why not)
     3. How DevOps was integrated into the general workflow
     4. What effect did DevOps tools/methods have; what worked well / less well -->

### 3.8.1 DevOps Considerations for Embedded Development

[What challenges are unique to CI/CD for embedded C on ATmega2560?
(No easy emulation, hardware-dependent peripherals, cross-compilation toolchain.)
How did you plan around these constraints from the start?]

### 3.8.2 Tools and Pipeline

[Describe the CI pipeline for the IoT codebase:
- CI platform used (GitHub Actions, GitLab CI) and configuration
- Pipeline stages: what happens on each commit/PR? (build, lint, unit tests)
- Unit test framework for embedded C (Unity, CMock, custom harness)
- How hardware-dependent code is mocked or stubbed for automated testing
- Container setup for the cross-compilation build environment]

### 3.8.3 Integration into Workflow

[How was the CI pipeline used day-to-day?
Were PRs blocked on failing tests? Who was responsible for fixing broken builds?]

### 3.8.4 Outcomes and Evaluation

[To what extent was DevOps successfully integrated into IoT development?
What worked well? What was difficult or impractical to automate, and why?]

## 3.9 Machine Learning — Models

*Authors: [Name, Name]*

### 3.9.1 Model Selection

[Which ML model(s) were evaluated? Justify the choice for your task type
(classification / regression / clustering). What alternatives were considered?]

### 3.9.2 Training and Hyperparameter Tuning

[Describe the training procedure. How were hyperparameters tuned
(grid search, random search, manual)? What evaluation metric was optimised?]

### 3.9.3 Model Evaluation

[Present performance results on the held-out test set.
Use tables and visualisations (confusion matrix, learning curves, residual plots):]

<!-- ![Confusion Matrix](../../Documentation/Design/ML/confusion_matrix.png) -->

| Model              | Metric 1  | Metric 2  | Metric 3  |
| :----------------- | :-------- | :-------- | :-------- |
| Baseline           |           |           |           |
| [Chosen model]     |           |           |           |

### 3.9.4 Result Export

[How are model predictions or insights exported for the rest of the system?
What format, API endpoint, or file output does the ML component produce?
How does the frontend consume this output?]

## 3.10 Frontend CI/CD

*Authors: [Name, Name]*

<!-- DevOps checklist — same four points as IoT CI/CD (Section 3.8). -->

### 3.10.1 DevOps Considerations for the Frontend

[What DevOps planning was done specifically for the React codebase?
How were code ownership and review responsibilities organised?]

### 3.10.2 Tools and Pipeline

[Describe the CI/CD pipeline for the frontend:
- Linting and formatting (ESLint, Prettier)
- Unit and component tests (Jest, React Testing Library)
- E2E tests if applicable (Cypress, Playwright)
- Automated build and deployment to hosting
- Container usage for frontend (if applicable)]

### 3.10.3 Integration into Workflow

[How was the pipeline used day-to-day? Branch protection rules, required checks?]

### 3.10.4 Outcomes and Evaluation

[What effect did DevOps have on frontend quality and development speed?
What automated checks ran on every PR? What gaps remained?]

## 3.11 IoT Tests

*Authors: [Name, Name]*

### 3.11.1 Testing Strategy for Embedded C

[What aspects of the IoT application were unit-tested?
What test framework was used? How were hardware-dependent parts handled
(mock drivers, stub peripherals, hardware-in-the-loop)?]

### 3.11.2 Unit Test Results

| Module               | Tests | Passed | Failed | Coverage |
| :------------------- | :---- | :----- | :----- | :------- |
| [Sensor driver X]    |       |        |        |          |
| [Communication]      |       |        |        |          |

### 3.11.3 Integration and System-Level Tests

[Describe any integration testing performed with actual hardware.
How was end-to-end behaviour (sensor reading → cloud transmission) verified?
What manual or automated system tests were run?]

## 3.12 Frontend Tests

*Authors: [Name, Name]*

### 3.12.1 Testing Strategy

[What test types were applied? Unit tests (component rendering), integration tests
(API mocking), or E2E tests (full browser automation)?]

### 3.12.2 Test Results

| Test Suite           | Tests | Passed | Failed | Coverage |
| :------------------- | :---- | :----- | :----- | :------- |
| Component tests      |       |        |        |          |
| Integration tests    |       |        |        |          |

### 3.12.3 Responsiveness Testing

[How was responsive behaviour verified at the three required breakpoints
(576px, 768px, 1200px)? Include screenshots if helpful.]

# 4. Results and Discussion

<!-- MERGES BACK — one coherent section covering the complete integrated system.
     Objective tone only. No personal opinions — those go in the Process Report.
     Cover: full-system integration, objectives met, critical evaluation, limitations. -->

*Authors: [Name, Name, Name]*

## 4.1 Integrated System Results

[How does the complete system perform end-to-end?
Demonstrate all three parts working together (reference the submitted demo video).
What does actual sensor data look like flowing through to the frontend predictions?]

## 4.2 Evaluation Against Objectives

[Revisit each objective from Section 1.3. For each, state whether it was met,
partially met, or not met, and support the assessment with evidence.]

| Objective     | Status                   | Evidence                  |
| :------------ | :----------------------- | :------------------------ |
| [Objective 1] | ✔ Met / ⟳ Partial / ✗ Not | [Test results / screenshot] |

## 4.3 IoT Performance

[How reliably does the embedded system read sensors and transmit data?
Any latency, sampling drift, memory issues, or failure modes observed?]

## 4.4 ML Performance

[Summarise the final model performance in context. Are predictions accurate enough
to be useful for the application? How does the model compare to a naive baseline?]

## 4.5 Frontend Quality

[Does the application meet the functional requirements? Does it display data correctly
across all required breakpoints? Are all customer-facing features accessible via the UI?]

## 4.6 Cloud and DevOps Evaluation

[How does the cloud infrastructure perform under normal use?
Are containerised services and serverless workloads functioning as designed?
How successfully was DevOps integrated — what was the actual effect on the project?]

## 4.7 Critical Evaluation and Limitations

[Honestly evaluate validity and reliability of your results.
What are the system's remaining weaknesses? What assumptions constrain the findings?
What would need to change for this to be a production-grade system?
Address limitations per component where the issues differ significantly.]

# 5. Conclusions

*Authors: [Name, Name, Name]*

[Summarise the project in 3–5 paragraphs:
1. Restate the problem and the three-part approach taken
2. What was achieved — per component and as an integrated system
3. Did the system solve the stated problem, and to what degree?
4. What is the overall answer to the problem statement?]

# 6. Future Work

*Authors: [Name, Name, Name]*

[Describe the most important directions for continuing or improving the system.
Be specific and actionable.

- **IoT**: additional sensors, power optimisation, OTA firmware updates, PCB design...
- **ML**: more training data, online/incremental learning, alternative models, explainability...
- **Frontend**: mobile app, push notifications, user authentication, dashboard customisation...
- **Cloud/DevOps**: full CD with staged environments, infrastructure-as-code (Terraform),
  monitoring and alerting (Grafana, Prometheus), load testing...]

# References

<!-- APA 7th edition. Every in-text citation must appear here, and vice versa.
     Typical sources: ATmega datasheets, RFC/standards, ML papers,
     React/framework documentation, cloud provider docs, DevOps tool docs.

     APA examples:
     Author, A. A. (Year). Title of article. Journal, vol(issue), pp. https://doi.org/...
     Organisation. (Year). Title of documentation. Retrieved from https://... -->

::: {#refs}
:::

# Appendices

<!-- Typically not counted toward the 60-page limit — verify with supervisor. -->

## Appendix A — Source Code

| Component  | Repository URL          |
| :--------- | :---------------------- |
| IoT        | [GitHub/GitLab URL]     |
| Cloud      | [GitHub/GitLab URL]     |
| ML         | [GitHub/GitLab URL]     |
| Frontend   | [GitHub/GitLab URL]     |

## Appendix B — API Documentation

[Link to hosted API docs (Swagger/OpenAPI), or include the endpoint specification here.]

## Appendix C — Hardware Schematics

<!-- Full wiring diagrams if too large for Section 3.2. -->

## Appendix D — Additional ML Figures

<!-- EDA plots, learning curves, feature importance charts that support Section 3.9. -->