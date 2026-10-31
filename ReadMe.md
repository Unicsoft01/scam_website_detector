# Real-Time Scam Website Detection Using Heuristic and Behavioural Analysis

## Project Description

The Real-Time Scam Website Detection System is a web-based cybersecurity research prototype developed to identify potentially fraudulent websites using a combination of heuristic and behavioural analysis. The system validates submitted URLs, collects permitted website information, extracts static and runtime indicators, applies separate Random Forest models for heuristic and behavioural evidence, and combines the results through hybrid evidence fusion. It then presents a Scam or Legitimate classification together with supporting explanations and stores scan information for evaluation and history management.
Project Disclaimer
> **Disclaimer:** This system is an academic research prototype. Its classifications represent analytical assessments produced from the implemented detection methods and should not be interpreted as legal proof that a website is fraudulent. A **Legitimate** classification does not guarantee that a website is completely safe. Users should never submit passwords, payment details, authentication tokens, or other sensitive credentials to a website solely because the system classifies it as legitimate.

# PART A — PROJECT INFORMATION

## 1. Project Overview

Scam websites are increasingly used to deceive users through fraudulent online shops, investment schemes, cryptocurrency-related scams and technical-support deception. Simple URL-based detection can provide useful initial evidence, but it may not capture important characteristics contained in website structure, security metadata or runtime behaviour.

This project therefore implements a combined detection approach. Heuristic analysis examines observable website and security indicators, while behavioural analysis observes defined runtime characteristics during controlled website interaction. The two evidence sources are processed independently and combined through hybrid evidence fusion to produce a final classification.

The completed system provides a web-based interface for URL submission, controlled website analysis, machine-learning classification, explanation of detected indicators and storage of scan results. The project also experimentally compares heuristic-only, behavioural-only and hybrid approaches using defined evaluation metrics.
Optional project summary table
### Project Summary

| Item | Description |
|---|---|
| Project Type | Academic cybersecurity research prototype |
| Primary Task | Scam website detection |
| Detection Approaches | Heuristic and behavioural analysis |
| Machine Learning | Random Forest |
| Final Decision | Hybrid evidence fusion |
| Classification | Scam / Legitimate |
| Interface | Web-based application |
| Browser Analysis | Playwright with Chromium |
| Database | MySQL |
| Backend | Python-based application |


## 2. Research Aim

> **The aim of this study is to design and implement a real-time scam website detection system using heuristic and behavioural analysis.**


## 3. Research Objectives

The specific objectives are to:

1. **Identify and define relevant heuristic and behavioural indicators for detecting scam websites.**

2. **Design and implement a real-time web-based scam detection system that integrates heuristic and behavioural analysis.**

3. **Evaluate the effectiveness of the implemented hybrid system against heuristic-only and behavioural-only detection using appropriate performance metrics.**
Objective-to-system mapping



### Objective-to-System Mapping

| Research Objective | Implemented System Component |
|---|---|
| Identify heuristic and behavioural indicators | Feature extraction and behavioural observation modules |
| Design and implement the detection system | Web interface, collectors, feature extraction, ML and fusion services |
| Evaluate the hybrid system | Experimental evaluation, performance metrics and comparative analysis |

## 4. System Purpose and Scope

The system is designed to analyse submitted website URLs and determine whether the available evidence is consistent with a scam or legitimate website. It combines website structure, domain and security information with controlled runtime observations to support the final classification.


### 4.1 Detection Scope

The evaluation scope covers the following scam categories:

- Fake online shops
- Investment scams
- Cryptocurrency-related scams
- Technical-support/scare scams
- Other scam websites represented within the project's evaluation dataset


### 4.2 Classification Classes

| Class | Meaning |
|---|---|
| **SCAM** | The available evidence meets the system's criteria for scam classification. |
| **LEGITIMATE** | The available evidence does not meet the system's criteria for scam classification. |


### 4.3 What the System Does

The system:

- accepts a website URL;
- validates and normalises the submitted URL;
- performs controlled website collection;
- extracts heuristic indicators;
- observes defined behavioural indicators;
- generates heuristic and behavioural evidence;
- applies Random Forest classification;
- combines model evidence through hybrid fusion;
- produces a final Scam/Legitimate classification;
- generates an explanation of relevant indicators;
- records scan information and performance data.
4.4 What the System Does Not Do
### 4.4 What the System Does Not Do

The system does not:

- guarantee that a website is completely safe;
- establish legal proof of fraud;
- replace professional cybersecurity investigation;
- execute website content without defined controls;
- provide unrestricted browser interaction;
- guarantee detection of every scam website;
- guarantee that all previously unknown scam techniques will be detected.
5. Key System Features
## 5. Key System Features

