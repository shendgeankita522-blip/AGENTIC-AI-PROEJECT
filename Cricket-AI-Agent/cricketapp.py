import streamlit as st
from phi.agent import Agent
from phi.model.groq import Groq
from ddgs import DDGS
from dotenv import load_dotenv
import os
from datetime import datetime


# ============================================================
# 1. LOAD ENVIRONMENT VARIABLES
# ============================================================

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    st.error("GROQ_API_KEY not found in .env file.")
    st.stop()


# ============================================================
# 2. PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Cricket AI",
    page_icon="🏏",
    layout="wide"
)


# ============================================================
# 3. TITLE
# ============================================================

st.title("🏏 Cricket AI")
st.subheader("Live Scores • Player Statistics • Cricket News")

current_date = datetime.now().strftime("%d %B %Y")

st.caption(f"Today's date: {current_date}")


# ============================================================
# 4. CREATE GROQ MODEL
# ============================================================

def create_model():

    return Groq(
        id="llama-3.3-70b-versatile",
        api_key=GROQ_API_KEY
    )


# ============================================================
# 5. WEB SEARCH FUNCTION
# ============================================================

def search_web(query, max_results=8):

    results = []

    try:

        with DDGS() as ddgs:

            search_results = ddgs.text(
                query,
                region="in-en",
                safesearch="moderate",
                max_results=max_results
            )

            for result in search_results:

                results.append({
                    "title": result.get("title", ""),
                    "body": result.get("body", ""),
                    "href": result.get("href", "")
                })

    except Exception as e:

        st.warning(f"Web search error: {e}")

    return results


# ============================================================
# 6. NEWS SEARCH FUNCTION
# ============================================================

def search_news(query, max_results=8):

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

        st.warning(f"News search error: {e}")

    return results


# ============================================================
# 7. FORMAT SEARCH RESULTS
# ============================================================

def format_results(results):

    if not results:
        return "NO SEARCH RESULTS FOUND."

    text = ""

    for i, result in enumerate(results, start=1):

        text += f"""
SOURCE {i}

TITLE:
{result.get("title", "")}

URL:
{result.get("href", "")}

CONTENT:
{result.get("body", "")}

--------------------------------------------------
"""

    return text


# ============================================================
# 8. FORMAT NEWS RESULTS
# ============================================================

def format_news_results(results):

    if not results:
        return "NO NEWS RESULTS FOUND."

    text = ""

    for i, result in enumerate(results, start=1):

        text += f"""
NEWS SOURCE {i}

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

--------------------------------------------------
"""

    return text


# ============================================================
# 9. CREATE AGENTS
# ============================================================

match_agent = Agent(

    name="Live Match Agent",

    model=create_model(),

    instructions=[
        "You are a cricket live match specialist.",
        "Analyze ONLY the search results provided in the prompt.",
        "Find the latest India vs Australia cricket match information.",
        "Report score, wickets, overs and match status if available.",
        "Mention important players if available.",
        "Do not invent any cricket information.",
        "If no current match is found, clearly say so.",
        "Use a markdown table.",
        "Keep the answer concise."
    ],

    markdown=True
)


player_agent = Agent(

    name="Player Stats Agent",

    model=create_model(),

    instructions=[
        "You are a cricket statistics specialist.",
        "Analyze ONLY the search results provided in the prompt.",
        "Find recent statistics for the requested player.",
        "Include runs, highest score, average and strike rate when available.",
        "Mention match/date when available.",
        "Do not invent statistics.",
        "If reliable statistics are unavailable, clearly say so.",
        "Use a markdown table.",
        "Keep the answer concise."
    ],

    markdown=True
)


news_agent = Agent(

    name="Cricket News Agent",

    model=create_model(),

    instructions=[
        "You are a cricket news specialist.",
        "Analyze ONLY the news results provided in the prompt.",
        "Summarize the latest cricket news.",
        "Mention important headlines.",
        "Mention upcoming matches when available.",
        "Mention injuries and team updates when available.",
        "Mention tournament updates when available.",
        "Mention source and date when available.",
        "Do not invent news.",
        "Use markdown formatting.",
        "Keep the answer concise."
    ],

    markdown=True
)


# ============================================================
# 10. STREAMLIT INPUTS
# ============================================================

st.divider()

col1, col2 = st.columns(2)

with col1:

    match_query = st.text_input(
        "🏏 Enter Match",
        placeholder="India vs Australia"
    )

with col2:

    player_query = st.text_input(
        "👤 Enter Player",
        placeholder="Virat Kohli"
    )


# ============================================================
# 11. BUTTON
# ============================================================

if st.button("🔍 Get Cricket Updates", use_container_width=True):

    if not match_query and not player_query:

        st.warning(
            "Please enter a match or player name."
        )

        st.stop()


    # ========================================================
    # LIVE MATCH
    # ========================================================

    if match_query:

        st.divider()

        st.header("🏏 Live Match Information")

        match_search_query = (
            f"{match_query} cricket latest live score "
            f"{current_date} Cricbuzz ESPNcricinfo"
        )

        with st.spinner("Searching latest match information..."):

            match_results = search_web(
                match_search_query,
                max_results=8
            )

        match_data = format_results(match_results)

        try:

            match_response = match_agent.run(

                f"""
Today is {current_date}.

Analyze the following web search results.

MATCH REQUEST:
{match_query}

SEARCH RESULTS:

{match_data}

IMPORTANT:
- Use ONLY the search results.
- Do NOT use your own memory.
- Do NOT invent scores.
- Prefer the most recent information.
- If no current match is available, clearly say so.
"""

            )

            st.markdown(match_response.content)

        except Exception as e:

            st.error(
                f"Match agent error: {e}"
            )


    # ========================================================
    # PLAYER STATISTICS
    # ========================================================

    if player_query:

        st.divider()

        st.header("👤 Player Statistics")

        player_search_query = (
            f"{player_query} latest cricket match "
            f"runs statistics {current_date} "
            f"Cricbuzz ESPNcricinfo"
        )

        with st.spinner("Searching player statistics..."):

            player_results = search_web(
                player_search_query,
                max_results=8
            )

        player_data = format_results(player_results)

        try:

            player_response = player_agent.run(

                f"""
Today is {current_date}.

Analyze the following search results.

PLAYER:
{player_query}

SEARCH RESULTS:

{player_data}

IMPORTANT:
- Use ONLY the search results.
- Do NOT invent statistics.
- Prefer recent matches.
- If statistics are unavailable, clearly say so.
"""

            )

            st.markdown(player_response.content)

        except Exception as e:

            st.error(
                f"Player agent error: {e}"
            )


    # ========================================================
    # CRICKET NEWS
    # ========================================================

    st.divider()

    st.header("📰 Latest Cricket News")

    news_search_query = (
        f"latest cricket news "
        f"{match_query} "
        f"{player_query} "
        f"{current_date}"
    )

    with st.spinner("Searching latest cricket news..."):

        news_results = search_news(
            news_search_query,
            max_results=10
        )

    news_data = format_news_results(news_results)

    try:

        news_response = news_agent.run(

            f"""
Today is {current_date}.

Analyze the following cricket news search results.

NEWS RESULTS:

{news_data}

IMPORTANT:
- Use ONLY the provided news results.
- Do NOT invent news.
- Prefer the most recent news.
- Mention source and date when available.
"""

        )

        st.markdown(news_response.content)

    except Exception as e:

        st.error(
            f"News agent error: {e}"
        )


    # ========================================================
    # COMPLETED
    # ========================================================

    st.divider()

    st.success(
        "🏏 Cricket analysis completed successfully!"
    )