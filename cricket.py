from phi.agent import Agent
from phi.model.groq import Groq
from ddgs import DDGS
from dotenv import load_dotenv
from datetime import datetime
import os


# ============================================================
# 1. LOAD ENVIRONMENT VARIABLES
# ============================================================

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError(
        "\nGROQ_API_KEY was not found.\n\n"
        "Create a .env file in the same folder as this program "
        "and add:\n\n"
        "GROQ_API_KEY=your_actual_groq_api_key\n"
    )


# ============================================================
# 2. CURRENT DATE
# ============================================================

current_date = datetime.now().strftime("%d %B %Y")

print("=" * 70)
print("CRICKET AI ANALYSIS SYSTEM")
print("=" * 70)
print(f"Date: {current_date}")
print("=" * 70)


# ============================================================
# 3. CREATE GROQ MODEL
# ============================================================

def create_model():

    return Groq(
        id="llama-3.3-70b-versatile",
        api_key=GROQ_API_KEY
    )


# ============================================================
# 4. WEB TEXT SEARCH
# ============================================================

def search_web(query, max_results=8):

    print()
    print(f"Searching web:")
    print(query)

    results = []

    try:

        with DDGS() as ddgs:

            search_results = ddgs.text(
                query,
                region="in-en",
                safesearch="moderate",
                max_results=max_results,
                backend="auto"
            )

            for result in search_results:

                results.append({
                    "title": result.get("title", ""),
                    "body": result.get("body", ""),
                    "href": result.get("href", "")
                })

    except Exception as e:

        print()
        print("Web search error:")
        print(str(e))

    return results


# ============================================================
# 5. CRICKET NEWS SEARCH
# ============================================================

def search_news(query, max_results=8):

    print()
    print("Searching cricket news:")
    print(query)

    results = []

    try:

        with DDGS() as ddgs:

            news_results = ddgs.news(
                query,
                region="in-en",
                safesearch="moderate",
                max_results=max_results
            )

            for result in news_results:

                results.append({
                    "title": result.get("title", ""),
                    "body": result.get("body", ""),
                    "url": result.get("url", ""),
                    "date": result.get("date", ""),
                    "source": result.get("source", "")
                })

    except Exception as e:

        print()
        print("News search error:")
        print(str(e))

    return results


# ============================================================
# 6. FORMAT WEB SEARCH RESULTS
# ============================================================

def format_web_results(results):

    if not results:

        return "NO SEARCH RESULTS FOUND."

    text = ""

    for index, result in enumerate(results, start=1):

        text += f"""
SOURCE {index}

TITLE:
{result.get("title", "")}

URL:
{result.get("href", "")}

CONTENT:
{result.get("body", "")}

============================================================
"""

    return text


# ============================================================
# 7. FORMAT NEWS RESULTS
# ============================================================

def format_news_results(results):

    if not results:

        return "NO NEWS RESULTS FOUND."

    text = ""

    for index, result in enumerate(results, start=1):

        text += f"""
NEWS SOURCE {index}

TITLE:
{result.get("title", "")}

SOURCE:
{result.get("source", "")}

DATE:
{result.get("date", "")}

URL:
{result.get("url", "")}

CONTENT:
{result.get("body", "")}

============================================================
"""

    return text


# ============================================================
# 8. LIVE MATCH AGENT
# ============================================================

match_agent = Agent(

    name="Live Match Agent",

    model=create_model(),

    instructions=[
        "You are a cricket live match specialist.",
        "Analyze only the search information provided to you.",
        "Find the latest India vs Australia cricket match information.",
        "Report the latest score if available.",
        "Report runs, wickets and overs if available.",
        "Report match status if available.",
        "Mention important players if available.",
        "Do not invent scores or match information.",
        "If there is no current India vs Australia match, clearly say so.",
        "Prefer the most recent information.",
        "Use a markdown table.",
        "Keep the answer easy to understand."
    ],

    markdown=True
)


# ============================================================
# 9. PLAYER STATS AGENT
# ============================================================

