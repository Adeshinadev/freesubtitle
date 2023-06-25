from typing import List
import httpx
import json
from bs4 import BeautifulSoup

headers = {
    "authority": "www.opensubtitles.org",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-language": "en,ru;q=0.9",
    "cache-control": "max-age=0",
    # 'cookie': '_ga=GA1.2.2026298587.1682033738; _gid=GA1.2.838139868.1682033738; searchform=formname%3Dsearchform%7C%7C%7C%7C%7C%7C%7C%7C%7C%7C%7C%7C%7C%7C1%7C%7C%7C1%7C%7C%7C%7C%7C%7C%7C%7C%7C%7C%7C%7C%7C%7C%7C%7C%7C; PHPSESSID=bA2jNCdwZ6WA5uUzeiGsDqCCFS3',
    "referer": "https://www.opensubtitles.org/en/search/subs",
    "sec-ch-ua": '"Chromium";v="110", "Not A(Brand";v="24", "YaBrowser";v="23"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Linux"',
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "none",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 YaBrowser/23.3.1.906 (beta) Yowser/2.5 Safari/537.36",
}

post_headers = {
    "connection": "keep-alive",
    # 'content-length': '1282',
    "x-real-ip": "111.88.222.106",
    "content-type": "application/json",
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 YaBrowser/23.3.1.906 (beta) Yowser/2.5 Safari/537.36 X-Middleton/1",
    # 'accept-encoding': 'deflate, gzip',
    "accept": "*/*",
    "host": "https://freesubtitle-dd3fc3b3d9c1.herokuapp.com",
}


def initial_request(url):
    print(f"HTTP POST request to URL: {url}", end="\n")
    with httpx.Client(headers=headers, timeout=180) as client:
        resp = client.get(url)
        print(f" | Status Code: {resp.status_code}")
        return resp


def pagination(response, ignore_titles: List[str]):
    for page in range(0, 500 + 1, 40):
        page_next = (
            f"https://www.opensubtitles.org/en/search/sublanguageid-all/offset-{page}"
        )
        print(f"HTTP POST request to URL: {page_next}", end="\n")
        next_response = httpx.get(page_next, headers=headers)
        print(f" | Status Code: {next_response.status_code}")
        parse_titles(next_response, ignore_titles)


def parse_titles(response, ignore_titles: List[str]):
    soup = BeautifulSoup(response.content, "html.parser")
    odd = soup.select("tr.change.odd.expandable")
    even = soup.select("tr.change.even.expandable")
    data = even + odd
    subtitle_data = []
    for d in data:
        if d.select_one("td.sb_star_even") or d.select_one("td.sb_star_odd"):
            title = (
                d.select_one("a.bnone")
                .get("title")
                .replace('"', "")
                .replace("subtitles -", "")
                .strip()
            )
            lang = d.select_one('td[align="center"] > a').get("title")
            if title not in ignore_titles:
                subtitle_data.append(
                    {
                        "Title": title,
                        "Star": True,
                        "Language": lang,
                    }
                )
        else:
            if (
                d.select_one("a.bnone")
                .get("title")
                .replace('"', "")
                .replace("subtitles -", "")
                .strip()
                not in ignore_titles
            ):
                subtitle_data.append(
                    {
                        "Title": d.select_one("a.bnone")
                        .get("title")
                        .replace('"', "")
                        .replace("subtitles -", "")
                        .strip(),
                        "Star": False,
                        "Language": d.select_one('td[align="center"] > a').get("title"),
                    }
                )

    json_data = json.dumps(subtitle_data, indent=2)
    print(json_data)
    httpx.post(
        "https://freesubtitle-dd3fc3b3d9c1.herokuapp.com/dashboard/post-titles",
        headers=post_headers,
        json=json_data,
    )


def hello_world(request):
    ignore_titles = [
        "Inventing Anna Two Birds, One Throne",
        "My Sister's Serial Killer Boyfriend",
    ]
    base_url = "https://www.opensubtitles.org/en/search/sublanguageid-all"
    init_response = initial_request(base_url)
    pagination(init_response, ignore_titles)
    return 'Task is done'
