# ✈️ SLA Airline API System

## Project Overview
SLA Airline API is a robust backend solution designed to manage modern airline operations. The system handles everything from flight scheduling and bulk data management to secure passenger check-ins. It is built with a focus on **scalability**, **security**, and **cloud-native** principles.

---

## Technology Stack

| Category | Technology |
| :--- | :--- |
| **Language** | Python 3.11 |
| **Framework** | Flask 3.1.3 |
| **Database** | SQLite with Flask-SQLAlchemy |
| **Authentication** | Flask-JWT-Extended (JWT) |
| **API Documentation** | Flasgger (Swagger UI) |
| **Deployment** | Azure App Services (Linux) |
| **Testing** | k6 (Load Testing) |

---

## Data Model (ER Diagram)
The database structure is designed to support high-performance flight querying and secure ticketing.

<img src="/assets/er_diagram.png" width="500" style="height: auto;" alt="ER Diagram">
<img src="/assets/details.png" width="800" style="height: auto;" alt="ER Diagram Details">
<img src="/assets/relations.png" width="800" style="height: auto;" alt="ER Diagram Relations">


---

## Research & Development Journey
During the lifecycle of this project, I conducted extensive research to implement industry-standard practices and overcome deployment challenges:

### 1. Architectural Patterns
* **Layered Design:** I moved away from monolithic scripts by implementing **Flask Blueprints**. This separates the application into logical layers: Routes (Controllers), Services, and Models.
* **Data Transfer:** Used **Marshmallow** for object serialization to ensure clean and structured API responses.

### 2. Cloud Engineering (Azure)
* **Gunicorn Integration:** Researched how to run Python in production using WSGI servers rather than the built-in Flask development server.
* **Environment Configuration:** Solved deployment bottlenecks by mapping `WEBSITES_PORT` to 8000 and defining custom startup commands to handle Azure’s Linux container lifecycle.

---

## Load Testing Report (Performance Analysis)

I performed a rigorous stress test using **k6** to evaluate the system's stability under high concurrency.


### 🔍 Test Scenarios
1. **Endpoint 1:** `GET /flights/query` (Heavy database filtering)
2. **Endpoint 2:** `GET /flights/passengers` (JWT Authentication check)


### 📈 Metrics Summary
Below are the results captured during the **100 Virtual Users (VU)** stress test:

| Metric | Result Value |
| :--- | :--- |
| **Total Requests** | 2460 |
| **Avg. Response Time** | **826.14 ms** |
| **p95 Response Time** | **4.93 s** |
| **Throughput** | 23.81 req/s |
| **Success Rate (Checks)** | **100%** |
| **HTTP Error Rate** | 50.00% (Expected 401 Unauthorized) |


<img src="/assets/k6_load_testing.png" width="600" alt="k6 Load Test Results">


### Performance Insights
* **Security Resilience:** The 50% error rate is a **positive security indicator**. It confirms the JWT middleware successfully blocked 1230 unauthorized attempts to access protected passenger data, returning the correct `401 Unauthorized` status.
* **Bottleneck Analysis:** The spike in p95 latency (4.93s) was identified as a CPU/RAM limitation of the Azure Basic tier during peak load.
* **Scalability Recommendations:** Future versions will implement **Redis Caching** to reduce database load and **Horizontal Auto-scaling** on Azure to maintain low latency during traffic spikes.

---

## 🔗 Deployed Swagger URL
The API is currently hosted on Microsoft Azure:
👉 [SLA Airline API Swagger Docs](https://sila-api-air-gsh6hgdxgwcedub0.francecentral-01.azurewebsites.net/apidocs/)
