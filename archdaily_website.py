import json
import requests
from bs4 import BeautifulSoup


def get_page_content(url: str, headers: dict) -> BeautifulSoup:
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        html_content = response.text
        soup = BeautifulSoup(html_content, 'html.parser')
        return soup


def get_project_data(url: str, start_page: int, pages_checked: int, all_results, headers: dict) -> None:
    page = start_page

    while page <= pages_checked:
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            data = response.json()
            results = data.get('results')

            for result in results:
                project_data = {
                    "title": result["parent_info"]["title"],
                    "publication_date": None,
                    "url_project": result["parent_info"]["url"],
                    "project_images": [],
                }

                project_url = result["parent_info"]["url"]
                project_data["project_images"] = get_project_images(project_url, headers)
                project_data["publication_date"] = get_publication_date(project_url, headers)

                all_results.append(project_data)
            print(f"Обработана страница {page}")
            page += 1
            url = f'{headers["base_url"]}/search/api/v1/us/images?page={page}'
        else:
            print(f"Не удалось получить данные для страницы {page}. Код Статуса: {response.status_code}")
            break


def get_project_images(url: str, headers: dict) -> list[str] | list:
    soup = get_page_content(url, headers)

    if soup:
        elements = soup.find_all("a", class_="gallery-thumbs-link")
        return [headers['base_url'] + element['href'] for element in elements]

    return []


def get_publication_date(url: str, headers: dict) -> str | None:
    soup = get_page_content(url, headers)

    if soup:
        date_element = soup.find("span", class_="date-publication")
        if date_element:
            publication_date = date_element.find("time")["datetime"]
            publication_date = publication_date.split("T")[0]
            return publication_date

    return None


def save_to_json(filename: str, data: list) -> None:
    with open(filename, 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=4)


def main() -> None:
    start_page = 1
    number_pages_checked = 3
    all_results = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0',
        'Accept': '*/*',
        'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
        'Accept-Encoding': 'gzip, deflate, br',
        'Referer': 'https://www.archdaily.com/search/images?ad_source=jv-header&ad_name=main-menu',
        'Connection': 'keep-alive',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'If-None-Match': 'W/794e66a60279190a35babbc4b212751f',
        'base_url': 'https://www.archdaily.com',
    }
    api_url = f'{headers["base_url"]}/search/api/v1/us/images?page={start_page}'

    get_project_data(api_url, start_page, number_pages_checked, all_results, headers)
    save_to_json('projects.json', all_results)


if __name__ == "__main__":
    main()
