#!/usr/bin/env python3
from os import environ
from selenium.webdriver import Remote, ChromeOptions as Options
from selenium.webdriver.chromium.remote_connection import (
    ChromiumRemoteConnection as Connection,
)
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
import os

AUTH = "brd-customer-hl_80709a30-zone-scraping_browser_ek01:syrhqte1x8er"
TARGET_URL = environ.get("TARGET_URL", default="https://wellfound.com/startups")


def scrape(url=TARGET_URL):
    if AUTH == "USER:PASS":
        raise Exception(
            "Provide Scraping Browsers credentials in AUTH "
            + "environment variable or update the script."
        )
    print("Connecting to Browser...")
    server_addr = f"https://{AUTH}@brd.superproxy.io:9515"
    connection = Connection(server_addr, "goog", "chrome")

    # Set Chrome options to disable loading images
    chrome_options = Options()
    prefs = {"profile.managed_default_content_settings.images": 2}
    chrome_options.add_experimental_option("prefs", prefs)

    driver = Remote(connection, options=Options())
    try:
        print(f"Connected! Navigating to {url}...")
        driver.get(url)
        print("Navigated! Waiting captcha to detect and solve...")
        result = driver.execute(
            "executeCdpCommand",
            {
                "cmd": "Captcha.waitForSolve",
                "params": {"detectTimeout": 10 * 1000},
            },
        )
        status = result["value"]["status"]
        print(f"Captcha status: {status}")

        print("Getting page source...")
        html_source = driver.page_source
        print("Page source obtained!")
        return html_source
    finally:
        driver.quit()


def get_wellfound_comapny_links(html_source):
    """
    Get link to pages of companies listed on this page on wellfound.com
    """
    print("Getting links to company pages...")
    print("Parsing HTML...")
    soup = BeautifulSoup(html_source, "html.parser")
    links = []
    print("Extracting links...")
    for a in soup.find_all("a", class_="content-center", href=True):
        if a["href"].startswith("/company/"):
            links.append(f"https://wellfound.com/" + a["href"] + "\n")
    print("Links extracted!")
    return links


def write_output_file(name, data, subfolder=None):
    """
    Write data to a file in the output folder, possibly in a subfolder
    """
    folder = "output" if subfolder is None else f"output/{subfolder}"
    with open(f"{folder}/{name}", "w", encoding="utf-8") as file:
        file.write(data)


def wellfound_company_links_scraping():
    base_url = "https://wellfound.com/startups"
    errored_pages = []

    print("Scraping wellfound.com/startups...")
    for i in [
        31,
        86,
        107,
        132,
        278,
        290,
        302,
        316,
        320,
        355,
        370,
        391,
        394,
        415,
        423,
        431,
        449,
        486,
        487,
        518,
        521,
        584,
        598,
        613,
    ]:
        try:
            print(f"Page {i}")
            html_source = scrape(base_url + f"?page={i}")
            links = get_wellfound_comapny_links(html_source)
            write_output_file(
                f"wellfound_companies_{i}.txt", "".join(links), "company_links"
            )
            print(f"Page {i} scraped!\n")
        except Exception as e:
            print(f"Error on page {i}: {e}\n")
            errored_pages.append(i)
            continue

    print("Scraping completed!")
    if errored_pages:
        print(f"Errored pages: {errored_pages}")
        write_output_file(
            "errored_pages.txt", "\n".join(map(str, errored_pages)), "company_links"
        )
    else:
        print("No errors occurred!")


def navigation_based_scraping(url=TARGET_URL):
    if AUTH == "USER:PASS":
        raise Exception(
            "Provide Scraping Browsers credentials in AUTH "
            + "environment variable or update the script."
        )
    print("Connecting to Browser...")
    server_addr = f"https://{AUTH}@brd.superproxy.io:9515"
    connection = Connection(server_addr, "goog", "chrome")

    # Set Chrome options to disable loading images
    chrome_options = Options()
    prefs = {"profile.managed_default_content_settings.images": 2}
    chrome_options.add_experimental_option("prefs", prefs)

    driver = Remote(connection, options=Options())
    try:
        print(f"Connected! Navigating to {url}...")
        driver.get(url)
        print("Navigated! Waiting captcha to detect and solve...")
        result = driver.execute(
            "executeCdpCommand",
            {
                "cmd": "Captcha.waitForSolve",
                "params": {"detectTimeout": 2 * 1000},
            },
        )
        status = result["value"]["status"]
        print(f"Captcha status: {status}")
        return driver
    except:
        driver.quit()
        raise


