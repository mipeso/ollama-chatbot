# Ollama Chatbot

This is a simple chatbot I made to experiment with LLM APIs. The app uses Ollama to run LLMs locally. To get started, install [Ollama](https://www.ollama.com) and pull any model you like.

> [!WARNING]
> Note that models can take up to hunderds of GBs of storage. Choose model according to your storage (and CPU) limits.

> [!IMPORTANT]
> I've tested the app only using a few models. At least gemma3 should work.

## Usage
To start using the app, first install dependencies in a Python virtual environment.

Create a virtual environment with
```
python3 -m venv ollama-chatbot
```
and activate it.

In the repository root, install dependencies into the virtual environment using
```
pip install -r requirements.txt
```

To start using the app, run
```
python3 -m chatbot.ollama_chatbot.py
```
