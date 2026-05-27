import requests
from bs4 import BeautifulSoup
import subprocess
import os


def clear():
    command = "cls" if os.name == "nt" else "clear"
    subprocess.run([command], shell=True)


clear()
# print(f"\033[48;2;40;40;40m")

RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
MAGENTA = "\033[35m"
CYAN = "\033[36m"
WHITE = "\033[37m"

RESET = "\033[0m"
BOLD = "\033[1m"
UNDERLINE = "\033[4m"

print(
    "██╗   ██╗███████╗ ██████╗██╗███████╗    ██████╗  █████╗ ████████╗ █████╗     \n"
    "██║   ██║██╔════╝██╔════╝██║██╔════╝    ██╔══██╗██╔══██╗╚══██╔══╝██╔══██╗    \n"
    "██║   ██║███████╗██║     ██║███████╗    ██║  ██║███████║   ██║   ███████║    \n"
    "██║   ██║╚════██║██║     ██║╚════██║    ██║  ██║██╔══██║   ██║   ██╔══██║    \n"
    "╚██████╔╝███████║╚██████╗██║███████║    ██████╔╝██║  ██║   ██║   ██║  ██║    \n"
    " ╚═════╝ ╚══════╝ ╚═════╝╚═╝╚══════╝    ╚═════╝ ╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝    \n"
    "██████╗ ██╗██████╗ ███████╗██╗     ██╗███╗   ██╗███████╗                     \n"
    "██╔══██╗██║██╔══██╗██╔════╝██║     ██║████╗  ██║██╔════╝                     \n"
    "██████╔╝██║██████╔╝█████╗  ██║     ██║██╔██╗ ██║█████╗                       \n"
    "██╔═══╝ ██║██╔═══╝ ██╔══╝  ██║     ██║██║╚██╗██║██╔══╝                       \n"
    "██║     ██║██║     ███████╗███████╗██║██║ ╚████║███████╗                     \n"
    "╚═╝     ╚═╝╚═╝     ╚══════╝╚══════╝╚═╝╚═╝  ╚═══╝╚══════╝                     \n"
    f"{RED}██{YELLOW}██{GREEN}██{CYAN}██{BLUE}██{MAGENTA}██{WHITE}██{RESET}\n"
)

url = "https://travel.state.gov/content/travel/en/legal/visa-law0/visa-bulletin.html"

try:
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

    print(f"{MAGENTA}[*] Connecting to primary State Department directory...{RESET}")
    response = requests.get(url, headers=headers, timeout=10)

    print(f"Status Code: {response.status_code}")

    if response.status_code == 200:
        print(f"{GREEN}[+] Success! Connected to State Dept.{RESET}\n")

        print(
            f"{CYAN}[*] Scanning hyperlinks for the latest monthly publication link...{RESET}"
        )
        soup = BeautifulSoup(response.text, "html.parser")
        list_tag = soup.find_all("a")

        latest_bulletin_url = (
            f"{YELLOW}[!] Warning: Target bulletin link could not be isolated.{RESET}"
        )

        for tag in list_tag:
            text = tag.get_text()
            if "Visa Bulletin For" in text:
                value = tag.get("href")

                if value:
                    if value.startswith("/content"):
                        latest_bulletin_url = "https://travel.state.gov" + value
                        break
                    elif value.startswith("http"):
                        latest_bulletin_url = value
                        break

        print(f"{GREEN}[+] Targeting live URL:{RESET} {latest_bulletin_url}\n")

        if latest_bulletin_url.startswith("http"):
            print(
                f"{BLUE}[*] Requesting payload content from target monthly bulletin...{RESET}"
            )
            inner_response = requests.get(
                latest_bulletin_url, headers=headers, timeout=10
            )

            print(f"Status Code: {inner_response.status_code}")

            if inner_response.status_code == 200:
                print(
                    f"{GREEN}[+] Success! Content fetched from target inner page.{RESET}\n"
                )
                print(
                    f"{CYAN}[*] Querying DOM structures for Employment-Based priority tables...{RESET}"
                )
                inner_soup = BeautifulSoup(inner_response.text, "html.parser")
                all_tables = inner_soup.find_all("table")
                target_table = None

                for table in all_tables:
                    table_text = table.get_text().upper()
                    if (
                        "EMPLOYMENT" in table_text
                        and "1ST" in table_text
                        and "2ND" in table_text
                    ):
                        target_table = table
                        break

                if target_table:
                    print(
                        f"{GREEN}[+] Priority metrics isolated. Generating data grid layout:{RESET}\n"
                    )

                    rows_pool = []
                    max_columns_count = 0

                    for row in target_table.find_all("tr"):
                        columns = row.find_all(["td", "th"])

                        row_data = []
                        for col in columns:
                            text_chunk = col.get_text().replace("\n", " ").strip()
                            text_chunk = " ".join(text_chunk.split())
                            text_chunk = text_chunk.replace(
                                "All Chargeability Areas Except Those Listed",
                                "All Chargeability",
                            )
                            text_chunk = text_chunk.replace(
                                "CHINA- mainland born", "CHINA"
                            )
                            row_data.append(text_chunk)

                        if any(row_data):
                            if len(row_data) == 1 and (
                                "EXCEPT" in row_data[0].upper()
                                or "NUMBERS" in row_data[0].upper()
                            ):
                                continue
                            rows_pool.append(row_data)
                            if len(row_data) > max_columns_count:
                                max_columns_count = len(row_data)

                    for row_data in rows_pool:
                        if len(row_data) < max_columns_count and len(row_data) <= 2:
                            banner_text = " - ".join(row_data)
                            print(f"{YELLOW}{BOLD}{banner_text}{RESET}")
                            print("-" * 115)
                        else:
                            if len(row_data) == max_columns_count - 1:
                                row_data.insert(4, row_data[3])

                            formatted_cells = []
                            for idx, item in enumerate(row_data):
                                if idx == 0:
                                    formatted_cells.append(f"{item[:38]:<38}")
                                else:
                                    formatted_cells.append(f"{item[:14]:^14}")

                            while len(formatted_cells) < max_columns_count:
                                formatted_cells.append(f"{'-':^14}")

                            formatted_row = " | ".join(formatted_cells)
                            print(formatted_row)

                    print(f"\n{MAGENTA}[+] Script execution complete.{RESET}")
                    input(f"\n{BOLD}Press {BLUE}[Enter]{RESET} to {RED}exit{RESET}")
                else:
                    print(
                        f"\n{YELLOW}[!] Target table missing from page structural layout.{RESET}"
                    )
            else:
                print(
                    f"\n{RED}[-] Failed to download inner page. Status Code: {inner_response.status_code}{RESET}"
                )

    else:
        print(f"\n{RED}[-] Failed. Status Code: {response.status_code}{RESET}")

except requests.exceptions.RequestException as error_message:
    print(f"\n{RED}[-] Critical Connection Error: {error_message}{RESET}")
