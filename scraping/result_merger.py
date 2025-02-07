import glob
import os
from bs4 import BeautifulSoup
import re
import json


def merge_wellfound_company_files():
    input_pattern = os.path.join("output", "company_links", "wellfound_companies*")
    merged_file_path = os.path.join("output", "company_links.txt")
    companies = set()

    for file_path in glob.glob(input_pattern):
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                company = line.strip()
                if company:
                    companies.add(company)

    with open(merged_file_path, "w", encoding="utf-8") as out:
        for company in sorted(companies):
            out.write(company + "\n")


def remove_double_slash():
    with open("output/company_links.txt", "r", encoding="utf-8") as file:
        company_links = file.read().splitlines()

    with open("output/company_links.txt", "w", encoding="utf-8") as file:
        for link in company_links:
            file.write(link.replace(".com//", ".com/") + "\n")


def extract_data_from_raw_html():
    """
    Extracts data from html files into json files.
    """
    output_dir = os.path.join("output", "company_pages_csv")
    os.makedirs(output_dir, exist_ok=True)

    with open("output/scraped_companies.txt", "r", encoding="utf-8") as file:
        company_links = file.read().splitlines()
    companies = [company_link.split("/")[-1] for company_link in company_links]
    data_dict = {}

    companies_counter = 0

    for company in companies:
        if company in {
            "skm-group-2",
            "tech2i",
            "honeycomb-software-2",
            "flavorapp",
            "mixrank",
        }:
            print(f"Company {company}, bad data, skipping")
            companies_counter += 1
            continue

        print(f"Extracting data from company {company}")
        input_pattern = os.path.join("output", "raw_company_data", f"{company}.html")
        if os.path.exists(input_pattern):
            base_data = extract_data_from_base_html(input_pattern)

        input_pattern = os.path.join(
            "output", "raw_company_data", f"{company}_funding.html"
        )
        if os.path.exists(input_pattern):
            funding_data = extract_data_from_funding_html(input_pattern)
        else:
            funding_data = extract_data_from_funding_html(
                "output/raw_company_data/empty_data.html"
            )

        input_pattern = os.path.join(
            "output", "raw_company_data", f"{company}_culture_and_benefits.html"
        )
        if os.path.exists(input_pattern):
            culture_data = extract_data_from_culture_html(input_pattern)
        else:
            culture_data = extract_data_from_culture_html(
                "output/raw_company_data/empty_data.html"
            )

        data_dict[company] = {**base_data, **funding_data, **culture_data}
        companies_counter += 1
        print(
            f"Company {company} data extracted, {companies_counter}/{len(companies)}\n"
        )
    return data_dict


