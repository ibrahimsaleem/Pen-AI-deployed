import os
import subprocess
import time
import logging
import tempfile
import shutil
import uuid
from flask import Flask, request, render_template_string, jsonify
import google.generativeai as genai

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Read the default Gemini API key from environment variable (or use a fallback)
DEFAULT_GENAI_API_KEY = os.environ.get("GENAI_API_KEY", "YOUR_DEFAULT_API_KEY")
# Configure the module with the default API key
genai.configure(api_key=DEFAULT_GENAI_API_KEY)

app = Flask(__name__)

# In-memory store for analyses.
# Each entry is a dict with keys: "analysis" and "api_key"
analysis_store = {}

@app.route("/", methods=["GET"])
def index():
    html_template = '''
    <!doctype html>
    <html lang="en">
      <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
        <title>AI Pentesting Tool</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 800px;
                margin: 20px auto;
                padding: 20px;
                background-color: #f9f9f9;
            }
            .chatbox {
                background: #ffffff;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0 0 15px rgba(0, 0, 0, 0.1);
            }
            .chatbox h2 {
                margin-bottom: 15px;
                font-size: 26px;
                color: #222;
                text-align: center;
            }
            /* Conversation container */
            #conversation {
                margin-bottom: 20px;
                max-height: 500px;
                overflow-y: auto;
                border: 1px solid #ddd;
                border-radius: 5px;
                padding: 10px;
                background-color: #fafafa;
            }
            /* Message bubbles */
            .message {
                margin: 10px 0;
                padding: 10px;
                border-radius: 10px;
                width: fit-content;
                max-width: 80%;
                word-wrap: break-word;
            }
            .user-message {
                background-color: #d1ecf1;
                color: #0c5460;
                font-weight: bold;
                margin-left: auto;
            }
            .bot-message {
                background-color: #d4edda;
                color: #155724;
                margin-right: auto;
            }
            .error-message {
                background-color: #f8d7da;
                color: #721c24;
                margin-right: auto;
            }
            .prompt-input {
                width: 100%;
                padding: 12px;
                margin-top: 10px;
                border: 1px solid #ccc;
                border-radius: 5px;
                font-size: 16px;
                box-sizing: border-box;
            }
            .submit-btn {
                margin-top: 10px;
                padding: 12px;
                background-color: #007bff;
                color: white;
                border: none;
                border-radius: 5px;
                cursor: pointer;
                font-size: 16px;
            }
            .submit-btn:hover {
                opacity: 0.9;
            }
            pre {
                background: #e8f5e9;
                padding: 15px;
                border-radius: 5px;
                white-space: pre-wrap;
                margin-top: 5px;
            }
            .hidden {
                display: none;
            }
        </style>
      </head>
      <body>
        <div class="chatbox">
            <h2>AI Pentesting Tool</h2>
            
            <!-- Conversation area -->
            <div id="conversation"></div>
            
            <!-- Form for the initial scan -->
            <form id="chat-form">
                <!-- Optional field for user's Gemini API key -->
                <input type="text" id="api_key" name="api_key" class="prompt-input"
                       placeholder="Enter your Gemini API key (optional)" /><br>
                <input type="text" id="file_path" name="file_path" class="prompt-input"
                       placeholder="Enter folder path or GitHub URL to analyze..." /><br>
                <button type="submit" class="submit-btn">Analyze</button>
            </form>
            
            <!-- Post-analysis actions (hidden initially) -->
            <div id="post-analysis-actions" class="hidden">
                <!-- Ask more about the analysis -->
                <form id="ask-more-form">
                    <input type="hidden" id="analysis_id" name="analysis_id">
                    <input type="text" id="user_question" name="question" class="prompt-input"
                           placeholder="Ask more about the analysis..." />
                    <button type="submit" class="submit-btn" style="background-color: #ffc107;">Ask</button>
                </form>
                <!-- Start new scan -->
                <button type="button" id="new-scan-btn" class="submit-btn" style="background-color: #28a745;">
                    Start New Scan
                </button>
            </div>
        </div>
        
        <script>
            const conversation = document.getElementById("conversation");
            const chatForm = document.getElementById("chat-form");
            const apiKeyInput = document.getElementById("api_key");
            const filePathInput = document.getElementById("file_path");
            const postAnalysisActions = document.getElementById("post-analysis-actions");
            const askMoreForm = document.getElementById("ask-more-form");
            const analysisIdInput = document.getElementById("analysis_id");
            const newScanBtn = document.getElementById("new-scan-btn");

            // Handle the initial scan
            chatForm.addEventListener("submit", function(e) {
                e.preventDefault();
                const apiKey = apiKeyInput.value.trim();
                const filePath = filePathInput.value.trim();
                if (!filePath) return;

                conversation.innerHTML += "<div class='message user-message'><strong>You:</strong> " + filePath + "</div>";
                conversation.innerHTML += "<div class='message bot-message'>Processing... please wait.</div>";
                conversation.scrollTop = conversation.scrollHeight;
                filePathInput.value = "";

                // Build POST body including optional API key
                let body = "file_path=" + encodeURIComponent(filePath);
                if(apiKey) {
                    body += "&api_key=" + encodeURIComponent(apiKey);
                }

                // Send POST request to /analyze
                fetch("/analyze", {
                    method: "POST",
                    headers: {"Content-Type": "application/x-www-form-urlencoded"},
                    body: body
                })
                .then(response => response.json())
                .then(data => {
                    conversation.innerHTML += "<div class='message bot-message'><strong>Response:</strong>"
                        + "<pre>" + data.output + "</pre></div>";
                    chatForm.classList.add("hidden");
                    postAnalysisActions.classList.remove("hidden");
                    if (data.analysis_id) {
                        analysisIdInput.value = data.analysis_id;
                    }
                    conversation.scrollTop = conversation.scrollHeight;
                })
                .catch(error => {
                    conversation.innerHTML += "<div class='message error-message'><strong>Error:</strong> " + error + "</div>";
                    conversation.scrollTop = conversation.scrollHeight;
                });
            });

            // Handle follow-up questions
            askMoreForm.addEventListener("submit", function(e) {
                e.preventDefault();
                const question = document.getElementById("user_question").value.trim();
                if (!question) return;
                const analysisId = analysisIdInput.value;
                conversation.innerHTML += "<div class='message user-message'><strong>You (follow-up):</strong> " + question + "</div>";
                conversation.innerHTML += "<div class='message bot-message'>Asking AI...</div>";
                conversation.scrollTop = conversation.scrollHeight;
                document.getElementById("user_question").value = "";
                fetch("/ask_more", {
                    method: "POST",
                    headers: {"Content-Type": "application/x-www-form-urlencoded"},
                    body: "analysis_id=" + encodeURIComponent(analysisId) + "&question=" + encodeURIComponent(question)
                })
                .then(response => response.json())
                .then(data => {
                    conversation.innerHTML += "<div class='message bot-message'><strong>AI says:</strong>"
                        + "<pre>" + data.answer + "</pre></div>";
                    conversation.scrollTop = conversation.scrollHeight;
                })
                .catch(error => {
                    conversation.innerHTML += "<div class='message error-message'><strong>Error:</strong> " + error + "</div>";
                    conversation.scrollTop = conversation.scrollHeight;
                });
            });

            // Handle "Start New Scan"
            newScanBtn.addEventListener("click", () => {
                location.reload();
            });
        </script>
      </body>
    </html>
    '''
    return render_template_string(html_template)