| Feature | Description |
|---|---|
| URL Validation | Validates and prepares submitted website addresses for analysis. |
| Safe Website Collection | Collects permitted website and security information under controlled conditions. |
| Heuristic Analysis | Examines structural, URL, domain, HTML and security indicators. |
| Behavioural Analysis | Observes defined runtime website behaviours using controlled browser execution. |
| RF-Heuristic | Applies the trained Random Forest heuristic detection model. |
| RF-Behavioural | Applies the trained Random Forest behavioural detection model. |
| Hybrid Fusion | Combines heuristic and behavioural evidence for the final decision. |
| Scam/Legitimate Classification | Produces the final system classification. |
| Explanation | Presents indicators supporting the analytical result. |
| Scan History | Stores and retrieves previous scan information. |
| Performance Measurement | Records analysis and response-time information. |
| Error Handling | Provides controlled handling of invalid, inaccessible or failed scans. |
Feature flow
```text
URL
 ↓
Validation
 ↓
Collection
 ↓
Feature Extraction
 ↓
Heuristic + Behavioural Analysis
 ↓
Machine Learning
 ↓
Hybrid Fusion
 ↓
Classification + Explanation

---

# 6. System Architecture

```markdown
## 6. System Architecture

The system follows a modular architecture in which URL validation, website collection, feature extraction, machine-learning classification, evidence fusion, explanation and data persistence are separated into distinct application components. This structure supports maintainability and allows individual detection components to be modified without redesigning the complete application.
6.1 High-Level Architecture

For GitHub, Mermaid is a good choice because it keeps the architecture editable rather than embedding a fixed image.

### 6.1 High-Level Architecture

```mermaid
flowchart TD
    A[User] --> B[Web Interface]
    B --> C[URL Validation & Security]

    C --> D[Website Collection]

    D --> D1[HTTP]
    D --> D2[DNS]
    D --> D3[TLS]
    D --> D4[RDAP]
    D --> D5[Controlled Browser]

    D1 --> E[Feature Extraction]
    D2 --> E
    D3 --> E
    D4 --> E
    D5 --> E

    E --> E1[URL Features]
    E --> E2[Domain Features]
    E --> E3[HTML Features]
    E --> E4[TLS Features]
    E --> E5[Behavioural Features]

    E1 --> F[Detection Models]
    E2 --> F
    E3 --> F
    E4 --> F
    E5 --> F

    F --> F1[RF-Heuristic]
    F --> F2[RF-Behavioural]

    F1 --> G[Hybrid Evidence Fusion]
    F2 --> G

    G --> H[Final Classification]
    H --> I[Explanation]
    I --> J[(MySQL Database)]

### Architecture explanation

```markdown
The principal architectural layers are:

1. **Presentation layer** – provides the web interface through which users submit URLs and view results.
2. **API layer** – handles application requests and coordinates communication between the interface and backend services.
3. **Security and validation layer** – validates URLs and applies controls before website collection.
4. **Collection layer** – obtains HTTP, DNS, RDAP and TLS information and performs controlled browser analysis.
5. **Feature extraction layer** – transforms collected information into machine-learning and analytical indicators.
6. **Machine-learning layer** – applies the heuristic and behavioural Random Forest models.
7. **Fusion layer** – combines the independent model evidence into the final detection result.
8. **Explanation layer** – converts relevant detection evidence into user-readable information.
9. **Database layer** – persists scan records, observations and related application data.
10. **History and logging layer** – supports retrieval of previous scans and records system events.
7. End-to-End System Workflow
## 7. End-to-End System Workflow

The following workflow represents the normal processing path from URL submission to presentation of the final detection result.
Workflow diagram
```mermaid
flowchart TD
    A[URL Submission] --> B[URL Validation]
    B --> C[Safe Collection]

    C --> D[Heuristic Analysis]
    C --> E[Behavioural Analysis]

    D --> F[Heuristic Features]
    E --> G[Behavioural Features]

    F --> H[RF-Heuristic]
    G --> I[RF-Behavioural]

    H --> J[Hybrid Fusion]
    I --> J

    J --> K[Final Classification]
    K --> L[Explanation]
    L --> M[Store Result]
    M --> N[Display Result]

### Workflow stages

```markdown
### Workflow Stages

| Stage | Description |
|---|---|
| 1. URL Submission | The user submits a website address through the web interface. |
| 2. URL Validation | The system validates and prepares the URL for controlled analysis. |
| 3. Safe Collection | Website and security information are collected using the available collectors. |
| 4. Heuristic Analysis | Static and security-related indicators are extracted and assessed. |
| 5. Behavioural Analysis | Defined runtime behaviours are observed through controlled browser execution. |
| 6. Feature Extraction | Collected information is transformed into model-ready features. |
| 7. Model Classification | RF-Heuristic and RF-Behavioural independently process their respective evidence. |
| 8. Hybrid Fusion | The model outputs are combined into a final decision. |
| 9. Explanation | Relevant detection evidence is presented to the user. |
| 10. Storage | Scan information and relevant results are recorded. |
| 11. Display | The completed result is presented through the web interface. |
8. URL Security and Validation
## 8. URL Security and Validation

