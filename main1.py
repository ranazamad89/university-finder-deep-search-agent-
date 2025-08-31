# main.py
import os
import asyncio
import re
from urllib.parse import urljoin, urlparse
import aiohttp
import pandas as pd
import chainlit as cl
from dotenv import load_dotenv
from agents.run import RunConfig
from openai import AsyncOpenAI
from tavily import AsyncTavilyClient
from agents import Agent, Runner, function_tool, OpenAIChatCompletionsModel, handoffs
from playwright.async_api import async_playwright

# --- Configuration ---
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
if not GEMINI_API_KEY or not TAVILY_API_KEY:
    raise ValueError("Set GEMINI_API_KEY and TAVILY_API_KEY in .env")

external_client = AsyncOpenAI(api_key=GEMINI_API_KEY,
base_url="https://generativelanguage.googleapis.com/v1beta/openai/")
tavily_client = AsyncTavilyClient(api_key=TAVILY_API_KEY)
llm_model = OpenAIChatCompletionsModel(model="gemini-2.5-flash", openai_client=external_client)

# --- Global State ---
user_requirements = {"degree": "", "country": ""}
all_programs = []

# --- Helpers ---
HEADERS = {"User-Agent": "Mozilla/5.0"}

def update_requirements(text: str):
    lower = text.lower()
    if any(x in lower for x in ["bachelor", "bs", "bsc", "degree"]):
        if "in" in lower:
            user_requirements["degree"] = text.split("in")[-1].strip().title()
        else:
            user_requirements["degree"] = "Bachelor's"
    for c in ["germany", "usa", "canada", "uk", "australia"]:
        if c in lower:
            user_requirements["country"] = c.title()

def requirements_complete() -> bool:
    return all(user_requirements.values())

async def fetch_html(session: aiohttp.ClientSession, url: str) -> str:
    try:
        async with session.get(url, headers=HEADERS, timeout=20) as resp:
            if resp.status == 200:
                return await resp.text(errors="ignore")
    except:
        return ""
    return ""
async def fetch_with_playwright(url: str) -> str:
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto(url, timeout=30000, wait_until="networkidle")
            content = await page.content()
            await browser.close()
            return content
    except Exception:
        return ""


def clean_text(text: str, max_len=16000) -> str:
    return re.sub(r"\s+", " ", text).strip()[:max_len]

def same_domain(a, b):
    try:
        return urlparse(a).netloc == urlparse(b).netloc
    except:
        return False

def likely_program_link(href: str):
    keywords = ["program", "graduate", "ms", "msc", "ma", "master", "postgraduate", "admissions"]
    return any(k in href.lower() for k in keywords)

async def collect_links(session, base_url: str, html: str, limit=6):
    links = set()
    for m in re.finditer(r'href=["\']([^"\']+)["\']', html, re.IGNORECASE):
        href = m.group(1)
        if href.startswith("#") or href.startswith("mailto:") or href.startswith("javascript:"):
            continue
        full = urljoin(base_url, href)
        if same_domain(base_url, full) and likely_program_link(full):
            links.add(full)
        if len(links) >= limit:
            break
    return list(links)

# --- Tools ---
@function_tool(name_override="FIND_UNIVERSITIES")
async def find_universities(country: str, degree: str) -> list:
    query = f"Universities in {country} offering Master programs for {degree} site:.edu OR site:.{country.lower()}"
    results = await tavily_client.search(query, max_results=8)
    return results.get("results", [])

# --- Agents ---
requirement_agent = Agent(name="requirement_agent",
                    instructions="Ask user for degree and country before proceeding.",
                    model=llm_model)

general_agent = Agent(name="general_agent", instructions="Handle general queries", model=llm_model)

suggestion_agent = Agent(name="suggestion_agent",
                    instructions="Extract Master programs with requirements, deadlines, fees.",
                    model=llm_model,
                    tools=[find_universities])

orchestrator = Agent(name="orchestrator_agent",
                    model=llm_model,
                    tools=[
                    requirement_agent.as_tool("requirement_agent", "Gather requirements"),
                    suggestion_agent.as_tool("suggestion_agent", "Suggest Master programs"),
                    general_agent.as_tool("general_agent", "Handle general queries")
                    ])

