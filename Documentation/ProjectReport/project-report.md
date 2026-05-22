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

| ID   | User Story                                          | Priority  | Component   |
| :--- | :-------------------------------------------------- | :-------- | :---------- |
| US01 | As a [user], I want to [action], so that [benefit]. | Must have | IoT / Cloud |
| US02 | As a [user], I want to [action], so that [benefit]. | Should    | Frontend    |
| US03 | As a [user], I want to [action], so that [benefit]. | Could     | ML          |

## 2.3 System Requirements

[Derive functional and non-functional requirements from the user stories.
Cross-cutting requirements (security, DevOps, performance) belong here.]

| ID    | Requirement Description                                   | Type           | Source   |
| :---- | :-------------------------------------------------------- | :------------- | :------- |
| FR01  | [Functional requirement]                                  | Functional     | US01     |
| NFR01 | IoT–cloud communication shall be encrypted.              | Non-functional | Security |
| NFR02 | The frontend shall be responsive at 576px, 768px, 1200px. | Non-functional | US02     |
| NFR03 | The system shall be deployed using containers.            | Non-functional | DevOps   |

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

| Component              | Interface | Purpose             |
| :--------------------- | :-------- | :------------------ |
| Air temperature sensor | [I2C/ADC] | [What is measured]  |
| Air humidity sensor    | [I2C/ADC] | [What is measured]  |
| Soil humidity sensor   | [ADC]     | [What is measured]  |
| Light sensor           | [ADC]     | [What is measured]  |
| Proximity sensor       | [...]     | [What is detected]  |
| PIR sensor             | [GPIO]    | [What is detected]  |
| Servo motor            | [PWM]     | [What it controls]  |
| Water pump             | [GPIO]    | [What it controls]  |
| 7-segment display      | [...]     | [What it displays]  |
| LEDs                   | [GPIO]    | [Indicator purpose] |

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

The initial search for data focused on the relationship between environmental noise and cognitive focus. We explored combining datasets describing focus-related effects of background noise with labeled sound categories from WAV files, extracting frequencies and loudness. However, as the project evolved, we narrowed the ML objective from direct focus prediction to predicting a user-provided **Study Suitability Rating**. This shift was necessary because "focus" is a subjective internal state that cannot be directly measured by our sensors. By using a user-provided rating, we anchored our target variable in observable environmental conditions and explicit user feedback. [...]

### 3.3.2 Exploratory Data Analysis

During the exploratory phase, several candidate datasets were evaluated. We identified and eliminated datasets that appeared synthetic or "too perfect" to be realistic sensor data. For example, in datasets labeled as "Data 2" and "Data 4," the distributions of humidity, noise, and light were suspiciously uniform or perfectly bell-shaped, lacking the stochastic noise typical of real-world environments.

![Feature Distributions of Suspicious Datasets](../ProcessReport/image/process-report/1778581492077.png)

*Figure 3.x: Suspiciously perfect feature distributions in candidate datasets.*

Correlation analysis further revealed insights into data quality. Healthy datasets exhibited natural correlations between temperature, CO2, and humidity. Conversely, some "suspicious" datasets showed near-zero correlation across all features, suggesting high randomness or artificial generation.

![Healthy vs Suspicious Correlation Matrices](../ProcessReport/image/process-report/1778581896856.png)

*Figure 3.y: Correlation matrices showing healthy physical relationships (left) vs suspicious randomness (right).*

### 3.3.3 ML Problem Formulation

The ML task is formulated as a supervised learning problem aimed at predicting the Study Suitability Rating. [...]

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

### 3.6.1 Data Cleaning and Imputation

A significant challenge was merging disparate datasets, which often resulted in missing columns for specific sensors (e.g., noise or light). To handle these missing values while preserving natural variance, we implemented a sophisticated imputation strategy using the **Multivariate Imputation by Chained Equations (MICE)** framework.

Rather than using simple means or linear regression, we adopted a cluster-based approach:

1. **Environment Type Clustering**: We used k-means clustering to group data points into "environment types" based on features that were fully present (Temperature, CO2, Humidity). This accounts for different physical environments (e.g., sun-exposed sessions vs. windowless labs sessions) where sensor correlations might differ.
2. **ExtraTrees Estimator**: Within the MICE framework, we utilized an ExtraTrees estimator to model non-linear relationships.
3. **Variance Preservation**: We modified the imputation logic to include natural distribution variance based on the average standard deviation from the trees, preventing the "flat average" effect.

If a cluster suffered from extreme sparsity (e.g., completely missing a feature like noise), a global median was used as a fallback to prevent model bias.

