## Python Bot

Quick-start guide for configuring and running the Word Guess bot with the `uv` package manager.

### Requirements
- Python 3.12.6
- [uv](https://github.com/astral-sh/uv) installed.
- OpenAI API key with access to GPT-5/GPT-4 series models. If you have not got your key yet, follow the instructions given [here](https://spl.solitontech.ai/docs/setup-tools/creating-openai-api-key/).

### Install Dependencies with uv
```bash
uv sync
```
- The command creates a virtual environment under `.venv` and installs all dependencies declared in `pyproject.toml`.

### Configure OpenAI Api Key
- Create a `.env` file.
```
OPENAI_API_KEY = <your_open_ai_api_key>
```
- Add the above line to the `.env`, replacing the place holder with the actual api key.

### Select the Kernel
- Open the notebook in VS Code or Jupyter and choose the Python kernel that points to the `.venv` created by `uv sync`. This ensures the bot runs with the correct dependencies and environment variables loaded from `.env`.

### Run the notebook
- **VS Code**: Open [`wordle/wordle_starter_bot.ipynb`](wordle/wordle_starter_bot.ipynb) in the editor, select the `.venv` kernel, and run each cell sequentially with `Ctrl+Enter` (or the Run Cell buttons). The final cell starts the WebSocket listener and keeps running until you interrupt it.
- **JupyterLab**: Launch JupyterLab via `uv run jupyter lab`, open the same notebook, choose the `.venv` kernel from the upper right, and run the cells from top to bottom.

### Explore OpenAI
- Dive deeper into platform capabilities and model guidance in [OpenAI Bytes](https://spl.solitontech.ai/docs/learning/openai-bytes).