URL validation provides the initial control point before a website is analysed. The system does not treat a submitted URL as automatically safe for collection. Instead, the URL is processed through validation and security controls before the relevant collectors and browser components are invoked.
8.1 URL Validation
### 8.1 URL Validation

The URL validation process addresses:

- URL syntax;
- supported URL schemes;
- malformed or incomplete URLs;
- URL normalisation;
- validation before downstream collection.

The principal implementation is contained in:

`app/core/url_security.py`
8.2 Security Validation
### 8.2 Security Validation

The security-validation component provides controls intended to reduce unsafe or invalid website requests before collection. It operates as a boundary between user-submitted URLs and the collection layer.

Implementation:

`app/core/url_security.py`
8.3 Safe Collection
### 8.3 Safe Collection

After validation, the system performs controlled collection rather than unrestricted website interaction. HTTP, DNS, RDAP and TLS collectors obtain relevant information, while Playwright/Chromium provides the controlled browser environment required for behavioural observation.

The browser component is implemented in:

`app/collectors/browser_environment.py`
8.4 Failure Handling
### 8.4 Failure Handling

The application provides controlled failure handling for conditions such as:

- DNS resolution failure;
- connection failure;
- TLS or certificate-related failure;
- website timeout;
- browser-analysis failure;
- inaccessible websites;
- unsafe or invalid URLs.

Failure-related processing is supported by:

`app/core/failures.py`

`app/services/failure_service.py`
Compact failure workflow
```text
URL
 ↓
Validation
 ↓
[Valid?] ── No ──> Controlled Error
 ↓ Yes
Collection
 ↓
[Collection Successful?]
 ├── No ──> Failure Handling
 └── Yes
       ↓
    Analysis

---

# 9. Website Data Collection

```markdown
## 9. Website Data Collection

Website collection provides the evidence required by the feature-extraction and detection components. The system separates collection into specialised modules so that different sources of website information can be processed independently.
9.1 HTTP Collector
### 9.1 HTTP Collector

**Implementation:** `app/collectors/http_collector.py`

The HTTP collector obtains permitted HTTP/HTTPS response information required for subsequent analysis. This provides information about the website's accessible web response and related collection metadata.
9.2 DNS Collector
### 9.2 DNS Collector

**Implementation:** `app/collectors/dns_collector.py`

The DNS collector retrieves domain-resolution information used to support domain and infrastructure-related analysis.
9.3 RDAP Collector
### 9.3 RDAP Collector

**Implementation:** `app/collectors/rdap_collector.py`

The RDAP collector obtains available registration-related domain information. This provides additional domain evidence that can be incorporated into feature extraction.
9.4 TLS Collector
### 9.4 TLS Collector

**Implementation:** `app/collectors/tls_collector.py`

The TLS collector examines available TLS/security information associated with the website connection. The resulting information supports security-related feature extraction.
9.5 Browser Environment
### 9.5 Browser Environment

**Implementation:** `app/collectors/browser_environment.py`

The browser environment uses **Playwright with Chromium** to perform controlled website navigation and observe defined runtime behaviours. Depending on the website and available content, the behavioural collection process can capture information associated with navigation, redirects, browser events, dialogs, downloads and other implemented runtime observations.

The browser component is deliberately controlled rather than providing unrestricted interaction with the target website.
Collection architecture
```mermaid
flowchart LR
    A[Validated URL] --> B[Collection Layer]

    B --> C[HTTP]
    B --> D[DNS]
    B --> E[RDAP]
    B --> F[TLS]
    B --> G[Playwright / Chromium]

    C --> H[Collected Evidence]
    D --> H
    E --> H
    F --> H
    G --> H

    H --> I[Feature Extraction]

---

```markdown
# 10. Feature Extraction

## 10. Feature Extraction

Feature extraction converts collected website information into structured indicators for analysis and machine-learning classification. The project separates static/heuristic evidence from runtime behavioural evidence while retaining a common processing architecture.
10.1 URL Features
### 10.1 URL Features

**Implementation:** `app/features/url_features.py`

URL features represent characteristics of the submitted website address. Depending on the implemented feature set, these can include properties such as URL length, URL structure, subdomain characteristics, suspicious characters and IP-address-based URLs.

These features primarily support the heuristic detection pathway.
10.2 Domain Features
### 10.2 Domain Features

**Implementation:** `app/features/domain_features.py`

Domain features represent characteristics obtained from domain and registration-related information. These features provide additional evidence about the identity and structure of the website domain.
10.3 HTML Features
### 10.3 HTML Features

**Implementation:** `app/features/html_features.py`