run_config = RunConfig(model=llm_model, tracing_disabled=True)
# Raw async function to get university results
async def find_universities_raw(country: str, degree: str) -> list:
    query = f"Universities in {country} offering Master programs for {degree} site:.edu OR site:.{country.lower()}"
    results = await tavily_client.search(query, max_results=8)
    return results.get("results", [])


# --- Chainlit handlers ---
@cl.on_chat_start
async def on_start():
    cl.user_session.set("agent", orchestrator)
    cl.user_session.set("user_inputs", user_requirements)
    cl.user_session.set("all_programs", all_programs)
    await cl.Message(content=(
        "🎓 Welcome! Please provide:\n1) Country\n2) Bachelor's degree\n"
        "I will fetch all Master programs with deadlines, fees, and requirements."
    )).send()
@cl.on_message
async def main(message: cl.Message):
    text = message.content
    update_requirements(text)

    agent = cl.user_session.get("agent") or orchestrator
    user_inputs = cl.user_session.get("user_inputs") or user_requirements
    programs_list = cl.user_session.get("all_programs") or all_programs

    if not requirements_complete():
        result = Runner.run_sync(requirement_agent, text)
        await cl.Message(content=result.final_output).send()
        return

    # --- Fetch universities from Tavily ---
    tavily_results = await find_universities_raw(user_inputs["country"], user_inputs["degree"])

    session = aiohttp.ClientSession()
    try:
        for uni in tavily_results:
            uni_name = uni.get("title", "Unknown University")
            uni_url = uni.get("url", "")
            snippet = uni.get("content", "")

            if not uni_url:
                continue

            html_main = await fetch_html(session, uni_url)
            if not html_main:  # fallback if aiohttp fails
                html_main = await fetch_with_playwright(uni_url)

            candidate_links = await collect_links(session, uni_url, html_main, limit=6)

            candidate_urls = [uni_url] + candidate_links

            page_texts = []
            for cu in candidate_urls:
                h = await fetch_html(session, cu)
                if not h:  # fallback again for candidate pages
                    h = await fetch_with_playwright(cu)
                if not h:
                    page_texts.append(f"URL: {cu}\n<!-- Could not fetch page -->")
                else:
                    page_texts.append(f"URL: {cu}\n{clean_text(h, 12000)}")
            combined_text = "\n\n---PAGE_BREAK---\n\n".join(page_texts)

            # Call LLM to extract programs info
            prompt = (
                "Extract ALL Master programs explicitly confirmed on these pages. Include:\n"
                "- Program name\n- Admission requirements (GPA, tests, documents, language)\n"
                "- Deadlines and fees if listed\n"
                "- Official program link\n"
                "Return human-readable list in dict form."
            )

            try:
                # --- STREAMING ---
                stream_msg = cl.Message(content=f"🔍 Extracting info from {uni_name}...")
                await stream_msg.send()

                completion = await external_client.chat.completions.create(
                    model="gemini-2.5-flash",
                    messages=[
                        {"role": "system", "content": prompt},
                        {"role": "user", "content": combined_text[:40000]}
                    ],
                    max_tokens=2000,
                    temperature=0.0,
                    stream=True
                )

                model_text = ""
                async for chunk in completion:
                    delta = chunk.choices[0].delta.content or ""
                    if delta:
                        model_text += delta
                        await stream_msg.stream_token(delta)  # live token streaming

                await stream_msg.update()  # finalize message

            except Exception as e:
                model_text = snippet
                await cl.Message(content=f"⚠️ Failed to extract full info from {uni_name}. Showing snippet.").send()

            # Save program info incrementally
            programs_list.append({
                "University": uni_name,
                "Country": user_inputs["country"],
                "Degree": "Master",
                "Details": model_text,
                "URL": uni_url
            })

            # Immediate message after processing each university
            await cl.Message(content=f"✅ Processed: **{uni_name}**\n\n{model_text[:1000]}...").send()

        # Save CSV after all results
        if programs_list:
            df = pd.DataFrame(programs_list)
            csv_path = "C:\\Users\\Ammar\\OneDrive\\Desktop\\agent_as_a_tool\\master_programs_full.csv"
            df.to_csv(csv_path, index=False)
            await cl.Message(
                content=f"📑 Finished! Saved {len(programs_list)} programs to master_programs_full.csv",
                elements=[cl.File(name="master_programs_full.csv", path=csv_path)]
            ).send()
    finally:
        await session.close()
