Perfect 👍 you want **every command in the README wrapped inside fenced code blocks** so GitHub shows them properly formatted and copy-paste friendly. I’ll rewrite the README with **all commands and sample outputs in blocks**.

Here’s the **final detailed README.md** ⬇️

---

# 🎓 Master’s Program Finder Agent

An **AI-powered agent** that helps students find **Master’s programs** worldwide. It extracts admission requirements, deadlines, and fees from real university websites.

This project integrates:

* 🌐 **Tavily API** → real-time search engine
* 🤖 **Google Gemini (OpenAI-compatible API)** → LLM program extraction
* 🕹 **Playwright** → scrape dynamic JavaScript websites
* 💬 **Chainlit** → interactive conversational UI
* 📊 **Pandas** → save/export data

---

## ✨ Features

* 🔍 **Search universities** by country and degree
* 📝 **Scrape admission pages** (both static & JS-based)
* 🤖 **AI extracts**:

  * Program name
  * Admission requirements (tests, GPA, docs, language)
  * Deadlines
  * Fees
  * Official program links
* 📑 **Exports to CSV** (`master_programs_full.csv`)
* 💬 Interactive chatbot with **Chainlit**

---

## ⚡️ Quick Setup

### 1️⃣ Install [uv](https://docs.astral.sh/uv/)

```bash
pip install uv
```

### 2️⃣ Create a new environment

```bash
uv venv
```

### 3️⃣ Activate the environment

```bash
# Linux / macOS
source .venv/bin/activate

# Windows PowerShell
.venv\Scripts\Activate
```

### 4️⃣ Install dependencies

```bash
uv pip install -r requirements.txt
```

> If you don’t have `requirements.txt` yet, create it:

```txt
aiohttp
pandas
chainlit
python-dotenv
playwright
openai
tavily-python
```

### 5️⃣ Install Playwright browsers

```bash
playwright install chromium
```

---

## 🔑 Environment Variables

Create a `.env` file in the project root:

```env
# Google Gemini API Key (OpenAI-compatible endpoint)
GEMINI_API_KEY=your_gemini_api_key_here

# Tavily API Key
TAVILY_API_KEY=your_tavily_api_key_here
```

Create an example env file for others:

```bash
cp .env .env.example
```

---

## 🚀 Running the Project

Start the chat interface:

```bash
chainlit run main.py
```

Run with auto-reload (useful for dev):

```bash
chainlit run main.py -w
```

---

## 🛠 How It Works

1. **Start Chat**
   The agent asks for:

   ```text
   Country → e.g., Germany
   Degree  → e.g., BSIT
   ```

2. **Search**
   Uses Tavily API:

   ```text
   Searching universities in Germany offering Master’s programs for BSIT...
   ```

3. **Scrape**

   * Tries `aiohttp` first
   * Falls back to `Playwright` if blocked

4. **Program Extraction**
   Gemini extracts:

   ```json
   [
     {
       "program_name": "MSc Computer Science",
       "requirements": "IELTS 6.5, GPA ≥ 3.0, Recommendation letters",
       "deadlines": "15 July",
       "fees": "€4,000 per semester",
       "official_link": "https://www.hm.edu/cs-master"
     },
     {
       "program_name": "MSc Data Engineering",
       "requirements": "GRE optional, English proficiency required",
       "deadlines": "31 March",
       "fees": "Tuition-free",
       "official_link": "https://www.tum.de/data-eng"
     }
   ]
   ```

5. **Results Export**
   Automatically saved:

   ```bash
   📑 Finished! Saved 8 programs to master_programs_full.csv
   ```

---

## 📊 Example Output

**Sample CSV (`master_programs_full.csv`):**

```csv
University,Country,Degree,Details,URL
HM Hochschule München,Germany,Master,"MSc Computer Science – IELTS required, Deadline: 15 July, Fees: €4,000/semester, GPA ≥ 3.0",https://www.hm.edu/...
Technical University Munich,Germany,Master,"MSc Data Engineering – GRE optional, Deadline: 31 March, Tuition-free, Language: English",https://www.tum.de/...
```

---

## 🧩 Project Structure

```text
.
├── main.py                        # Main agent logic
├── requirements.txt               # Dependencies
├── .env                           # API keys
├── .env.example                   # Example env file
├── master_programs_full.csv        # Auto-generated results
└── README.md                      # Documentation
```

---

## 🧑‍💻 Development Commands

Format with Black:

```bash
uv pip install black
black main.py
```

Lint with Flake8:

```bash
uv pip install flake8
flake8 main.py
```

Export results to Excel:

```python
df.to_excel("master_programs_full.xlsx", index=False)
```

---

## 🔮 Roadmap

* [ ] Return results as **structured JSON** in addition to CSV
* [ ] Add filtering by tuition range or deadlines
* [ ] Docker support for deployment
* [ ] Multi-language support

---

## 🤝 Contributing

```bash
# 1. Fork the repo
git clone https://github.com/your-username/masters-program-finder.git

# 2. Create a new branch
git checkout -b feature/my-feature

# 3. Commit changes
git commit -m "Added my feature"

# 4. Push branch
git push origin feature/my-feature

# 5. Open Pull Request on GitHub
```

---