player_agent = Agent(

    name="Player Stats Agent",

    model=create_model(),

    instructions=[
        "You are a cricket statistics specialist.",
        "Analyze only the search information provided to you.",
        "Find the latest available statistics for Virat Kohli.",
        "Focus on recent matches.",
        "Include runs when available.",
        "Include highest score when available.",
        "Include batting average when available.",
        "Include strike rate when available.",
        "Mention match/date when available.",
        "Do not invent statistics.",
        "If reliable recent statistics are unavailable, clearly say so.",
        "Use a markdown table."
    ],

    markdown=True
)


# ============================================================
# 10. CRICKET NEWS AGENT
# ============================================================

news_agent = Agent(

    name="Cricket News Agent",

    model=create_model(),

    instructions=[
        "You are a cricket news specialist.",
        "Analyze only the news results provided to you.",
        "Summarize the latest cricket news.",
        "Highlight important headlines.",
        "Mention upcoming matches when available.",
        "Mention injuries when available.",
        "Mention team updates when available.",
        "Mention tournament updates when available.",
        "Include the source and date when available.",
        "Do not invent news.",
        "Use markdown formatting.",
        "Keep the answer concise."
    ],

    markdown=True
)


# ============================================================
# 11. LIVE MATCH SEARCH
# ============================================================

print()
print("=" * 70)
print("1. LIVE MATCH INFORMATION")
print("=" * 70)

match_query = (
    f"India vs Australia cricket latest live score "
    f"{current_date} Cricbuzz ESPNcricinfo"
)

match_results = search_web(
    match_query,
    max_results=8
)

match_data = format_web_results(match_results)


# ============================================================
# 12. SEND MATCH DATA TO MATCH AGENT
# ============================================================

try:

    match_response = match_agent.run(
        f"""
Today is {current_date}.

Find the latest India vs Australia cricket match information
from the following search results.

SEARCH RESULTS:

{match_data}

Important:
- Do not use your own memory for the score.
- Do not invent a score.
- Use only the information in the search results.
- If there is no current match, say that clearly.
"""
    )

    print()
    print(match_response.content)

except Exception as e:

    print()
    print("Match Agent Error:")
    print(str(e))


# ============================================================
# 13. VIRAT KOHLI SEARCH
# ============================================================

print()
print("=" * 70)
print("2. VIRAT KOHLI RECENT STATS")
print("=" * 70)

player_query = (
    f"Virat Kohli latest match runs statistics "
    f"{current_date} Cricbuzz ESPNcricinfo"
)

player_results = search_web(
    player_query,
    max_results=8
)

player_data = format_web_results(player_results)


# ============================================================
# 14. SEND PLAYER DATA TO PLAYER AGENT
# ============================================================

try:

    player_response = player_agent.run(
        f"""
Today is {current_date}.

Find recent Virat Kohli statistics from the
following search results.

SEARCH RESULTS:

{player_data}

Important:
- Do not invent statistics.
- Use only information from the search results.
- If recent statistics are unavailable, clearly say so.
"""
    )

    print()
    print(player_response.content)

except Exception as e:

    print()
    print("Player Agent Error:")
    print(str(e))


# ============================================================
# 15. CRICKET NEWS SEARCH
# ============================================================

print()
print("=" * 70)
print("3. LATEST CRICKET NEWS")
print("=" * 70)

news_query = (
    f"latest cricket news India Australia Virat Kohli "
    f"{current_date}"
)

news_results = search_news(
    news_query,
    max_results=10
)

news_data = format_news_results(news_results)


# ============================================================
# 16. SEND NEWS DATA TO NEWS AGENT
# ============================================================

try:

    news_response = news_agent.run(
        f"""
Today is {current_date}.

Summarize the latest cricket news from these
search results.

NEWS RESULTS:

{news_data}

Important:
- Use only the provided news results.
- Do not invent information.
- Mention source and date when available.
- Prefer the most recent news.
"""
    )

    print()
    print(news_response.content)

except Exception as e:

    print()
    print("News Agent Error:")
    print(str(e))


# ============================================================
# 17. COMPLETED
# ============================================================

print()
print("=" * 70)
print("CRICKET ANALYSIS COMPLETED")
print("=" * 70)