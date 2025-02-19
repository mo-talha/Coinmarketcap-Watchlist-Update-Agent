from playwright.sync_api import sync_playwright
from dotenv import load_dotenv
from google import genai
from google.genai import types
import os
import requests
import json


def get_cookie_and_csrf_token(EMAIL: str, PASSWORD: str) -> list[str]:
    """Log in using email and password and get the cookie and csrf token.

    Args:
        Takes in email id of type string and password of type string to log into coinmarketcap.

    Returns:
        a list of the csrf token string and cookie string.
    """
    with sync_playwright() as p:
        # Launch a browser (use head=False to see the browser)
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        try:
            # Navigate to CoinMarketCap login page
            page.goto("https://coinmarketcap.com")

            page.wait_for_timeout(10)

            login_btn = page.query_selector(
                ".sc-65e7f566-0.eQBACe.BaseButton_base__34gwo.bt-base.BaseButton_t-default__8BIzz.BaseButton_size-sm__oHKNE.BaseButton_v-primary__gkWpJ.BaseButton_vd__gUkWt").click()

            # cryptocurrencies_btn = page.query_selector(".sc-194d08f0-7.hKUAPU").click()
            page.wait_for_timeout(10000)

            # Fill email and password (adjust selectors if needed)
            page.fill('input[type="email"]', EMAIL)

            page.fill('input[type="password"]', PASSWORD)

            # Click login button (selector may vary)
            page.click('button[data-test="login-btn"]')

            print("log in success")

            nav_btns = page.query_selector_all(
                '.sc-65e7f566-0.gZBux.base-text')
            # print(len(nav_btns))
            watchlist_btn = nav_btns[1]
            watchlist_btn.click()
            page.wait_for_timeout(10000)
            # # Capture cookies after login
            cookies = context.cookies(
                "https://coinmarketcap.com/watchlist/627b865a849035b005d88d31/")

            tokens = []

            for cookie in cookies:
                if cookie["name"] == 'x-csrf-token':
                    tokens.append(cookie["value"])

                if cookie["name"] == 'Authorization':
                    tokens.append(cookie["value"])

            return tokens
            # # Save cookies to a file (optional)
            # with open("cmc_cookies.json", "w") as f:
            #     json.dump(cookies, f)

            # # Extract x-csrf-token
            # csrf_cookie = next(
            #     (c for c in cookies if c["name"] == "x-csrf-token"), None)
            # if csrf_cookie:
            #     print("Authenticated CSRF Token:", csrf_cookie["value"])
            # else:
            #     print("Token not found in cookies.")

        except Exception as e:
            print("Error:", e)
        finally:
            browser.close()


# tokens = get_cookie_csrf_tokens()


