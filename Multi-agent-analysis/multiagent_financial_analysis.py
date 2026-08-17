import os
from dotenv import load_dotenv

from phi.agent import Agent
from phi.model.groq import Groq
from duckduckgo_search import DDGS


# ============================================================
# 1. LOAD ENVIRONMENT VARIABLES
# ============================================================

load_dotenv()

groq_api_key = os.getenv("GROQ_API_KEY")

if not groq_api_key:
    raise ValueError(
        "GROQ_API_KEY not found. Please check your .env file."
    )

print("✅ GROQ_API_KEY loaded successfully")


# ============================================================
# 2. FUNCTION TO FETCH FINANCIAL NEWS
# ============================================================

def search_financial_news(company, max_results=5):
    """
    Search recent financial news using DuckDuckGo directly.
    This avoids Phi's DuckDuckGo tool-calling problem.
    """

    print(f"\n🔎 Searching news for {company}...")

    try:
        results = []

        with DDGS() as ddgs:
            search_results = ddgs.news(
                keywords=f"{company} financial news",
                max_results=max_results
            )

            for item in search_results:
                results.append({
                    "title": item.get("title", ""),
                    "url": item.get("url", ""),
                    "date": item.get("date", ""),
                    "source": item.get("source", ""),
                    "body": item.get("body", "")
                })

        return results

    except Exception as e:
        print(f"⚠️ Could not fetch news for {company}: {e}")
        return []


# ============================================================
# 3. CONVERT NEWS INTO TEXT
# ============================================================

def format_news(company, news_items):

    if not news_items:
        return f"No current news could be retrieved for {company}."

    text = f"\n### {company} Financial News\n\n"

    for i, item in enumerate(news_items, start=1):

        text += f"#### {i}. {item['title']}\n"

        if item["source"]:
            text += f"Source: {item['source']}\n"

        if item["date"]:
            text += f"Date: {item['date']}\n"

        if item["body"]:
            text += f"Summary: {item['body']}\n"

        if item["url"]:
            text += f"URL: {item['url']}\n"

        text += "\n"

    return text


# ============================================================
# 4. NEWS AGENT
# ============================================================

news_agent = Agent(
    name="News Analysis Agent",

    model=Groq(
        id="llama-3.3-70b-versatile",
        api_key=groq_api_key
    ),

    instructions=[
        "Analyze the financial news provided by the Python search function.",
        "Summarize the most important news.",
        "Identify important events that may affect the company.",
        "Do not invent news.",
        "Clearly mention when information is unavailable.",
        "Use markdown."
    ],

    markdown=True
)


# ============================================================
# 5. MARKET ANALYSIS AGENT
# ============================================================

market_analysis_agent = Agent(
    name="Market Analysis Agent",

    model=Groq(
        id="llama-3.3-70b-versatile",
        api_key=groq_api_key
    ),

    instructions=[
        "Analyze the financial news provided.",
        "Identify possible factors affecting stock price.",
        "Identify positive and negative market signals.",
        "Do not invent stock prices.",
        "Do not make guaranteed predictions.",
        "Use markdown tables when useful."
    ],

    markdown=True
)


# ============================================================
# 6. SENTIMENT ANALYSIS AGENT
# ============================================================

sentiment_analysis_agent = Agent(
    name="Sentiment Analysis Agent",

    model=Groq(
        id="llama-3.3-70b-versatile",
        api_key=groq_api_key
    ),

    instructions=[
        "Analyze the financial news provided.",
        "Classify the overall sentiment as Positive, Negative, or Neutral.",
        "Explain the reasons for the sentiment.",
        "Do not invent information.",
        "Use markdown."
    ],

    markdown=True
)


# ============================================================
# 7. COMPANIES
# ============================================================

companies = [
    "Tesla",
    "NVIDIA"
]


# ============================================================
# 8. FETCH NEWS
# ============================================================

print("\n" + "=" * 60)
print("📈 MULTI-AGENT FINANCIAL ANALYSIS")
print("=" * 60)

all_news = {}

for company in companies:

    news = search_financial_news(
        company,
        max_results=5
    )

    all_news[company] = news


# ============================================================
# 9. CREATE NEWS TEXT
# ============================================================

combined_news = ""

for company in companies:

    combined_news += format_news(
        company,
        all_news[company]
    )


# ============================================================
# 10. NEWS ANALYSIS
# ============================================================

print("\n")
print("=" * 60)
print("📰 NEWS ANALYSIS")
print("=" * 60)

try:

    news_response = news_agent.run(
        f"""
Analyze the following financial news about Tesla and NVIDIA.

{combined_news}

Provide:

1. The most important news for each company.
2. A short summary of each event.
3. Key business implications.
4. Important risks or opportunities.

Do not invent information.
"""
    )

    print("\n" + news_response.content)

except Exception as e:

    print(f"❌ News Agent Error: {e}")


# ============================================================
# 11. MARKET ANALYSIS
# ============================================================

print("\n")
print("=" * 60)
print("📊 MARKET ANALYSIS")
print("=" * 60)

try:

    market_response = market_analysis_agent.run(
        f"""
Analyze possible market implications of the following
financial news about Tesla and NVIDIA.

{combined_news}

Discuss:

1. Positive factors
2. Negative factors
3. Possible reasons for stock volatility
4. Important market signals

Do not give guaranteed price predictions.
"""
    )

    print("\n" + market_response.content)

except Exception as e:

    print(f"❌ Market Analysis Error: {e}")


# ============================================================
# 12. SENTIMENT ANALYSIS
# ============================================================

print("\n")
print("=" * 60)
print("😊 SENTIMENT ANALYSIS")
print("=" * 60)

try:

    sentiment_response = sentiment_analysis_agent.run(
        f"""
Perform sentiment analysis on the following financial news
about Tesla and NVIDIA.

{combined_news}

For each company:

1. Overall sentiment: Positive / Negative / Neutral
2. Main reasons
3. Important positive news
4. Important negative news

Do not invent information.
"""
    )

    print("\n" + sentiment_response.content)

except Exception as e:

    print(f"❌ Sentiment Analysis Error: {e}")


# ============================================================
# 13. FINAL MESSAGE
# ============================================================

print("\n")
print("=" * 60)
print("✅ FINANCIAL ANALYSIS COMPLETED")
print("=" * 60)