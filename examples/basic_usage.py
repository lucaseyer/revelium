"""Basic Revelium usage example."""

from selenium import webdriver
from selenium.webdriver.common.by import By

from revelium import ReveliumConfig, ReveliumDriver


def main() -> None:
    driver = webdriver.Chrome()
    rv = ReveliumDriver(
        driver,
        ReveliumConfig(report_dir="revelium_reports", save_dom_on_failure=True),
    )

    driver.get("https://example.com")
    rv.click(By.ID, "submit-login", hint="login button")


if __name__ == "__main__":
    main()
