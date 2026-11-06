# LOGIQ

LOGIQ is a Streamlit learning studio for maths, physics, and chemistry problems. It asks Gemini for a structured worked solution, key concepts, related ideas, and a quick verification where useful.

## Run locally (Windows PowerShell)

1. Use Python 3.10 or newer. In PowerShell, change into this project folder:

   ```powershell
   cd "$HOME\Documents\Codex\2026-11-06\i-want-you-to-build-a\outputs\logiq"
   ```

2. Install the dependencies into the same Python environment that will launch the app:

   ```powershell
   python -m pip install -r requirements.txt
   ```

3. Start Streamlit through Python. This works even when the `streamlit` command is not on `PATH`:

   ```powershell
   python -m streamlit run app.py
   ```

If PowerShell says `python` was not found, open Windows **Manage app execution aliases**. Toggle **Python (default)** `python.exe` and `python3.exe` Off and back On to refresh them, then close and reopen the terminal. If needed, refresh the Python install manager `py.exe` and `pymanager.exe` aliases the same way. Check with `python --version`.

If that still fails, use the interpreter path shown by VS Code's **Python: Select Interpreter** command. For the Python 3.14 installation in the supplied screenshot, the path is likely:

   ```powershell
   $py = "$env:LOCALAPPDATA\Python\pythoncore-3.14-64\python.exe"
   & $py -m pip install -r requirements.txt
   & $py -m streamlit run app.py
   ```

If that path does not exist on your computer, select the interpreter in VS Code, copy its full `python.exe` path, and replace the value assigned to `$py`.

4. Paste a Gemini API key in the app sidebar. You can also set one in PowerShell before launching:

   ```powershell
   $env:GEMINI_API_KEY = "YOUR_REAL_API_KEY"
   ```

   Create a key in [Google AI Studio](https://aistudio.google.com/app/apikey). Replace the placeholder with your own key; the sidebar option avoids setting an environment variable.

Questions and recent history stay in the active Streamlit session. Gemini interactions are sent with `store=False`.

## Deploy

Deploy this folder as a Streamlit app and add `GEMINI_API_KEY` to the deployment's secrets. `.streamlit/config.toml` sets the dark LOGIQ palette, and `assets/favicon.svg` contains the LOGIQ mark.