def extract_data_from_base_html(html_file):
    """
    Extract data from basic html file into dict containing:
    - id
        - Extracted from link
    - name
    - slogan

    Everything after here is extracted from div with class "styles_main__*"
    - description
        - div with class "styles_overview*"

    Everything after here is extracted from the only dl in the file
    - locations (list)
    - size (num of employees)
    - total_funding
    - type
    - industries (list)
    """
    with open(html_file, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")

    data = {}
    data["id"] = html_file.split("/")[-1].split(".")[0]
    data["name"] = soup.find("span", class_="inline text-md font-semibold").get_text(
        strip=True
    )
    try:
        data["slogan"] = soup.find("span", class_="text-md text-neutral-1000").get_text(
            strip=True
        )
    except:
        data["slogan"] = None
        print(f"Company {data['id']} has no slogan")

    try:
        data["description"] = (
            soup.find("div", class_=re.compile(r"^styles_main__"))
            .find("div", class_=re.compile(r"^styles_overview"))
            .find("div", class_=re.compile(r"^styles_description"))
            .get_text(strip=True)
        )
    except:
        data["description"] = None
        print(f"Company {data['id']} has no description")

    dl = soup.find("dl")
    data["locations"] = []
    data["size"] = None
    data["total_funding"] = None
    data["type"] = []
    data["industries"] = []

    if dl:
        for dt, dd in zip(dl.find_all("dt"), dl.find_all("dd")):
            key = dd.get_text(strip=True).lower()
            val = dt.get_text(strip=True)
            if "location" in key:
                data["locations"].extend(
                    li.get_text(strip=True) for li in dt.find_all("li")
                )
            elif "size" in key:
                data["size"] = val
            elif "total raised" in key:
                data["total_funding"] = transform_money(val)
            elif "type" in key:
                data["type"].extend(
                    sp.get_text(strip=True)
                    for sp in dt.find_all("span")
                    if sp.get_text(strip=True)
                )
            elif "markets" in key:
                data["industries"].extend(
                    sp.get_text(strip=True)
                    for sp in dt.find_all("span")
                    if sp.get_text(strip=True)
                )

    return data


def extract_data_from_funding_html(html_file):
    """
    Extract data from funding html file into dict containing:

    Each extracted from a div with class "styles_statement*", differentiated because the div contains two spans, one with the key and one with the value
    - valuation
    - num of funding rounds

    - funding_rounds (list)
        - each funding round found in a div with class "styles_round_*"
        - Each funding round is a dict containing:
            - amount
                - in a span with class "styles_amountRaised_*"
            each of the following is inside a div with class "styles_metadata_*", each one is represented by a span, we can differentiate them by the order the spans appear
            - type
            - date
            - valuation (if available)
    """

    def transfomorm_date(date):
        """
        Date is recieved as a string "month year", we want to transform it to a numerical format
        """
        months = {
            "Jan": "01",
            "Feb": "02",
            "Mar": "03",
            "Apr": "04",
            "May": "05",
            "Jun": "06",
            "Jul": "07",
            "Aug": "08",
            "Sep": "09",
            "Oct": "10",
            "Nov": "11",
            "Dec": "12",
        }
        try:
            month, year = date.split()
        except:
            return None
        return f"{year}.{months.get(month, '00')}"

    with open(html_file, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")

    data = {"valuation": None, "num_of_funding_rounds": None, "funding_rounds": []}
    for i, statement in enumerate(
        soup.find_all("div", class_=re.compile(r"^styles_statement"))
    ):
        span = statement.find("span", class_=re.compile(r"^styles_value_"))
        if i == 0:
            data["valuation"] = transform_money(span.get_text(strip=True))
        elif i == 1:
            try:
                data["num_of_funding_rounds"] = (
                    span.find("span", class_=re.compile(r"^styles_desktop_"))
                    .get_text(strip=True)
                    .split()[0]
                )
            except:
                data["num_of_funding_rounds"] = None
                print(
                    f"Company {html_file.split('/')[-1].split('.')[0]} has no funding rounds"
                )

    for round_div in soup.find_all("div", class_=re.compile(r"^styles_round_")):
        round_info = {}
        amount_span = round_div.find(
            "span", class_=re.compile(r"^styles_amountRaised_")
        )
        round_info["amount"] = (
            transform_money(amount_span.get_text(strip=True)) if amount_span else ""
        )
        metadata = round_div.find("div", class_=re.compile(r"^styles_metadata_"))
        if metadata:
            meta_spans = metadata.find_all("span")
            round_info["type"] = (
                meta_spans[0].get_text(strip=True) if len(meta_spans) > 0 else ""
            )
            round_info["date"] = transfomorm_date(
                meta_spans[1].get_text(strip=True) if len(meta_spans) > 1 else ""
            )
            round_info["valuation"] = transform_money(
                meta_spans[2].get_text(strip=True).replace("valuation", "")
                if len(meta_spans) > 2
                else ""
            )
        data["funding_rounds"].append(round_info)

    return data


def extract_data_from_culture_html(html_file):
    """
    Extract data from culture html file into dict containing:

    All the following is extracted from div with class "flex flex-col gap-8"
    - benefits_overview
        - div with class "styles_statement*"
    - benefits (list)
        - benefits are located in a div with class "styles_twoColumn*"
        - each benefit is a div with class "styles_body*"
        - each benefit has a header "h4" and a description "p", concatenate them to get the benefit
    """
    with open(html_file, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")

    data = {"benefits_overview": None, "benefits": []}

    main_div = soup.find("div", class_="flex flex-col gap-8")
    if main_div:
        overview_div = main_div.find("div", class_=re.compile(r"^styles_statement"))
        if overview_div:
            data["benefits_overview"] = overview_div.get_text(strip=True)

        two_col_div = main_div.find("div", class_=re.compile(r"^styles_twoColumn"))
        if two_col_div:
            for benefit_div in two_col_div.find_all(
                "div", class_=re.compile(r"^styles_body")
            ):
                title_node = benefit_div.find("h4")
                desc_node = benefit_div.find("p")
                title_text = title_node.get_text(strip=True) if title_node else ""
                desc_text = desc_node.get_text(strip=True) if desc_node else ""
                data["benefits"].append(f"{title_text}: {desc_text}")

    return data


def transform_money(valuation):
    valuation = valuation.replace(",", "").replace("$", "")
    try:
        if valuation.endswith("B"):
            return str(float(valuation[:-1]) * 1e9)
        elif valuation.endswith("M"):
            return str(float(valuation[:-1]) * 1e6)
        elif valuation.endswith("K"):
            return str(float(valuation[:-1]) * 1e3)
        else:
            return str(float(valuation))
    except ValueError:
        return None


def pretty_dict_print(data):
    for key, val in data.items():
        print(f"{key}:")
        if isinstance(val, dict):
            pretty_dict_print(val)
        elif isinstance(val, list):
            for i, item in enumerate(val):
                print(f"\t{i + 1}:")
                if isinstance(item, dict):
                    pretty_dict_print(item)
                else:
                    print(f"\t\t{item}")
        else:
            print(f"\t{val}")


if __name__ == "__main__":
    output_json_path = os.path.join("output/company_pages_json", "company_data.json")

    with open(output_json_path, "w", encoding="utf-8") as json_file:
        data = extract_data_from_raw_html()
        json.dump(data, json_file, indent=4)
