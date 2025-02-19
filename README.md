**CryptoWatchlist Automation**
Automate CoinMarketCap watchlist management with this Python tool that helps identify and add tradable Binance coins to your watchlist.

**Features**
- Automated login to CoinMarketCap via browser automation
- Retrieve your existing CoinMarketCap watchlist
- Identify Binance-tradable cryptocurrencies
- Add new tradable coins to your watchlist automatically

**Requirements**

- Python 3.9+
- CoinMarketCap account credentials
- Gemini API key

**Installation**

- Clone this repository
- Install dependencies:
- Copypip install -r requirements.txt

**Create a .env file in the project root with:**

- Copy GEMINI_API_KEY=your_gemini_api_key

**Setup**
Before running the script:

- Install Playwright browser dependencies:
- playwright install chromium

**Usage**

- python cmc.py
  **The script uses Google's Gemini AI to process your commands. You can prompt it with natural language like:**

"Login to CoinMarketCap and check my watchlist"
"Add Binance-tradable coins to my watchlist"

**How It Works**

- The script handles authentication with CoinMarketCap using Playwright browser automation, you need to enter the
  email and password in the termninal, make sure to create an account on coinmarketcap if you don't have one. This is not
  recommended as you are giving away your credentials on the API, to avoid this you can simply change the method to login
  by itself and after login you can hand it over to the agent.
- It retrieves your current watchlist contents
- It fetches coins tradable on Binance (currently using a sample list) can integrate an API.
- It can add missing coins to your watchlist that are Binance-tradable

**Security Note**

- Your CoinMarketCap credentials will be requested during runtime, not stored in code
- The script temporarily uses browser cookies for authentication
- Never share your .env file or credentials