@app.route("/analyze", methods=["POST"])
def analyze():
    """Handles the initial Bandit scan and AI analysis."""
    file_path = request.form.get("file_path")
    provided_api_key = request.form.get("api_key")
    # Use the provided API key if available; otherwise, use default.
    # (This changes the global configuration; note that this approach isn't thread-safe.)
    if provided_api_key:
        genai.configure(api_key=provided_api_key)
    else:
        genai.configure(api_key=DEFAULT_GENAI_API_KEY)
    result = []  # Messages to include in final output
    temp_dir = None

    try:
        logging.info("Starting analysis for: %s", file_path)
        # If a URL is provided, clone the GitHub repository temporarily.
        if file_path.startswith("http://") or file_path.startswith("https://"):
            temp_dir = tempfile.mkdtemp()
            logging.info("Cloning repository from URL: %s", file_path)
            subprocess.check_call(["git", "clone", file_path, temp_dir])
            target_path = temp_dir
        else:
            target_path = os.path.normpath(file_path)
            if not os.path.exists(target_path):
                return jsonify({"output": f"Error: The specified file or directory does not exist - {target_path}"})
        
        # Run Bandit on the target path
        bandit_output = run_bandit(target_path)
        save_bandit_report(bandit_output)
        logging.info("Bandit scan completed.")
        
        # Send the Bandit report to Gemini AI for analysis
        logging.info("Sending Bandit report to AI model...")
        ai_analysis = analyze_with_gemini(bandit_output)
        result.append("AI processing completed. Here are the results:")
        result.append(ai_analysis)

        # Generate a unique ID and store both the analysis and the API key used
        analysis_id = str(uuid.uuid4())
        analysis_store[analysis_id] = {
            "analysis": ai_analysis,
            "api_key": provided_api_key if provided_api_key else DEFAULT_GENAI_API_KEY
        }

        return jsonify({
            "output": "\n".join(result),
            "analysis_id": analysis_id
        })

    except Exception as e:
        logging.exception("An error occurred in the analysis pipeline")
        result.append(f"An error occurred: {e}")
        return jsonify({"output": "\n".join(result)})
    finally:
        # Clean up the cloned repository if one was used
        if file_path and (file_path.startswith("http://") or file_path.startswith("https://")):
            if temp_dir and os.path.exists(temp_dir):
                try:
                    shutil.rmtree(temp_dir)
                    logging.info("Cleaned up temporary directory: %s", temp_dir)
                except Exception as cleanup_error:
                    logging.error("Error during cleanup: %s", cleanup_error)