HTML features are derived from the structure and content of collected webpage markup. They provide evidence relating to webpage elements and structures that may contribute to scam-site detection.
10.4 TLS Features
### 10.4 TLS Features

**Implementation:** `app/features/tls_features.py`

TLS features represent security-related characteristics obtained during TLS inspection. They provide additional security evidence for the heuristic detection process.
10.5 Behavioural Features
### 10.5 Behavioural Features

**Implementation:** `app/features/behavioural_features.py`

Behavioural features represent runtime observations obtained during controlled browser interaction. Rather than examining only the static structure of a website, this component captures defined behaviours that occur during page execution and navigation.

Behavioural evidence therefore differs from heuristic evidence in its emphasis on what the website does during controlled execution rather than only what is observable from its static properties.
Static vs behavioural evidence
### Static and Behavioural Evidence

| Evidence Type | Primary Focus | Example Source |
|---|---|---|
| Heuristic | Observable structural and security characteristics | URL, domain, HTML and TLS information |
| Behavioural | Runtime characteristics during controlled execution | Browser navigation and runtime observations |
| Hybrid | Combined evidence from both approaches | RF-Heuristic + RF-Behavioural + fusion |
Feature architecture
```mermaid
flowchart TD
    A[Collected Website Information]

    A --> B[URL Features]
    A --> C[Domain Features]
    A --> D[HTML Features]
    A --> E[TLS Features]
    A --> F[Behavioural Features]

    B --> G[Heuristic Evidence]
    C --> G
    D --> G
    E --> G

    F --> H[Behavioural Evidence]

    G --> I[RF-Heuristic]
    H --> J[RF-Behavioural]

    I --> K[Hybrid Fusion]
    J --> K

---

## 11. Heuristic Detection Model

The heuristic detection branch analyses static and security-related characteristics of a submitted website. Its purpose is to identify structural, URL, domain, HTML and TLS indicators that may be associated with scam websites.

### 11.1 Heuristic Detection Pipeline

```mermaid
flowchart TD
    A[Heuristic Features] --> B[Feature Preparation]
    B --> C[RF-Heuristic]
    C --> D[Heuristic Score / Class]
11.2 Model Description

The heuristic branch uses a trained Random Forest classifier. The model receives the prepared heuristic feature vector and produces a classification output used as one of the evidence sources for the final hybrid decision.

Component	Description
Detection approach	Heuristic analysis
Machine-learning model	Random Forest Classifier
Input	Prepared heuristic feature vector
Output	Heuristic prediction and associated model evidence
Role	Independent static/security evidence source
Model file	models/rf_heuristic.joblib
11.3 Interpretation

The heuristic result represents the model's assessment based on the static and security characteristics available during the scan. It is not used in isolation as definitive proof of fraud; instead, it forms one part of the system's overall evidence.

11.4 Model Location
models/
└── rf_heuristic.joblib

The trained model is supplied with the application and is loaded during normal system operation. Model retraining is not required for normal installation or use.


---

# 12. Behavioural Detection Model

```markdown
## 12. Behavioural Detection Model

The behavioural detection branch examines how a website behaves during controlled browser execution. This complements static heuristic analysis by considering runtime evidence that may not be visible from the URL or static webpage structure alone.

### 12.1 Behavioural Detection Pipeline

```mermaid
flowchart TD
    A[Controlled Browser Observation] --> B[Behavioural Features]
    B --> C[Feature Preparation]
    C --> D[RF-Behavioural]
    D --> E[Behavioural Score / Class]
12.2 Model Description
Component	Description
Detection approach	Behavioural analysis
Machine-learning model	Random Forest Classifier
Input	Prepared behavioural feature vector
Output	Behavioural prediction and associated model evidence
Role	Independent runtime evidence source
Model file	models/rf_behavioural.joblib
12.3 Behavioural Evidence

Behavioural evidence refers to observable characteristics produced while the target website is analysed in the controlled browser environment. The evidence is therefore concerned with website behaviour during execution rather than only its static structure.

The behavioural model provides an independent evidence stream that can subsequently be combined with heuristic evidence by the hybrid fusion component.

12.4 Model Location
models/
└── rf_behavioural.joblib

The supplied trained model is used directly by the application. Normal users do not need to retrain the behavioural model.


---

# 13. Hybrid Evidence Fusion

```markdown
## 13. Hybrid Evidence Fusion

Hybrid evidence fusion is a central component of the detection architecture. It combines evidence generated independently by the heuristic and behavioural detection branches to support the final classification.

### 13.1 Fusion Pipeline

```mermaid
flowchart TD
    A[Heuristic Evidence] --> C[Hybrid Fusion]
    B[Behavioural Evidence] --> C
    C --> D[Final Decision]
13.2 Why Hybrid Detection?