def get_page(driver, url):
    """
    Get the page source of the given url, solving any captcha if necessary
    """
    print(f"Navigating to {url}...")
    try:
        driver.get(url)
    except:
        print("\nReloading session...")
        driver = navigation_based_scraping(url)
        driver.get(url)
        print(f"Reloading session successful! Navigating to {url}...")
    print("Navigated! Waiting captcha to detect and solve...")
    result = driver.execute(
        "executeCdpCommand",
        {
            "cmd": "Captcha.waitForSolve",
            "params": {"detectTimeout": 3 * 1000},
        },
    )
    status = result["value"]["status"]
    print(f"Captcha status: {status}")
    return (driver, status)


def scrape_all_startup_data():
    """
    Scrape all startup data from all pages of wellfound.com/startups
    """
    driver = navigation_based_scraping("https://wellfound.com/startups")
    # Read the list of company links from the output files
    company_links = []
    for filename in os.listdir("output/company_links"):
        if filename.startswith("wellfound_companies_") and filename.endswith(".txt"):
            with open(
                f"output/company_links/{filename}", "r", encoding="utf-8"
            ) as file:
                company_links.extend(file.readlines())

    # Read the list of already scraped companies
    scraped_companies = set()
    with open("output/scraped_companies.txt", "r", encoding="utf-8") as file:
        scraped_companies.update(file.read().splitlines())

    # Filter out already scraped companies
    companies_to_scrape = [
        link.strip() for link in company_links if link.strip() not in scraped_companies
    ]

    print(f"Scraping data for {len(companies_to_scrape)} companies...")
    scraped_counter = 0

    # Scrape data for each company
    for company_url in companies_to_scrape:
        try:
            print(f"Scraping data for {company_url}...")
            response = get_page(driver, company_url)
            driver = response[0]
            status = response[1]
            if status == "solve_failed":
                print("Captcha failed!")
                continue

            html_source = driver.page_source

            # check for and save the contents of subpages
            soup = BeautifulSoup(html_source, "html.parser")
            culture_and_benefits_link = soup.find(
                "a", href=f"/company/{company_url.split('/')[-1]}/culture_and_benefits"
            )
            funding_link = soup.find(
                "a", href=f"/company/{company_url.split('/')[-1]}/funding"
            )
            if culture_and_benefits_link:
                print(f"Scraping culture and benefits page for {company_url}...")
                result = get_page(
                    driver, f"https://wellfound.com{culture_and_benefits_link['href']}"
                )
                driver = result[0]
                status = result[1]
                if status == "solve_failed":
                    print("Captcha failed!\n")
                    continue
                culture_and_benefits_html = driver.page_source
                write_output_file(
                    f"{company_url.split('/')[-1]}_culture_and_benefits.html",
                    culture_and_benefits_html,
                    "raw_company_data",
                )
                print(
                    f"Culture and benefits page for {company_url} scraped successfully!\n"
                )

            if funding_link:
                print(f"Scraping funding page for {company_url}...")
                result = get_page(
                    driver, f"https://wellfound.com{funding_link['href']}"
                )
                driver = result[0]
                status = result[1]
                if status == "solve_failed":
                    print("Captcha failed!\n")
                    continue
                funding_html = driver.page_source
                write_output_file(
                    f"{company_url.split('/')[-1]}_funding.html",
                    funding_html,
                    "raw_company_data",
                )
                print(f"Funding page for {company_url} scraped successfully!\n")

            # Save the scraped data
            write_output_file(
                f"{company_url.split('/')[-1]}.html", html_source, "raw_company_data"
            )
            # Add the company to the list of scraped companies
            scraped_companies.add(company_url)
            with open("output/scraped_companies.txt", "a", encoding="utf-8") as file:
                file.write(company_url + "\n")
            scraped_counter += 1
            print(
                f"Data for {company_url} scraped successfully! remaining {len(companies_to_scrape)-scraped_counter}\n"
            )
        except Exception as e:
            print(f"Error scraping data for {company_url}: {e}\n")
            continue

    driver.quit()
    print("All company data scraped!")


if __name__ == "__main__":
    print("Starting scraping...")
    scrape_all_startup_data()
