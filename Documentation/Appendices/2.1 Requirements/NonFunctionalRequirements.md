# StudyHelper – Non-Functional Requirements

This document defines the non-functional requirements (NFRs) for the StudyHelper system, categorized under the FURPS+ quality model. These requirements specify the operational limits, quality attributes, and security constraints of the system.

---

## 1. Usability
- **Responsive Layout**: The user interface must adapt dynamically without horizontal scrolling or content clipping across screen widths from $320\text{ px}$ (mobile) to $1920\text{ px}$ (desktop).
- **Localization Transition**: The application must allow switching between English and Danish, updating 100% of visible user interface text within $500\text{ ms}$ of selection.

## 2. Reliability
- **Data Persistence**: The database must persist all telemetry and user profile data such that $0\%$ of data is lost in the event of database service termination or hardware power loss.
- **Automated Session Cleanup**: The backend must mark a study session as ended if no keepalive signal is received from the corresponding device for a continuous period of $30\text{ seconds}$.

## 3. Performance
- **Model Prediction Speed**: The prediction service must return the study suitability rating within $200\text{ ms}$ for $99\%$ of requests under a load of up to 10 concurrent requests.
- **Device Telemetry Frequency**: During an active study session, the device must transmit telemetry data to the backend at an interval of $30\text{ seconds} \pm 1\text{ second}$.

## 4. Supportability
- **Deployment Configuration**: All server-side components must be deployable to a target environment using a single orchestration command in under $5\text{ minutes}$.
- **Firmware Portability**: The microcontroller source code must compile using standard GCC toolchains for 8-bit AVR microcontrollers without modifications to the codebase.

## 5. Security
- **Brute-Force Protection**: The authentication service must temporarily lock a user account for $15\text{ minutes}$ after 5 consecutive failed login attempts.
- **Data Transmission Security**: All public API requests and user transactions must be encrypted using TLS version 1.2 or higher.

## 6. DevOps and Verification
- **Automated Build Gates**: The automated CI/CD pipeline must execute unit tests and block the merge if test coverage falls below $80\%$ or if any test fails, completing the entire run within $10\text{ minutes}$.
