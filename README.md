# Engineering Interview Practice Tool

A CLI-based tool designed to help candidates practice for engineering interviews at modern communications and SaaS companies. This tool simulates both **Coding** and **System Design** rounds, providing real-time interaction and structured feedback.

## 🚀 Features

- **Coding Interview Simulation (60 min):** Analyze complex datasets (GitLab CI/CD metrics, Jira sprint data) and generate executive summaries.
- **System Design Interview Simulation (60 min):** Design scalable architectures for real-world scenarios like real-time call intelligence or AI-powered support systems.
- **AI Interviewer:** Powered by Claude (Anthropic), the interviewer acts as a senior/staff engineer, asking clarifying questions and probing your decisions.
- **Structured Feedback:** Receive a detailed rubric-based evaluation at the end of each session.

## 🛠️ Setup

### Prerequisites

- Python 3.8+
- An Anthropic API Key

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Felipe-Cal/engineering-interviewer.git
   cd engineering-interviewer
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment:**
   Copy the example environment file and add your API key:
   ```bash
   cp .env.example .env
   ```
   Edit `.env` and replace `your_api_key_here` with your actual Anthropic API key.

## 🏃 Usage

Launch the practice tool by running:

```bash
python3 practice.py
```

### Commands during interview:
- `done`: Wrap up the interview and request your structured evaluation.
- `time`: Check how much time you have remaining.
- `quit`: Exit the session without an evaluation.

## 📂 Project Structure

- `practice.py`: The main entry point and interview engine.
- `data/`: Sample datasets for coding exercises.
- `ex1.py` / `ex2.py`: Placeholder files for your coding implementation.

## ⚖️ License

MIT