Heuristic and behavioural analysis examine different aspects of a website. Static characteristics can provide useful structural and security evidence, while runtime analysis can reveal behaviours that may not be apparent from static inspection alone.

Combining the two evidence sources therefore provides a broader analytical basis than relying exclusively on one detection approach.

13.3 Fusion Configuration

The hybrid configuration is stored in:

models/hybrid_fusion_config.json

The configuration is loaded by the application to control the implemented fusion process.

Important: The README does not prescribe fixed fusion weights or mathematical values. The deployed configuration should be treated as the authoritative source for the current implementation.

13.4 Fusion Process
RF-Heuristic
     │
     ├── Heuristic Evidence
     │
     ▼
 Hybrid Fusion
     ▲
     │
     ├── Behavioural Evidence
     │
RF-Behavioural
     │
     ▼
Final Classification

The resulting fused evidence is passed to the final classification and explanation stages.


---

# 14. Scam Classification

```markdown
## 14. Scam Classification

The system produces a binary final classification based on the available analytical evidence.

| Classification | Meaning |
|---|---|
| **SCAM** | The available evidence meets the system's criteria for scam classification. |
| **LEGITIMATE** | The available evidence does not meet the system's criteria for scam classification. |

### Classification Interpretation

The final classification is an analytical output of the research prototype. It should not be interpreted as absolute proof that a website is fraudulent or completely safe.

A **SCAM** result indicates that the characteristics detected by the implemented system are consistent with scam-site indicators.

A **LEGITIMATE** result means that the available evidence did not meet the system's scam classification criteria. It does **not** guarantee that the website is completely safe.
15. Explanation and Interpretability
## 15. Explanation and Interpretability

The system is designed to provide more than a simple `SCAM` or `LEGITIMATE` output. The explanation component presents information about the indicators and evidence contributing to the analytical result.

### Implementation

```text
app/services/explanation_service.py
Explanation Pipeline
Explanation Information

Depending on the available scan evidence, the result interface can communicate:

detected indicators;
heuristic evidence;
behavioural evidence;
risk-related information;
analytical reasoning;
user-readable interpretation.

This makes the system more interpretable than a classification-only system because the user can examine the evidence associated with the result.


### Recommended screenshot

```markdown
> **Recommended screenshot:** Insert a screenshot of the completed result page showing the final classification together with the explanation/indicator section.

**Figure X: Scam Detection Result and Explanation Interface**  
*Source: Screenshot from the implemented system (2026).*
16. Database and Data Persistence
## 16. Database and Data Persistence

The system uses a relational database to persist scan-related information and support retrieval of previous analysis results.

### 16.1 Database Technology

The application uses:

| Technology | Purpose |
|---|---|
| MySQL | Persistent relational database |
| SQLAlchemy | Object-relational mapping and database interaction |
| PyMySQL | MySQL connectivity |

### 16.2 Database Connection

The principal database implementation is located in:

```text
app/database/database.py
app/database/session.py

The database connection is configured through the application's settings, with the connection string supplied through the environment configuration.

16.3 Database Models

Database entities are defined in:

app/database/models.py

SQLAlchemy is used to represent application data as database models and to manage database interactions.

16.4 Stored Information

The database supports the persistence of information associated with website scans, observations, events and system operations.

The principal implemented entities include:

Scans
Heuristic_Observations
Behavioural_Observations
Scan_Events
System_Logs

Note: The exact deployed database schema should be treated as authoritative. Additional entities should only be documented here if they are present in the final app/database/models.py implementation.

Database Flow

---

# 17. Scan History

```markdown
## 17. Scan History

Completed scans are persisted so that previously analysed websites can be retrieved through the application's history interface.

### 17.1 Scan History Pipeline

```text
URL Submission
      ↓
Website Analysis
      ↓
Classification
      ↓
Result Storage
      ↓
History Retrieval
      ↓
User Interface
17.2 Implementation

The principal history components are:

app/services/scan_query_service.py
app/services/scan_repository.py

The repository component supports interaction with stored scan information, while the query service provides the application-level retrieval functionality.

17.3 History Interface

The history interface allows users to review previously completed scans and access the corresponding stored results.

The history functionality is intended to support usability, traceability and evaluation of previously performed analyses.


### Recommended screenshot

```markdown
> **Recommended screenshot:** Insert the application's scan-history page.

**Figure X: Scan History Interface**  
*Source: Screenshot from the implemented system (2026).*
18. User Interface
## 18. User Interface

The application provides a web-based interface through which users submit URLs, monitor analysis, inspect results and review previous scans.

The principal interface templates are located in:

```text
app/templates/
├── base.html
├── index.html
├── result.html
├── history.html
└── error.html
18.1 Home / Scan Page

The home page provides the primary entry point for submitting a website URL for analysis.

18.2 URL Input