### 3.6.2 Feature Selection

[...]

### 3.6.3 Data Split and Validation Strategy

[...]

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

*Authors: [Jakub Maciej Baczek, Name]*

<!-- DevOps checklist — address all four points:
     1. General DevOps considerations and planning
     2. Which tools were used and why (or why not)
     3. How DevOps was integrated into the general workflow
     4. What effect did DevOps tools/methods have; what worked well / less well -->

### 3.8.1 DevOps Considerations for Embedded Development

Integrating CI/CD into an embedded C project targeting the ATmega2560 microcontroller presents challenges that are fundamentally different from those encountered in typical software projects. The most significant of these is the absence of practical emulation: unlike web or desktop applications, firmware for an AVR microcontroller cannot be meaningfully run on a standard x86 Linux host without significant behavioural divergence. This makes end-to-end automated testing on real hardware largely impractical in a CI context, as it would require physical hardware attached to the runner or a dedicated hardware-in-the-loop setup.

A further challenge is that much of the codebase is tightly coupled to
hardware-dependent peripherals — UART, Wi-Fi modules, and similar — whose behaviour cannot be exercised without the target hardware. The cross-compilation toolchain adds additional complexity: building firmware for the ATmega2560 requires the AVR-GCC toolchain and PlatformIO, neither of which are part of a standard CI environment, and both of which must be installed and cached correctly to produce a reproducible build.

Automatic deployment presents a similar problem. In a conventional software project,a CD pipeline can push a build artifact directly to its destination — a server, a container registry, a package repository. For embedded firmware, deployment means physically flashing the binary onto the microcontroller, which cannot be done without direct access to the hardware. Fully automated deployment is therefore not feasible in this context. The practical solution adopted here is to treat the compiled firmware as the deployable artifact: the pipeline produces a flashable `.hex` file and uploadsit as a GitHub Actions artifact on every successful build, ready to be downloaded and flashed to the board manually.

These constraints were acknowledged from the outset, and the CI/CD strategy was designed accordingly. Rather than attempting to run firmware on the target or simulate peripherals fully, the CI side of the pipeline focuses on two concerns: automated unit testing of hardware-independent logic, compiled and run natively on the CI runner using GCC, and a firmware build step using PlatformIO to verify that the codebase compiles correctly for the ATmega2560 target. The CD side is reduced to producing and publishing the `.hex` artifact, deferring the final flashing step to the developer. This separation allowed meaningful automation despite the inherent limitations of embedded CI/CD.

### 3.8.2 Tools and Pipeline

The CI pipeline is implemented using GitHub Actions and is defined in a single workflow file. It is triggered on pull requests targeting the `main` and `dev` branches. To avoid unnecessary work when unrelated parts of the repository change, the pipeline checks for modifications within the `IOT/` directory at runtime and skips the build and test steps if none are found.

The pipeline is divided into two sequential jobs:

**`iot-test` — Testing and Coverage**

