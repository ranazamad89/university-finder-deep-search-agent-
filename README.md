🎓 Master’s Program Finder Agent

This project is an AI-powered agent that helps students discover Master’s programs worldwide, fetching details such as admission requirements, deadlines, and fees from university websites in real-time.

It combines:

Tavily API
 for web search

Google Gemini (OpenAI-compatible API)
 for program extraction

Playwright
 for JavaScript-rendered pages

Chainlit
 for interactive chat UI

Pandas for saving results to CSV

✨ Features

🔍 Search universities in a specific country offering Master’s programs for a given degree.

📄 Scrape university websites (supports both static and dynamic pages).

🤖 Use Gemini LLM to extract structured program details:

Program name

Admission requirements (GPA, documents, tests, language proficiency)

Application deadlines

Tuition fees

Official program links

📊 Export results into CSV for further analysis.

💬 Interactive chat interface with Chainlit.

⚡️ Setup Instructions
1. Install uv

This project uses uv
 for managing environments.

# Install uv (if not already installed)
pip install uv

2. Create a new environment
uv venv

3. Activate environment
# On Linux/Mac
source .venv/bin/activate

# On Windows (PowerShell)
.venv\Scripts\Activate

4. Install dependencies
uv pip install -r requirements.txt

📦 Dependencies

Create a requirements.txt with:

aiohttp
pandas
chainlit
python-dotenv
playwright
openai
tavily-python


After installing Playwright, make sure to install browsers:

playwright install chromium

🔑 Environment Variables

Create a .env file in the project root:

GEMINI_API_KEY=your_gemini_api_key
TAVILY_API_KEY=your_tavily_api_key

🚀 Running the Project

Run with Chainlit:

chainlit run main.py


This starts a local UI where you can chat with the agent.

🛠 Workflow

Start Chat
The agent asks for:

Country (e.g., Germany)

Bachelor’s degree (e.g., BSIT)

Search
Tavily API searches for universities matching the requirements.

Scraping

First, tries fetching with aiohttp.

If blocked or the site requires JavaScript, falls back to Playwright.

Program Extraction
Gemini model parses the scraped content and extracts details into structured text.

Results Export
Saves everything into master_programs_full.csv.

📊 Example Output
University	Country	Degree	Details	URL
HM Hochschule München	Germany	Master	Program: MSc Computer Science …	https://www.hm.edu/
...
🧩 Project Structure
.
├── main.py               # Main entry point
├── requirements.txt      # Dependencies
├── .env                  # API keys
├── master_programs_full.csv  # Auto-generated results
└── README.md             # Documentation

🔮 Roadmap

 Export results in JSON in addition to CSV

 Improve Gemini prompt for fully structured outputs

 Add support for filtering by tuition range

 Docker support for easy deployment

🤝 Contributing

Pull requests are welcome! For major changes, please open an issue first to discuss what you’d like to change.