The user enters the website address into the URL submission interface. The submitted address is then passed to the validation and analysis pipeline.

18.3 Scan Progress / Status

The interface communicates the state of the scan while the system performs the required analysis operations.

18.4 Result Page

The result page presents the final classification and relevant analytical information.

18.5 Explanation Panel

The explanation component provides supporting indicators and interpretation associated with the result.

18.6 Scan History

The history page provides access to previously stored scan information.

18.7 Error / Failure Page

The error interface provides controlled feedback when a URL cannot be analysed successfully because of validation, accessibility, collection or processing problems.


### Recommended screenshot layout

```markdown
### Recommended Interface Screenshots

| Screenshot | Recommended Content |
|---|---|
| Figure X | Home/URL submission page |
| Figure X | Scan progress/status |
| Figure X | Scam classification result |
| Figure X | Legitimate classification result |
| Figure X | Explanation/indicators |
| Figure X | Scan history |
| Figure X | Error/failure response |
19. Technologies Used
## 19. Technologies Used

The completed system combines web development, machine learning, browser automation, data processing and database technologies.

| Technology | Purpose |
|---|---|
| Python 3.11 | Core application implementation |
| FastAPI | Backend/API services |
| SQLAlchemy | Database ORM |
| MySQL | Persistent database |
| PyMySQL | MySQL database connectivity |
| BeautifulSoup4 | HTML parsing |
| Playwright | Controlled browser automation |
| Chromium | Browser execution environment |
| Pandas | Data processing |
| NumPy | Numerical processing |
| Scikit-learn | Machine-learning implementation |
| Joblib | Trained-model persistence |
| HTML/CSS | Web interface |
| JavaScript | Client-side interaction |
Technology architecture
```text
Web Interface
     │
     ▼
FastAPI Application
     │
     ├── Collection
     ├── Feature Extraction
     ├── Machine Learning
     └── Services
             │
             ▼
        SQLAlchemy
             │
             ▼
           MySQL

Playwright + Chromium
          │
          ▼
Controlled Behavioural Analysis

---

# 20. Project Directory Structure

```markdown
## 20. Project Directory Structure

The repository is organised into application, data, model, testing and supporting components.

```text
scam_website_detector/
│
├── app/
│   ├── api/
│   ├── collectors/
│   ├── core/
│   ├── database/
│   ├── features/
│   ├── ml/
│   ├── schemas/
│   ├── services/
│   ├── static/
│   ├── templates/
│   └── web/
│
├── data/
├── logs/
├── models/
├── reports/
├── tests/
├── training/
│
├── requirements.txt
├── .env.example
├── setup_windows.bat
├── run_setup_check.bat
├── run_application.bat
└── README.md
Directory Description
Directory	Purpose
app/	Main application source code
app/api/	API routes, dependencies and schemas
app/collectors/	HTTP, DNS, RDAP, TLS and browser collection
app/core/	Configuration, security, failure and performance utilities
app/database/	Database connection, sessions and models
app/features/	URL, domain, HTML, TLS and behavioural feature extraction
app/ml/	Machine-learning models, preprocessing, evaluation and hybrid fusion
app/schemas/	Application data schemas
app/services/	Scan, prediction, explanation, failure and repository services
app/static/	CSS and JavaScript resources
app/templates/	HTML interface templates
app/web/	Web routing
data/	Dataset, processing and evaluation artefacts
logs/	Application/system logs
models/	Trained deployment models and configuration
reports/	Generated evaluation and visualisation outputs
tests/	Software and system tests
training/	Dataset preparation, model training and evaluation scripts

> **Deployment note:** The `training/` directory contains research/training utilities. Normal users do not need to execute the training scripts to operate the completed application.
21. Machine-Learning Model Files
## 21. Machine-Learning Model Files

The application is distributed with trained machine-learning artefacts required for normal detection.

### 21.1 Deployment Models

```text
models/
├── rf_heuristic.joblib
├── rf_behavioural.joblib
└── hybrid_fusion_config.json
File	Purpose
rf_heuristic.joblib	Trained Random Forest heuristic model
rf_behavioural.joblib	Trained Random Forest behavioural model
hybrid_fusion_config.json	Configuration for hybrid evidence fusion
21.2 Runtime Model Package

The repository may also contain a versioned runtime package:

models/
└── runtime/
    └── v1.1.0/

The runtime package contains versioned model artefacts and supporting deployment metadata.

21.3 Model Usage

The application loads the supplied trained models during operation.

Model retraining is not required for normal installation or system operation.

The training scripts are retained for research reproducibility and future experimentation but are not part of the normal user workflow.


---

# 22. Evaluation Dataset

```markdown
## 22. Evaluation Dataset

The final evaluation dataset contains website URLs used to assess the implemented detection approaches.

### 22.1 Dataset Composition

