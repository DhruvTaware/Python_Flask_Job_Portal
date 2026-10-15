# Master Test Plan (STQA)

## Project: Software Testing and Quality Assurance of a Job Application and Resume Submission Portal
**Document Identifier:** STQA-MTP-01  
**Version:** 1.0  
**Date:** October 2026  
**Status:** Approved for Execution  

---

### 1. Introduction and Objectives
The objective of this Software Testing and Quality Assurance (STQA) project is to verify and validate the functionality, security, data integrity, and usability of the **Python Flask Job Application and Resume Submission Portal**.

Testing ensures that:
1. Candidate and employer workflows function accurately without crashes or data corruption.
2. Broken access controls and authorization flaws (OWASP A01) are identified and neutralized.
3. Uploaded resumes and personal candidate details are safeguarded against unauthorized access.
4. The system reliably runs in modern Python runtimes (Python 3.13+) on Windows environments.

---

### 2. Scope of Testing

#### 2.1 In-Scope
* **User Authentication & Authorization:**
  * Role separation between 'Company' and 'Job Seeker'.
  * Secure bcrypt password hashing and session management.
  * Access control on protected endpoints (`/post_jobs`, `/post_cvs`, `/show_applications`, `/resume`).
* **Job Posting & Browsing:**
  * Job creation with input boundary and character validation.
  * Industry categorization and public job listing display.
* **Resume & Application Submission:**
  * Multipart form file upload verification (`.png`, `.jpg`, `.bmp`).
  * Filename collision resistance and path traversal defense.
  * Application ranking and sorting by academic degree and years of experience.
* **Review System:**
  * Review submission and dynamic presentation in the homepage carousel.
* **Non-Functional & Quality Attributes:**
  * Test database isolation (preventing production `site.db` pollution).
  * Error handling on missing files or malformed inputs.

#### 2.2 Out-of-Scope
* Production Twilio Video live streaming infrastructure (backend token server is not implemented in the current prototype).
* Stress testing exceeding 5,000 concurrent virtual users.

---

### 3. Test Levels and Strategy

| Test Level | Scope | Framework / Tool | Success Metric |
| :--- | :--- | :--- | :--- |
| **Unit Testing** | Database models, default values, form validation logic | `pytest`, `unittest` | 100% pass rate; >85% model & form coverage |
| **Integration Testing** | HTTP request/response flows, session state, authorization checks | `pytest`, Flask Test Client | 100% pass rate on role transitions and access controls |
| **System / E2E Automation** | Cross-browser candidate and employer journeys | Selenium 4 WebDriver (Chrome & Edge) | Flawless end-to-end execution without UI timeouts |
| **Regression Testing** | Automated re-run of all suites upon bug fixes | `pytest -m regression` | Zero regressions introduced |
| **Security Testing** | Authorization boundary tests, unauthenticated file access tests | Custom security fixtures in `pytest` | Zero unauthorized data leaks |

---

### 4. Test Environment Specification

* **Operating System:** Windows 11 (64-bit)
* **Python Runtime:** Python 3.13.1 (Virtual Environment `venv`)
* **Web Framework:** Flask 3.1.3, Werkzeug 3.1.9, Jinja2 3.1.6
* **Database Engine:** SQLite (Isolated temporary database for automated tests, `site.db` for manual runtime)
* **Browsers for Automation:** Google Chrome (v120+), Microsoft Edge (v120+)
* **Test Runners & Reporting:** `pytest 9.1+`, `pytest-html 4.2+`, `coverage.py 7.16+`

---

### 5. Test Data Management & Database Isolation
* **Zero Production Mutation:** Automated tests **must never** execute against or mutate `app/site.db`.
* **Temporary DB Fixture:** Each test execution uses a dedicated temporary SQLite database (`stqa_test_*.db`) initialized with `db.create_all()` and dropped upon test completion via `tests/conftest.py`.

---

### 6. Entry and Exit Criteria

#### 6.1 Entry Criteria
* Python virtual environment initialized with all dependencies installed.
* Application imports cleanly without `RuntimeError` or `ModuleNotFoundError`.
* Database tables created and test fixtures initialized.

#### 6.2 Exit Criteria
* All critical and high-severity defects resolved and verified.
* 100% of smoke, unit, integration, and regression tests passing.
* Test execution reports and code coverage generated in `/reports/`.
* Formal defect register documented with before/after test evidence.

---

### 7. Deliverables
1. **Master Test Plan (`test_plan.md`)**
2. **Comprehensive Test Cases (`test_cases.csv`)**
3. **Defect Register & Bug Life Cycle Log (`defect_register.csv`)**
4. **Pytest Test Suites (`tests/unit/`, `tests/integration/`, `tests/e2e/`, `tests/regression/`)**
5. **Interactive HTML Test Execution Report (`reports/test_report.html`)**
6. **Code Coverage Report (`reports/coverage/`)**
