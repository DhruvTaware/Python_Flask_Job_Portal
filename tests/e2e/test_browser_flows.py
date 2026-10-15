import os
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from app import app, db as _db
from app.models import Application


@pytest.mark.e2e
class TestSeleniumBrowserFlows:
    """End-to-End browser automation tests using Selenium WebDriver."""

    def test_public_job_board_loads_successfully(self, browser, live_server):
        """Verify the public job board displays the branding and seeded job listings."""
        browser.get(f"{live_server['base_url']}/")

        # Wait for page title and header
        WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.XPATH, "//a[contains(@class, 'navbar-brand')]"))
        )
        assert "Job Portal" in browser.title

        # Verify navigation buttons
        login_btn = browser.find_element(By.XPATH, "//a[@href='/login']")
        signup_btn = browser.find_element(By.XPATH, "//a[@href='/register']")
        assert login_btn.is_displayed()
        assert signup_btn.is_displayed()

        # Verify seeded job title is displayed
        job_card = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.XPATH, f"//*[contains(text(), '{live_server['job_title']}')]"))
        )
        assert job_card.is_displayed()

    def test_valid_applicant_login(self, browser, live_server):
        """Verify an applicant can successfully log in and is redirected to show_jobs."""
        browser.get(f"{live_server['base_url']}/login")

        # Wait for login form
        email_input = WebDriverWait(browser, 10).until(
            EC.visibility_of_element_located((By.ID, "email"))
        )

        # Select Job Seeker role
        usertype_select = Select(browser.find_element(By.ID, "usertype"))
        usertype_select.select_by_value("Job Seeker")

        # Fill credentials
        email_input.clear()
        email_input.send_keys(live_server['seeker_email'])

        pwd_input = browser.find_element(By.ID, "password")
        pwd_input.clear()
        pwd_input.send_keys(live_server['raw_password'])

        # Submit login form
        submit_btn = browser.find_element(By.ID, "submit")
        submit_btn.click()

        # Verify redirect to show_jobs
        WebDriverWait(browser, 10).until(
            lambda d: "/show_jobs" in d.current_url or d.current_url.endswith("/")
        )

        # Verify authenticated state: 'Log out' button is visible
        logout_btn = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.XPATH, "//a[@href='/logout']"))
        )
        assert logout_btn.is_displayed()

    def test_invalid_login_shows_error(self, browser, live_server):
        """Verify submitting invalid credentials displays danger alert feedback."""
        browser.get(f"{live_server['base_url']}/login")

        email_input = WebDriverWait(browser, 10).until(
            EC.visibility_of_element_located((By.ID, "email"))
        )

        usertype_select = Select(browser.find_element(By.ID, "usertype"))
        usertype_select.select_by_value("Job Seeker")

        email_input.clear()
        email_input.send_keys(live_server['seeker_email'])

        pwd_input = browser.find_element(By.ID, "password")
        pwd_input.clear()
        pwd_input.send_keys("WrongPassword999!")

        submit_btn = browser.find_element(By.ID, "submit")
        submit_btn.click()

        # Wait for danger flash message
        alert = WebDriverWait(browser, 10).until(
            EC.visibility_of_element_located((By.CLASS_NAME, "alert-danger"))
        )
        assert "Login Unsuccessful. Please check email, password and usertype" in alert.text

        # Verify user remains on login page
        assert "/login" in browser.current_url

    def test_unauthenticated_access_to_protected_page_redirects(self, browser, live_server):
        """Verify accessing a protected page while logged out redirects to login."""
        browser.get(f"{live_server['base_url']}/post_jobs")

        # Should be redirected to /login with next parameter
        WebDriverWait(browser, 10).until(
            lambda d: "/login" in d.current_url
        )

        # Confirm login input elements are displayed
        email_input = WebDriverWait(browser, 10).until(
            EC.visibility_of_element_located((By.ID, "email"))
        )
        assert email_input.is_displayed()

    def test_job_application_submission_with_valid_resume(self, browser, live_server):
        """
        Verify end-to-end job application submission with an uploaded resume file:
        1. Log in as job seeker.
        2. Navigate to application form.
        3. Fill form and attach a valid PNG resume image.
        4. Submit and verify success confirmation and DB persistence.
        """
        # Step 1: Create a test resume image
        temp_resume_path = os.path.join(r"E:\temp", "selenium_test_resume.png")
        # Minimal valid 1x1 PNG image bytes
        png_bytes = (
            b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01'
            b'\x08\x06\x00\x00\x00\x1f\x15c4\x00\x00\x00\rIDATx\x9cc\xf8\xff\x9f'
            b'\x81\x00\x03\x01\x01\x00\x18\xdd\x8d\xb0\x00\x00\x00\x00IEND\xaeB`\x82'
        )
        with open(temp_resume_path, "wb") as f:
            f.write(png_bytes)

        try:
            # Step 2: Log in as job seeker
            browser.get(f"{live_server['base_url']}/login")
            email_input = WebDriverWait(browser, 10).until(
                EC.visibility_of_element_located((By.ID, "email"))
            )
            Select(browser.find_element(By.ID, "usertype")).select_by_value("Job Seeker")
            email_input.send_keys(live_server['seeker_email'])
            browser.find_element(By.ID, "password").send_keys(live_server['raw_password'])
            browser.find_element(By.ID, "submit").click()

            WebDriverWait(browser, 10).until(
                lambda d: "/show_jobs" in d.current_url or d.current_url.endswith("/")
            )

            # Step 3: Navigate to post_cvs for the seeded job
            browser.get(f"{live_server['base_url']}/post_cvs/{live_server['job_id']}")

            # Wait for application form elements
            exp_input = WebDriverWait(browser, 10).until(
                EC.visibility_of_element_located((By.ID, "experience"))
            )

            # Step 4: Fill form fields
            Select(browser.find_element(By.ID, "gender")).select_by_value("Female")
            Select(browser.find_element(By.ID, "degree")).select_by_value("cBachelor")
            Select(browser.find_element(By.ID, "industry")).select_by_value("Computer And Technology")

            exp_input.clear()
            exp_input.send_keys("4")

            cover_letter = browser.find_element(By.ID, "cover_letter")
            cover_letter.clear()
            cover_letter.send_keys("Submitting application via automated Selenium E2E suite.")

            # Attach resume file
            cv_upload = browser.find_element(By.ID, "cv")
            cv_upload.send_keys(temp_resume_path)

            # Step 5: Submit application
            submit_btn = browser.find_element(By.ID, "submit")
            browser.execute_script("arguments[0].scrollIntoView({block: 'center'});", submit_btn)
            try:
                submit_btn.click()
            except Exception:
                browser.execute_script("arguments[0].click();", submit_btn)

            # Step 6: Verify redirect and success flash message
            WebDriverWait(browser, 10).until(
                lambda d: "/show_jobs" in d.current_url or d.current_url.endswith("/")
            )

            success_alert = WebDriverWait(browser, 10).until(
                EC.visibility_of_element_located((By.CLASS_NAME, "alert-success"))
            )
            assert "Your application has been submitted successfully!" in success_alert.text

            # Step 7: Verify database persistence in isolated test DB
            with app.app_context():
                saved_app = Application.query.filter_by(job_id=live_server['job_id']).first()
                assert saved_app is not None
                assert saved_app.experience == 4
                assert saved_app.degree == 'cBachelor'
                assert saved_app.cv.endswith('.png')

        finally:
            if os.path.exists(temp_resume_path):
                try:
                    os.remove(temp_resume_path)
                except OSError:
                    pass