| Category | Samples |
|---|---:|
| Legitimate Websites | 9 |
| Scam/Phishing Websites | 40 |
| **Total Evaluation URLs** | **49** |

### 22.2 Evaluation Purpose

The evaluation dataset was used to assess the detection behaviour of the implemented heuristic, behavioural and hybrid approaches and to calculate the selected performance metrics.

The scam examples represented the categories included in the project's evaluation data, while legitimate examples provided the comparison class required for binary classification.

### 22.3 Dataset Preparation

The broader project contains dataset collection, validation, auditing, feature extraction, cleaning, splitting and evaluation stages. The final evaluation set represents the data selected for the completed experimental assessment.

### 22.4 Dataset Limitation

The evaluation set contains **49 URLs**, with 40 scam examples and 9 legitimate examples. This relatively small sample limits the extent to which the resulting performance measurements can be generalised to the wider population of websites.

Results should therefore be interpreted as findings from the defined experimental evaluation rather than universal estimates of scam-detection performance.
Recommended chart
> **Recommended figure:** Insert the final legitimate-versus-scam evaluation dataset bar chart.

**Figure X: Distribution of Evaluation Website Categories**  
*Source: Author's experimental dataset (2026).*
23. Model Evaluation
## 23. Model Evaluation

The system evaluates three detection approaches:

1. Heuristic-only detection;
2. Behavioural-only detection;
3. Hybrid detection.

The evaluation uses classification metrics and comparative analysis to determine how the approaches perform against the defined evaluation dataset.

### 23.1 Accuracy

Accuracy measures the proportion of evaluation cases correctly classified by the detection approach.

```text
Accuracy = Correct Predictions / Total Predictions
23.2 Precision

Precision measures the proportion of websites classified as scam that were correctly identified as scam cases.

Precision = TP / (TP + FP)
23.3 Recall

Recall measures the proportion of actual scam websites correctly detected by the system.

Recall = TP / (TP + FN)
23.4 F1-Score

F1-score provides a combined measure of precision and recall.

F1 = 2 × (Precision × Recall) / (Precision + Recall)
23.5 Confusion Matrix

The confusion matrix records:

	Predicted Legitimate	Predicted Scam
Actual Legitimate	True Negative (TN)	False Positive (FP)
Actual Scam	False Negative (FN)	True Positive (TP)

The confusion matrix provides a more detailed view of correct and incorrect classifications than accuracy alone.

23.6 Comparative Evaluation

The three approaches are compared using the same evaluation framework:

Approach	Accuracy	Precision	Recall	F1-Score
Heuristic Only	See final evaluation results	See final evaluation results	See final evaluation results	See final evaluation results
Behavioural Only	See final evaluation results	See final evaluation results	See final evaluation results	See final evaluation results
Hybrid	See final evaluation results	See final evaluation results	See final evaluation results	See final evaluation results

Important: Replace the cells above with the final values from the frozen evaluation results before publishing the README. No performance values should be manually estimated or inferred.


### Recommended figures

```markdown
### Recommended Evaluation Figures

- Confusion matrix for RF-Heuristic
- Confusion matrix for RF-Behavioural
- Confusion matrix for Hybrid
- Comparative model-metrics chart
- False-positive-rate chart
- ROC curves, where supported by the final evaluation data
24. Testing
## 24. Testing

Testing was used to determine whether the implemented system performs its intended functions and whether its principal components operate together correctly.

### 24.1 Unit Testing

Individual application components are tested independently where applicable, including feature extraction, validation, collection and service-level functionality.

### 24.2 Integration Testing

Integration testing examines communication between major components such as URL validation, collectors, feature extraction, machine-learning services and database operations.

### 24.3 Functional Testing

Functional testing verifies the principal user workflow:

```text
Submit URL
    ↓
Validate URL
    ↓
Analyse Website
    ↓
Generate Features
    ↓
Classify
    ↓
Generate Explanation
    ↓
Store Result
    ↓
Display Result
24.4 Behavioural Analysis Testing

Behavioural testing verifies controlled browser execution and the collection of implemented runtime indicators.

24.5 Database Testing

Database testing verifies database connectivity, model interaction and persistence/retrieval of scan information.

24.6 End-to-End Testing

End-to-end testing evaluates the complete workflow from URL submission through final result presentation and storage.

24.7 User Acceptance Testing

User acceptance testing assesses whether the completed interface and workflow satisfy the intended functional requirements from a user perspective.

24.8 Performance Testing

Performance testing records operational timing associated with website analysis and response processing.

Testing Summary
Test Area	Purpose
Unit	Verify individual components
Integration	Verify component interaction
Functional	Verify required system functions
Behavioural	Verify runtime website observation
Database	Verify persistence and retrieval
End-to-End	Verify complete scan workflow
User Acceptance	Verify usability and functional suitability
Performance	Assess operational response time

---

# 25. Performance

```markdown
## 25. Performance