The first job runs on an `ubuntu-latest` runner and is responsible for compiling and executing the unit test suite natively. Hardware-dependent subsystems — such as UART drivers, SPI communication, and Wi-Fi module interaction — cannot run on a host machine and were therefore isolated behind fakes and stubs using the [FFF (Fake Function Framework)](https://github.com/meekrosoft/fff). These fakes are placed under `test/fakes/` and are included at compile time via the `-I./test/fakes` flag, replacing real peripheral drivers with non-operational or configurable substitutes. This allows the logic within modules such as `wifi_http.c` and `server_api.c` to be tested in isolation without any hardware dependency.

Tests are written using the [Unity](https://github.com/ThrowTheSwitch/Unity) unit test framework for C, with test files compiled and linked against the source under test and the Unity runner. The `make coverage` target compiles all test binaries with GCC's `--coverage` flag (gcov instrumentation), executes them, and then uses `lcov` and `genhtml` to produce an HTML coverage report. Third-party and test infrastructure paths (`fakes/`, `unity/`, `test/`, `/usr/`) are excluded from the coverage data to ensure only production source is measured. The resulting HTML report is uploaded as a GitHub Actions artifact for inspection after each run.

The job also requires a `secrets.ini` file containing build flags for credentials such as Wi-Fi SSID and server host. Since these cannot be stored in the repository, the file is generated dynamically in the pipeline using placeholder values sufficient for compilation and testing.

**`iot-build` — Firmware Compilation**

The second job runs only if `iot-test` succeeds and is responsible for verifying that the firmware compiles correctly for the ATmega2560 target using PlatformIO. PlatformIO is installed via `pip`, with the `~/.platformio` directory cached using `actions/cache` keyed on the hash of `platformio.ini` to avoid redundant downloads across runs. The build targets the `megaatmega2560` PlatformIO environment, and the resulting `firmware.hex` file — ready to be flashed to the microcontroller — is uploaded as a build artifact. This provides a verifiable, reproducible binary for every pull request that passes testing.

### 3.8.3 Integration into Workflow

The CI pipeline was integrated directly into the pull request workflow on GitHub. All pull requests targeting `main` or `dev` were required to pass both pipeline jobs before merging was permitted — a failing test run or a broken firmware build would block the PR. This ensured that neither regressions in testable logic nor compilation failures could be introduced into the protected branches.

Responsibility for fixing a broken build was straightforward: the author of the pull request that caused the failure was expected to resolve it. This kept accountability clear and avoided a situation where broken builds were left for others to diagnose. In practice, outright compilation failures were rare, as code was manually verified on the Arduino before being pushed. The most common failure mode was instead test failures arising from changes to modules covered by the Unity test suite.

### 3.8.4 Outcomes and Evaluation

The DevOps integration was largely successful within the constraints imposed by embedded development. The two-job pipeline structure — separating native unit testing from cross-compiled firmware verification — proved to be a practical and effective approach. Compilation errors targeting the ATmega2560 were caught automatically on every PR, and the unit tests provided a degree of confidence in the correctness of the hardware-independent application logic.

The use of FFF for faking peripheral dependencies worked well in practice: modules could be tested in isolation without requiring any hardware, and the fake implementations were straightforward to write and maintain. The Unity framework similarly integrated cleanly with the native GCC compilation path and the lcov coverage toolchain.

The most significant limitation of the pipeline is the scope of what could be tested automatically. Because tests run natively on an x86 host, only code that could be cleanly decoupled from hardware-specific behaviour was testable in CI. Driver-level code — responsible for directly interfacing with UART, SPI, or the Wi-Fi module — was excluded from automated testing entirely, as no meaningful substitute for actual hardware execution exists at that level. Full integration testing, including end-to-end verification of sensor readings and server communication over a real network, remained a manual process conducted on physical hardware.

Overall, the pipeline added clear value to the development workflow by catching build and logic errors early, enforcing a baseline standard for all contributions, and producing a deployable firmware artifact on every successful PR. The inability to automate hardware-level testing is an inherent property of the embedded domain rather than a gap in the implementation, and the pipeline was scoped accordingly.

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

| Model          | Metric 1 | Metric 2 | Metric 3 |
| :------------- | :------- | :------- | :------- |
| Baseline       |          |          |          |
| [Chosen model] |          |          |          |

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

*Authors: [Jakub Maciej Baczek, Name]*

### 3.11.1 Testing Strategy for Embedded C

Unit testing for the IoT application focused on the two modules containing application logic: `wifi_http`, responsible for establishing TCP connections and constructing HTTP requests, and `server_api`, responsible for session management and server communication. Tests were written using the Unity unit test framework for C and compiled natively on the host using GCC, allowing them to run in CI without any physical hardware.

Hardware-dependent components — TCP socket operations, Wi-Fi driver commands, and buzzer output — were replaced with fakes generated using the FFF (Fake Function Framework). FFF allows individual driver functions to be substituted with configurable stubs that record call counts, capture arguments, and inject return values or response payloads. This made it possible to test application logic such as session ID parsing, retry behaviour, and endpoint construction in full isolation from the underlying hardware.

The remaining codebase consists of low-level peripheral drivers and the main application loop. Drivers are inherently hardware-dependent and cannot be meaningfully tested without the target device. The main loop contains no isolated logic of its own, acting purely as an orchestrator of the other modules. Neither lends itself to unit testing, and both were verified manually on the physical hardware.

### 3.11.2 Unit Test Results

| Module         | Tests | Passed | Failed | Coverage |
| :------------- | :---- | :----- | :----- | :------- |
| `wifi_http`  | 14    | 14     | 0      | 93.9%    |
| `server_api` | 24    | 24     | 0      | 95.3%    |

### 3.11.3 Integration and System-Level Tests

No automated integration testing was implemented, as the hardware constraints discussed in section 3.8.1 make this impractical without a dedicated hardware-in-the-loop setup. Integration and system-level verification was instead performed manually throughout development. This involved flashing the firmware onto the ATmega2560 and observing end-to-end behaviour: confirming that sensor readings were correctly acquired, formatted into the expected JSON payloads, transmitted to the server, and that session lifecycle events such as session start and pulse updates were handled correctly. While informal, this process provided confidence in the integrated behaviour of the system and complemented the unit-level coverage achieved through automated testing.

## 3.12 Frontend Tests

*Authors: [Name, Name]*

### 3.12.1 Testing Strategy

[What test types were applied? Unit tests (component rendering), integration tests
(API mocking), or E2E tests (full browser automation)?]

### 3.12.2 Test Results

| Test Suite        | Tests | Passed | Failed | Coverage |
| :---------------- | :---- | :----- | :----- | :------- |
| Component tests   |       |        |        |          |
| Integration tests |       |        |        |          |

### 3.12.3 Responsiveness Testing

[How was responsive behaviour verified at the three required breakpoints
(576px, 768px, 1200px)? Include screenshots if helpful.]

## 3.13 Machine Learning Tests and DevOps (MLOps)

*Authors: [Piotr, Name]*

### 3.13.1 Machine Learning Testing Strategy TODO: update after the py-cov

The Machine Learning and API (MAL) component is verified through a multi-layered testing strategy that ensures both the data processing logic and the serving infrastructure are robust.

**Data Pipeline Testing**
We implemented unit and integration tests for the data transformation logic (e.g., `test_build_unified_environment_dataset.py`). These tests verify:

- **Merging Logic**: Ensuring that disparate datasets (IoT sensor logs, study ratings, and environmental history) are correctly joined on time-series keys.
- **Preprocessing Correctness**: Validating that the MICE imputation and k-means clustering logic produce consistent outputs without introducing data leakage.
- **Schema Validation**: Ensuring the final processed dataset matches the input requirements of the Random Forest model.

**API and Model Serving Testing**
To verify the serving layer, we use `pytest` (e.g., `test_prediction_api.py`) to test the FastAPI endpoints. These tests serve as integration checks that:

- **Endpoint Availability**: Confirm the `/predict` and health check endpoints respond correctly.
- **Model Loading**: Verify the `rf_model.pkl` artifact is correctly loaded and can produce predictions.
- **Input Validation**: Test the API's resilience to malformed or out-of-range sensor data.
- **Inference Correctness**: Validate that the prediction output matches the expected schema and logical bounds of the Study Suitability Rating.

### 3.13.2 MLOps Considerations

The MAL component requires a specialized DevOps approach to manage the lifecycle of both code and serialized model weights. The primary challenge is ensuring that changes to the data processing logic in `ml_pipeline/` are always compatible with the model artifact committed in `models/`. Unlike traditional software, the "build" artifact in MLOps includes both the code and the serialized model weights (`rf_model.pkl`).

### 3.13.3 Tools and Pipeline

The MLOps pipeline is automated via GitHub Actions (`mlops.yaml`) and executes the testing strategy described above on every pull request.

**`test-and-train` Job**

The pipeline automates several critical verification steps:

1. **Environment Setup**: Python 3.10 is configured with dependencies, using a PostgreSQL sidecar for realistic data integration checks.
2. **Automated Verification**: The pipeline runs the full `pytest` suite, including the data pipeline and API tests. This ensures that no code change breaks the existing model's ability to serve predictions.
3. **Model Artifact Integrity**: The workflow explicitly fails if the `rf_model.pkl` is missing or corrupted, preventing "empty" deployments.
4. **Containerized Continuous Delivery**: On successful validation and merge to `main`, the pipeline builds a Docker image (`mal-api`) and pushes it to the GitHub Container Registry (GHCR).

### 3.13.4 Outcomes and Evaluation

This integrated Testing and MLOps approach significantly reduced deployment risks. By coupling data transformation tests with live API integration checks, we ensured that the entire pipeline—from raw data to study suitability prediction—is verifiable and reproducible. The use of Docker images for deployment ensures that the exact environment used during CI is replicated in production.

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

| Objective     | Status                       | Evidence                    |
| :------------ | :--------------------------- | :-------------------------- |
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

| Component | Repository URL      |
| :-------- | :------------------ |
| IoT       | [GitHub/GitLab URL] |
| Cloud     | [GitHub/GitLab URL] |
| ML        | [GitHub/GitLab URL] |
| Frontend  | [GitHub/GitLab URL] |

## Appendix B — API Documentation

[Link to hosted API docs (Swagger/OpenAPI), or include the endpoint specification here.]

## Appendix C — Hardware Schematics

<!-- Full wiring diagrams if too large for Section 3.2. -->

## Appendix D — Additional ML Figures

<!-- EDA plots, learning curves, feature importance charts that support Section 3.9. -->
