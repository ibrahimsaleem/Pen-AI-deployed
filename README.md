# AI Pentesting Tool

An open-source, AI-powered penetration testing tool that scans Python projects for vulnerabilities and provides prioritized analysis and remediation recommendations. It integrates:

- **Bandit** for scanning Python code.
- **Google Gemini AI** for remote analysis (optional, user-provided API key).
- **Ollama (LLaMA)** for local analysis via the Ollama CLI.
- **Flask** for the web interface (supporting real-time SSE or conversational UI in the updated version).

> **Note:** As of the latest update, you no longer need to hardcode your Gemini API key in the source code. Simply run the app, and when you open the web interface, you can optionally provide your API key. If you don’t have a Gemini API key, the tool will use a default or environment-provided key if available.

---

## Features

1. **Bandit Integration**  
   - Scans your Python files or folders for common security vulnerabilities (e.g., hardcoded credentials, weak cryptographic functions).

2. **AI Analysis**  
   - Leverages either Google Gemini AI (remote analysis) or Ollama (LLaMA) (local analysis via CLI) to generate penetration testing insights.
   - Provides a prioritized list of vulnerabilities, exploitation methods, potential impacts, and recommended fixes.

3. **Real-Time or Conversational Interface**  
   - Original SSE-based approach streams analysis results in real-time.
   - Updated version offers a single-page app with a conversation panel:
     - **Optional Gemini API Key Input** (overrides default key).
     - **Local Path or Public GitHub URL** support (temporarily clones the repo if a URL is given).
     - **Ask Follow-Up Questions** about detected vulnerabilities.
     - **Start New Scan** button to reset the conversation and analyze a new project.

4. **Open Source & Community-Driven**  
   - Contributions are welcome! Fork the project, create a branch, and submit a pull request.
   - All contributions will be reviewed and merged by the maintainers.

---

## Requirements

- Python 3.6+
- Flask
- Bandit
- Google Gemini AI Client (for remote Gemini analysis)
- Ollama CLI (for local LLaMA analysis, if desired)

---

## Installation

1. **Clone the Repository**
```
git clone https://github.com/ibrahimsaleem/pen-ai.git
cd pen-ai
  ```


2. **(Optional) Create and Activate a Virtual Environment**

**For Unix/Mac**:
 ```
python3 -m venv venv source venv/bin/activate
  ```


**For Windows**:
python -m venv venv venv\Scripts\activate


3. **Install Dependencies**
 ```
pip install -r requirements.txt
  ```

4. **Configure or Provide API Keys**

- **Optional Default Gemini API Key**:
  Set the environment variable `GENAI_API_KEY`:
  ```
  export GENAI_API_KEY="YOUR_DEFAULT_GEMINI_API_KEY"
  ```
  (Alternatively, you can just provide your key in the web UI if you prefer.)

- **Ollama (LLaMA)**:
  Ensure the Ollama CLI is installed and configured if you plan to use local analysis.

---

## Usage

### 1. Run the Flask Application

python app.py

### 2. Open Your Browser

Go to [http://127.0.0.1:5000](http://127.0.0.1:5000). You will see the **AI Pentesting Tool** interface.

### 3. Perform an Analysis

- **Optional**: Enter your Gemini API key in the first text box if you want to override the default or environment variable.
- **Enter Folder Path or GitHub URL**: Provide either a local path (e.g., `/path/to/python/project`) or a public GitHub repo URL (e.g., `https://github.com/user/repo`).
- Click **Analyze**.

The tool will:
1. (If URL) Clone the GitHub repository into a temporary folder.
2. Run Bandit on the specified path.
3. Generate a security report (`bandit_report.txt`).
4. Send the report to Gemini AI or Ollama (depending on configuration) for analysis.
5. Display the AI’s final report in the conversation window.

### 4. Ask Follow-Up Questions

- After the initial analysis, a follow-up form appears.
- You can ask clarifying questions like: “Which files have the highest severity issues?” or “How do I fix the insecure function usage?”
- The AI will respond based on the stored Bandit findings and prior analysis.

### 5. Start a New Scan

- Click **Start New Scan** to reset the conversation and analyze a new project or repository.

---

## Output Details

Based on the Bandit scan and AI analysis, the tool provides:

- **Summary** of the overall findings (2-3 lines).
- **Detailed Vulnerability Breakdown**, including:
  - File & Line Number
  - Vulnerability Type & Severity
  - Likelihood of Exploitation
  - Exploitation Method
  - Preconditions for Successful Exploit
  - Potential Impact
  - Pentesting Strategy
- **Exploit Code/Path** (if relevant)
- **Fixed Code** (recommended secure snippet)

You can then ask additional follow-up questions in the same UI for deeper insights.

---

## Project Structure

- **app.py (or Pen-AI-Gemni-Api.py)**  
  - Main Flask application.
  - Runs the Bandit scan.
  - Integrates with either the Google Gemini AI client or Ollama CLI for analysis.
  - Handles both the initial scan and any follow-up Q&A via in-memory storage of analysis.

- **requirements.txt**  
  - Lists all Python dependencies.

- **bandit_report.txt** (generated at runtime)  
  - Contains the most recent Bandit scan output.

---

## Contributing

We welcome contributions! To help improve this project, please follow these steps:

1. Fork the repository.
2. Create a new branch (e.g., `git checkout -b feature-xyz`).
3. Commit your changes (e.g., `git commit -m 'Add new feature'`).
4. Push your branch (e.g., `git push origin feature-xyz`).
5. Submit a pull request.

The maintainers will review your changes and, if everything looks good, merge them into the main branch.

---

## License

This project is licensed under the [MIT License](LICENSE).

---

## Disclaimer

This tool is provided for **educational and research** purposes only. Use it responsibly and only on codebases or systems for which you have explicit permission to perform security testing. The maintainers assume no liability for misuse or damage.