System performance is influenced by URL validation, network availability, website response characteristics, static collection, browser execution, behavioural observation, feature extraction, model prediction and database operations.

### 25.1 Response Time

The application records timing information associated with website analysis. Response time can vary considerably because the target website is an external dependency.

### 25.2 Scan Duration

A complete scan may involve multiple collection operations and controlled browser execution. Consequently, total scan duration is expected to be greater than a simple URL-only classification process.

### 25.3 Browser-Analysis Overhead

Behavioural analysis introduces additional processing because the target website must be loaded and observed within the controlled browser environment.

### 25.4 Database Operations

Scan information must be persisted after analysis. Database operations therefore contribute to the overall application workflow.

### 25.5 Resource Considerations

The browser component is particularly resource-intensive compared with simple URL processing. Adequate memory and CPU resources are therefore important when performing repeated scans.

### Performance Data

Where available, the project records response-time information in the experimental performance outputs. The final numerical values should be taken directly from the completed evaluation artefacts rather than manually estimated.
26. Limitations
## 26. Limitations

The system should be interpreted within the boundaries of its dataset, implementation and controlled experimental environment.

### 26.1 Dataset Size

The final evaluation dataset contains 49 URLs. The relatively small sample limits statistical generalisation.

### 26.2 Evaluation Composition

The evaluation data does not represent the full diversity of websites encountered on the Internet. Results may therefore differ when the system is applied to substantially different website populations.

### 26.3 Website Accessibility

Detection depends partly on the availability and accessibility of website content. Domains that are offline, unreachable or unavailable to the collection process may produce incomplete evidence.

### 26.4 Automated Collection Restrictions

Some websites restrict automated requests or browser access. Such restrictions can reduce the amount of information available for analysis.

### 26.5 Dynamic JavaScript Behaviour

Modern websites can contain complex and rapidly changing JavaScript behaviour. A controlled browser observation cannot necessarily reproduce every possible user interaction or execution state.

### 26.6 False Positives and False Negatives

The system can incorrectly classify websites. Legitimate websites may contain characteristics associated with scam sites, while sophisticated scam websites may avoid detectable indicators.

### 26.7 Changing Scam Techniques

Scam websites continuously change their techniques, infrastructure and presentation. Detection models trained on historical evidence may therefore encounter previously unseen patterns.

### 26.8 Model Generalisation

The performance of the trained models depends on the characteristics and diversity of the training and evaluation data. Results should not automatically be generalised to all future websites.

### 26.9 Controlled Browser Limitations

The behavioural component operates within a controlled execution environment. This provides an important safety boundary but also limits unrestricted interaction with target websites.
27. Responsible Use and Security Considerations
## 27. Responsible Use and Security Considerations

The system was developed for legitimate cybersecurity research, educational evaluation and controlled scam-website analysis.

### Responsible Use Principles

- Use the system only for legitimate security analysis and research.
- Do not use the system to conduct unauthorised activity against websites.
- Do not submit passwords, payment information, authentication tokens or other sensitive credentials.
- Treat analysed websites as potentially untrusted.
- Do not interpret a `SCAM` result as a legal determination of fraud.
- Do not interpret a `LEGITIMATE` result as a guarantee of safety.
- Independently verify important security decisions using additional evidence.
- Respect applicable laws, website policies and organisational security procedures.

### Controlled Analysis

Website interaction is performed through controlled collection mechanisms and a controlled browser environment. The system is designed to observe defined website characteristics rather than provide unrestricted interaction with potentially malicious websites.

### Security Decision-Making

The system should be treated as a **decision-support and research tool**, not as an emergency cybersecurity authority or a replacement for professional investigation.

Important security decisions should therefore consider additional sources of evidence and, where appropriate, human cybersecurity expertise.

> **Final Safety Notice:** Never enter confidential credentials or sensitive personal information into a website merely because this system classifies it as `LEGITIMATE`.
Recommended README Part A closing block

I strongly recommend ending Part A with a compact architecture summary before beginning the installation instructions in Part B.

---

## Part A Summary

The completed system provides an integrated workflow for scam website analysis:

```text
URL
 ↓
Validation & Security
 ↓
Website Collection
 ├── HTTP
 ├── DNS
 ├── RDAP
 ├── TLS
 └── Controlled Browser
 ↓
Feature Extraction
 ├── URL
 ├── Domain
 ├── HTML
 ├── TLS
 └── Behavioural
 ↓
RF-Heuristic ─────┐
                  ├── Hybrid Fusion
RF-Behavioural ───┘
                  ↓
          Scam / Legitimate
                  ↓
             Explanation
                  ↓
              MySQL
                  ↓
            Scan History

The supplied repository contains the trained models and application components required for normal operation. Users do not need to retrain the machine-learning models to install or use the system.