@app.route("/ask_more", methods=["POST"])
def ask_more():
    """Handles follow-up questions about the previously generated analysis."""
    analysis_id = request.form.get("analysis_id")
    question = request.form.get("question")
    if not analysis_id or analysis_id not in analysis_store:
        return jsonify({"answer": "No analysis found for this ID."})
    stored = analysis_store[analysis_id]
    original_analysis = stored["analysis"]
    stored_api_key = stored.get("api_key")
    # Reconfigure with the stored API key for follow-up
    genai.configure(api_key=stored_api_key)
    answer = ask_gemini_followup(original_analysis, question)
    return jsonify({"answer": answer})

def ask_gemini_followup(original_analysis, question):
    prompt = f"""
You previously provided the following security analysis:
{original_analysis}

Now the user asks:
{question}

Please answer based on the above context, clarifying or expanding the analysis as needed.
"""
    try:
        response = genai.generate_text(
            model="gemini-2.0-flash",
            prompt=prompt
        )
        if not response.text:
            return "Error: No response from AI for follow-up."
        return response.text.strip()
    except Exception as e:
        logging.exception("Error during follow-up analysis")
        return f"Error analyzing follow-up: {e}"

def run_bandit(target_path):
    """
    Runs Bandit on the provided file or directory and returns its output.
    """
    try:
        formatted_path = os.path.normpath(target_path)
        if not os.path.exists(formatted_path):
            logging.error("Bandit Error: File or directory not found - %s", formatted_path)
            return f"Error: The specified file or directory does not exist - {formatted_path}"
        process = subprocess.Popen(
            ["python", "-m", "bandit", "-r", formatted_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        stdout, stderr = process.communicate()
        full_output = stdout.strip() + "\n" + stderr.strip()
        if process.returncode != 0:
            logging.error("Bandit encountered an error: %s", stderr.strip())
            return f"Error running Bandit: {full_output}"
        return full_output
    except Exception as e:
        logging.exception("Exception occurred while running Bandit")
        return f"Error running Bandit: {e}"

def save_bandit_report(report):
    """
    Saves the latest Bandit report to a text file.
    """
    try:
        with open("bandit_report.txt", "w", encoding="utf-8") as file:
            file.write(report)
        logging.info("Bandit report saved to bandit_report.txt")
    except Exception as e:
        logging.error("Error saving Bandit report: %s", e)

def analyze_with_gemini(report):
    try:
        logging.info("Starting AI analysis with Google Gemini...")
        response = genai.generate_text(
            model="gemini-2.0-flash",
            prompt=f"""You are a penetration tester analyzing a security report. (If you did not see the report, tell 'no python file found in project'.)
Sort vulnerabilities by highest likelihood of successful exploitation and provide a concise penetration testing approach.
First give a short summary of the Analysis in 2-3 lines.

Analysis Format:
- File & Line Number
- Vulnerability Type & Severity
- Likelihood of Exploitation (High/Medium/Low)
- Exploitation Method (How an attacker can penetrate)
- Preconditions (Requirements for a successful attack)
- Potential Impact (What happens if exploited)
- Pentesting Strategy (How to test & validate)

Prioritize vulnerabilities that:
✅ Enable RCE, privilege escalation, or authentication bypass
✅ Are easy to exploit (e.g., weak validation, exposed endpoints)
✅ Affect publicly accessible or critical systems

Additional Deliverables:
- Exploit Code/Path → Demonstrates the vulnerability in action
- Fixed Code → Secure version mitigating the issue

Analyze the report below and return findings in this format (if you did not see the report tell 'no python file found in project'):

{report}
"""
        )
        if not response.text:
            logging.error("Error: No response from Gemini AI.")
            return "Error: AI analysis failed to generate a response."
        logging.info("Google Gemini analysis completed.")
        return response.text.strip()
    except Exception as e:
        logging.exception("Exception occurred while analyzing with Google Gemini")
        return f"Error analyzing with Gemini AI: {e}"


if __name__ == "__main__":
    app.run(debug=True)