def get_watchlist(tokens: list[str]) -> list[str, list[dict]]:
    """Get coinmarket cap watchlist.

    Args:
        tokens:list[str] - takes in a list of csrf token string and a cookie string. 

    Returns:
        A list of watchlist id of type string and watchlist coins of type list of dict objects.
    """
    url = "https://api.coinmarketcap.com/asset/v3.1/watchlist/query-basic"

    payload = json.dumps({})
    headers = {
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'en-US,en;q=0.9,en-IN;q=0.8',
        'cache-control': 'no-cache',
        'content-type': 'application/json',
        'cookie': f'_ga=GA1.2.754198406.1676981437; _sharedID=b3176688-2fbd-48c6-b287-75a74989a423; _sharedID_cst=zix7LPQsHA%3D%3D; _au_1d=AU1D-0100-001709721529-B47W3V2V-9II6; bnc-uuid=b605663a-a8ae-4b61-b0ad-f4f01f1ac544; se_gd=ApWWwWw0SABFgcLcJFlIgZZFhAhoVBSV1pW5QU0R1lXVQU1NWUNc1; se_gsd=USglChF7JSAnFlIwNRM0IxMyWxIDDwsFUFlDVV1aUllRCVNT1; OptanonAlertBoxClosed=2024-08-26T05:50:57.779Z; eupubconsent-v2=CQD8rGQQD8rGQAcABBENBDFgAAAAAAAAAChQAAAUcgIgA4AM-AjwBKoDfAHbAO5AgoBIgCSgEowJkgTSAn2BRQCi0FGgUcAA.YAAAAAAAAAAA; _au_last_seen_iab_tcf=1726922107095; _cc_id=159c57b18973c5d7170fb14a6cdba689; OTGPPConsent=DBABLA~BVQVAAAABgA.QA; _awl=2.1727762085.5-685abb2e5dbfcc4bd0704938bab95c6e-6763652d617369612d6561737431-1; _cb=qCMVzsJc4bBnu2b_; _chartbeat2=.1734267765109.1734267765109.1.CUpnMiln4bLzn5DQDVkCUyCSyreZ.1; _hjSessionUser_1060636=eyJpZCI6IjY1YTNjZTI1LWQwZDQtNWEyMi04NjZkLTkzZWVmYTU3NTE1OCIsImNyZWF0ZWQiOjE3MzQyNjc3NjU1NzUsImV4aXN0aW5nIjpmYWxzZX0=; _sharedid=a61840c0-8212-4880-b8c5-6562c6dcaac1; _sharedid_cst=zix7LPQsHA%3D%3D; cto_bundle=lmkW_V9vcXRzQ0lRM1ZrY1NpSGdUNyUyQlRQUk9hMTMybE0lMkI0RjF4blRnNDhHd2N2c2R6SnEzWEJNNnJBSzRLWENiTTdzT2ozaU51YzlCaUZQMGJIVzMyS0lnRkZWUlRGV1YzUDdJeUQxS1QyMnF4TUR6Z0VyQTlTSmFWdUdJMzNoMiUyRnVWdGp0anZnYkZpd012bk55bXZ4ciUyQlM5ZyUzRCUzRA; cto_bidid=Zo-Y9l92SlRpUnpDaU4xVXAlMkJWbVlNc0ZpU0dZbyUyRlpsd3dzVHo5Tmp2ajNoWGZVc3JVdW9sMVB5eVJzbzdmNmlSSG85M0Z6OXNYN2tlTXd2a0FTOWVXcXNjM2VFTjNJJTJCSVJOekhsSjNGd3NKNGZwNklsaVZGMXM5eVZJVVByaUxYVXNaRQ; cto_dna_bundle=2w8Jb180M0RITmhlJTJCZkMwOUJGQlhaMUN2czhtMENUUm9jQ0dqd1JJVG9YUEtwbUgxNUQ5Z0dzJTJGclUybDR6aEtwd1E2YQ; se_sd=1JSDFWQJaHOUlUBxVFREgZZBwBQoWEZW1UG5cW0JVhSUAAVNWUUF1; BNC_FV_KEY=33932b57b78b93a5b9498b688c290a74bf5cd1d9; BNC_FV_KEY_EXPIRE=1739725896720; Authorization={tokens[1]}; sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%226405b878b2cfa2468c7c60f8%22%2C%22first_id%22%3A%22187567459d4298-03d7d39cd4aa86a-7a545474-1327104-187567459d5876%22%2C%22props%22%3A%7B%22%24latest_traffic_source_type%22%3A%22%E7%9B%B4%E6%8E%A5%E6%B5%81%E9%87%8F%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC_%E7%9B%B4%E6%8E%A5%E6%89%93%E5%BC%80%22%2C%22%24latest_referrer%22%3A%22%22%7D%2C%22identities%22%3A%22eyIkaWRlbnRpdHlfY29va2llX2lkIjoiMTg3NTY3NDU5ZDQyOTgtMDNkN2QzOWNkNGFhODZhLTdhNTQ1NDc0LTEzMjcxMDQtMTg3NTY3NDU5ZDU4NzYiLCIkaWRlbnRpdHlfbG9naW5faWQiOiI2NDA1Yjg3OGIyY2ZhMjQ2OGM3YzYwZjgifQ%3D%3D%22%2C%22history_login_id%22%3A%7B%22name%22%3A%22%24identity_login_id%22%2C%22value%22%3A%226405b878b2cfa2468c7c60f8%22%7D%2C%22%24device_id%22%3A%22187567459d4298-03d7d39cd4aa86a-7a545474-1327104-187567459d5876%22%7D; x-csrf-token={tokens[0]}; __gads=ID=990673b0f08bf4f3:T=1738464442:RT=1739678043:S=ALNI_MYwpo4UaqQsfHSljs126l9LmwnxHQ; __gpi=UID=0000101ab6e79c5a:T=1738464442:RT=1739678043:S=ALNI_MZLyZ7qAv4hMVIts4CjFIoQ0j6p3g; __eoi=ID=cd8c7d587da32832:T=1727762092:RT=1739678043:S=AA-Afjb1eqUaqoAkU4UsMwhpoRko; OptanonConsent=isGpcEnabled=0&datestamp=Sun+Feb+16+2025+09%3A25%3A23+GMT%2B0530+(India+Standard+Time)&version=202409.1.0&browserGpcFlag=0&isIABGlobal=false&hosts=&consentId=ee38b294-a549-4bdc-9d10-b4cec1bb272e&interactionCount=1&isAnonUser=1&landingPath=NotLandingPage&groups=C0001%3A1%2CC0003%3A0%2CC0004%3A0%2CC0002%3A0&geolocation=IN%3BKA&AwaitingReconsent=false&intType=2&GPPCookiesCount=1; Authorization={tokens[1]}',
        'fvideo-id': '33932b57b78b93a5b9498b688c290a74bf5cd1d9',
        'origin': 'https://coinmarketcap.com',
        'platform': 'web',
        'priority': 'u=1, i',
        'referer': 'https://coinmarketcap.com/',
        'sec-ch-ua': '"Not A(Brand";v="8", "Chromium";v="132", "Microsoft Edge";v="132"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36 Edg/132.0.0.0',
        'x-csrf-token': f'{tokens[0]}',
        'x-request-id': 'db5592b07f30451ebfeb1ad3cc3c5379'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    if response.status_code == 200:
        data = response.json()
        # print(data)
        watchlist_data: dict = data["data"]["watchLists"][0]

        watchlist_coins: list[dict] = watchlist_data["cryptoCurrencies"]

        watchlist_id: str = watchlist_data.get("watchListId")

        # print(watchlist_id)

        return [watchlist_id, watchlist_coins]


def get_binance_tradables() -> list[dict]:
    """Get coins which are tradable on binance.

    Returns:
        A list of binance tradables as dict objects, each object consists of baseCurrencyId, baseCurrencyName and baseSymbol.
    """
    # Can implement api call to fetch latest binance coins
    bnb_tradables = [
        {
            "baseCurrencyId": 35336,
            "baseCurrencyName": "OFFICIAL TRUMP",
            "baseSymbol": "TRUMP"
        },
        {
            "baseCurrencyId": 6536,
            "baseCurrencyName": "MANTRA",
            "baseSymbol": "OM"
        },
        {
            "baseCurrencyId": 1027,
            "baseCurrencyName": "Ethereum",
            "baseSymbol": "ETH"
        },
        {
            "baseCurrencyId": 1,
            "baseCurrencyName": "Bitcoin",
            "baseSymbol": "BTC"
        }
    ]

    return bnb_tradables


def add_coin_to_watchlist(watchlist_id: str, coin_id: int, tokens:list[str]) -> str:
    """Adds a coin to coinmarketcap watchlist.

    Args:
        watchlist_id: Id of the watchlist to which the coin is to be added, coin_id: id of the coin which needs to be added to the watchlist.
        tokens:list[str] - takes in a list of csrf token string and a cookie string. 
    Returns:
        a success or failed message indicating if a coin was added or not.
    """
    url = "https://api.coinmarketcap.com/asset/v3/watchlist/subscribe"

    payload = json.dumps({
        "resourceId": coin_id,
        "resourceType": "CRYPTO",
        "subscribeType": "SUBSCRIBE",
        "watchListId": watchlist_id
    })

    headers = {
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'no-cache',
        'content-type': 'application/json',
        'cookie': f'_ga=GA1.2.754198406.1676981437; _sharedID=b3176688-2fbd-48c6-b287-75a74989a423; _sharedID_cst=zix7LPQsHA%3D%3D; _au_1d=AU1D-0100-001709721529-B47W3V2V-9II6; bnc-uuid=b605663a-a8ae-4b61-b0ad-f4f01f1ac544; se_gd=ApWWwWw0SABFgcLcJFlIgZZFhAhoVBSV1pW5QU0R1lXVQU1NWUNc1; se_gsd=USglChF7JSAnFlIwNRM0IxMyWxIDDwsFUFlDVV1aUllRCVNT1; OptanonAlertBoxClosed=2024-08-26T05:50:57.779Z; eupubconsent-v2=CQD8rGQQD8rGQAcABBENBDFgAAAAAAAAAChQAAAUcgIgA4AM-AjwBKoDfAHbAO5AgoBIgCSgEowJkgTSAn2BRQCi0FGgUcAA.YAAAAAAAAAAA; _au_last_seen_iab_tcf=1726922107095; sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%22627b865a80d1186958b782dd%22%2C%22first_id%22%3A%22187567459d4298-03d7d39cd4aa86a-7a545474-1327104-187567459d5876%22%2C%22props%22%3A%7B%22%24latest_traffic_source_type%22%3A%22%E7%9B%B4%E6%8E%A5%E6%B5%81%E9%87%8F%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC_%E7%9B%B4%E6%8E%A5%E6%89%93%E5%BC%80%22%2C%22%24latest_referrer%22%3A%22%22%7D%2C%22identities%22%3A%22eyIkaWRlbnRpdHlfY29va2llX2lkIjoiMTg3NTY3NDU5ZDQyOTgtMDNkN2QzOWNkNGFhODZhLTdhNTQ1NDc0LTEzMjcxMDQtMTg3NTY3NDU5ZDU4NzYiLCIkaWRlbnRpdHlfbG9naW5faWQiOiI2MjdiODY1YTgwZDExODY5NThiNzgyZGQifQ%3D%3D%22%2C%22history_login_id%22%3A%7B%22name%22%3A%22%24identity_login_id%22%2C%22value%22%3A%22627b865a80d1186958b782dd%22%7D%2C%22%24device_id%22%3A%22187567459d4298-03d7d39cd4aa86a-7a545474-1327104-187567459d5876%22%7D; _cc_id=159c57b18973c5d7170fb14a6cdba689; OTGPPConsent=DBABLA~BVQVAAAABgA.QA; _awl=2.1727762085.5-685abb2e5dbfcc4bd0704938bab95c6e-6763652d617369612d6561737431-1; _cb=qCMVzsJc4bBnu2b_; _chartbeat2=.1734267765109.1734267765109.1.CUpnMiln4bLzn5DQDVkCUyCSyreZ.1; _hjSessionUser_1060636=eyJpZCI6IjY1YTNjZTI1LWQwZDQtNWEyMi04NjZkLTkzZWVmYTU3NTE1OCIsImNyZWF0ZWQiOjE3MzQyNjc3NjU1NzUsImV4aXN0aW5nIjpmYWxzZX0=; _sharedid=a61840c0-8212-4880-b8c5-6562c6dcaac1; _sharedid_cst=zix7LPQsHA%3D%3D; cto_bundle=lmkW_V9vcXRzQ0lRM1ZrY1NpSGdUNyUyQlRQUk9hMTMybE0lMkI0RjF4blRnNDhHd2N2c2R6SnEzWEJNNnJBSzRLWENiTTdzT2ozaU51YzlCaUZQMGJIVzMyS0lnRkZWUlRGV1YzUDdJeUQxS1QyMnF4TUR6Z0VyQTlTSmFWdUdJMzNoMiUyRnVWdGp0anZnYkZpd012bk55bXZ4ciUyQlM5ZyUzRCUzRA; cto_bidid=Zo-Y9l92SlRpUnpDaU4xVXAlMkJWbVlNc0ZpU0dZbyUyRlpsd3dzVHo5Tmp2ajNoWGZVc3JVdW9sMVB5eVJzbzdmNmlSSG85M0Z6OXNYN2tlTXd2a0FTOWVXcXNjM2VFTjNJJTJCSVJOekhsSjNGd3NKNGZwNklsaVZGMXM5eVZJVVByaUxYVXNaRQ; cto_dna_bundle=2w8Jb180M0RITmhlJTJCZkMwOUJGQlhaMUN2czhtMENUUm9jQ0dqd1JJVG9YUEtwbUgxNUQ5Z0dzJTJGclUybDR6aEtwd1E2YQ; se_sd=1JSDFWQJaHOUlUBxVFREgZZBwBQoWEZW1UG5cW0JVhSUAAVNWUUF1; BNC_FV_KEY=33932b57b78b93a5b9498b688c290a74bf5cd1d9; BNC_FV_KEY_EXPIRE=1739725896720; __gads=ID=990673b0f08bf4f3:T=1738464442:RT=1739648306:S=ALNI_MYwpo4UaqQsfHSljs126l9LmwnxHQ; __gpi=UID=0000101ab6e79c5a:T=1738464442:RT=1739648306:S=ALNI_MZLyZ7qAv4hMVIts4CjFIoQ0j6p3g; __eoi=ID=cd8c7d587da32832:T=1727762092:RT=1739648306:S=AA-Afjb1eqUaqoAkU4UsMwhpoRko; Authorization={tokens[1]}; OptanonConsent=isGpcEnabled=0&datestamp=Sun+Feb+16+2025+02%3A01%3A24+GMT%2B0530+(India+Standard+Time)&version=202409.1.0&browserGpcFlag=0&isIABGlobal=false&hosts=&consentId=ee38b294-a549-4bdc-9d10-b4cec1bb272e&interactionCount=1&isAnonUser=1&landingPath=NotLandingPage&groups=C0001%3A1%2CC0003%3A0%2CC0004%3A0%2CC0002%3A0&geolocation=IN%3BKA&AwaitingReconsent=false&intType=2&GPPCookiesCount=1; x-csrf-token={tokens[0]}',
        'fvideo-id': '33069bea31639c31a9529c1c981f7c1d68ddbfdb',
        'origin': 'https://coinmarketcap.com',
        'platform': 'web',
        'priority': 'u=1, i',
        'referer': 'https://coinmarketcap.com/',
        'sec-ch-ua': '"Not A(Brand";v="8", "Chromium";v="132", "Google Chrome";v="132"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36',
        'x-csrf-token': f'{tokens[0]}',
        'x-request-id': '892a6727cbf34ae6acc21168ef6a460b'
    }
    response = requests.request("POST", url, headers=headers, data=payload)

    # print(f"{response.json()}")
    if response.status_code == 200:
        response_data = response.json()
        message = response_data["status"]["error_message"]

        return message

    else:
        print(f"Failed to add coin_id:{coin_id} to watchlist")
        return "Failed"


if __name__ == "__main__":
    load_dotenv("C:\Python\Agents\CoinMarketCapAgent\.env")

    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY_2")

    while True:
        config = types.GenerateContentConfig(
            tools=[get_cookie_and_csrf_token, get_watchlist, get_binance_tradables, add_coin_to_watchlist]
            # tools=[get_cookie_and_csrf_token, get_watchlist, get_binance_tradables, add_binance_coins_not_in_watchlist]
        )

        client = genai.Client(api_key=GEMINI_API_KEY)

        prompt = input()

        response = client.models.generate_content(
            model="gemini-2.0-flash",
            config=config,
            contents=prompt
        )

        print(response.text)
