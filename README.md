# Python_Flask_Job_Portal
Job Portal Web App with Flask Python

Python 3.9

## Local Environment

### Install

1- Create a virtual environment


```virtualenv venv```

or 

```python -m venv venv```

2- Activate it

```source venv/Scripts/activate``` (Windows)

```source venv/bin/activate``` (Linux)

3- Clone the repository and install the packages in the virtual env:

```pip install -r requirements.txt```

4- Run application

```python run.py```

---

## Software Testing and Quality Assurance (STQA)

This project has been verified and hardened through a comprehensive STQA engineering process:
- **117 Automated Tests**: 10 Smoke, 57 Unit, 45 Integration, and 5 Selenium E2E Tests (100% Pass Rate).
- **91% Application Statement Coverage**: 100% on `models.py`, `forms.py`, and `__init__.py`.
- **Zero Production Database Mutation**: All automated tests run against temporary, isolated SQLite databases. `app/site.db` remains 100% pristine.

### Running Automated Tests

```powershell
# Run the complete test suite with interactive HTML report
.\venv\Scripts\pytest.exe -v tests/ --html=reports/test_report.html --self-contained-html

# Run specific test tiers
.\venv\Scripts\pytest.exe -v tests/test_smoke.py      # Smoke tests
.\venv\Scripts\pytest.exe -v tests/unit/             # Unit tests (models & forms)
.\venv\Scripts\pytest.exe -v tests/integration/      # Integration & RBAC tests
.\venv\Scripts\pytest.exe -v tests/e2e/              # Headless Selenium E2E tests

# Generate test coverage report
.\venv\Scripts\coverage.exe run -m pytest tests/
.\venv\Scripts\coverage.exe report -m --include="app/*"
.\venv\Scripts\coverage.exe html -d reports/coverage --include="app/*"
```

### STQA Academic Documentation & Deliverables

- **Master Test Plan**: [`test_documents/test_plan.md`](test_documents/test_plan.md) (IEEE 829-aligned)
- **Traceable Test Cases**: [`test_documents/test_cases.csv`](test_documents/test_cases.csv) (83 formal specifications)
- **Defect Register & Log**: [`test_documents/defect_register.csv`](test_documents/defect_register.csv) (DEF-001 through DEF-008 history)
- **Academic Project Report**: [`test_documents/academic_project_report.md`](test_documents/academic_project_report.md)
- **Demonstration Guide**: [`test_documents/demonstration_guide.md`](test_documents/demonstration_guide.md)
- **Interactive HTML Test Report**: [`reports/test_report.html`](reports/test_report.html)
- **Interactive Coverage Report**: [`reports/coverage/index.html`](reports/coverage/index.html)

---

# Screenshots

### Home
![alt text](https://github.com/hamziqureshi/Python_Flask_Job_Portal/blob/master/Screenshots/home_before_login_jobseeker.png)


## Sign up
You can either sign up as company or a person who is looking for a job
![alt text](https://github.com/hamziqureshi/Python_Flask_Job_Portal/blob/master/Screenshots/sign_up.png)

## Login
You can either log in as company or a person who is looking for a job
![alt text](https://github.com/hamziqureshi/Python_Flask_Job_Portal/blob/master/Screenshots/login.png)

## Home after a job seeker logs in
![alt text](https://github.com/hamziqureshi/Python_Flask_Job_Portal/blob/master/Screenshots/home_after_login_jobseeker.png)

## Applying for a job
![alt text](https://github.com/hamziqureshi/Python_Flask_Job_Portal/blob/master/Screenshots/application.png)

## Post a review about website
![alt text](https://github.com/hamziqureshi/Python_Flask_Job_Portal/blob/master/Screenshots/post_review.png)

## Home after you log in as a company
The company will only see those jobs which they have posted. 
![alt text](https://github.com/hamziqureshi/Python_Flask_Job_Portal/blob/master/Screenshots/home_for_company_after_login.png)

## See as a company who has applied on you posted job
Only those who have applied on your specific posted jobs will be seen here
![alt text](https://github.com/hamziqureshi/Python_Flask_Job_Portal/blob/master/Screenshots/see_applicants.png)

## See resume of selected applicant
![alt text](https://github.com/hamziqureshi/Python_Flask_Job_Portal/blob/master/Screenshots/see_resume_of_applicants.png)

## Start interview with the applicant.
This webpage is under working in which company can have interview with the applicant on this same website.
![alt text](https://github.com/hamziqureshi/Python_Flask_Job_Portal/blob/master/Screenshots/start_interview.png)
