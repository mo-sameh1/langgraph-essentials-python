# Local Ollama operations

## Everyday commands

```bash
systemctl --user status ollama
ollama list
ollama ps
ollama run langgraph-coder
journalctl --user -u ollama -f
```

The service listens only on `127.0.0.1:11434`; it is not exposed to the LAN.
The custom `langgraph-coder` model uses Qwen 3.5 9B with a 32K context window
and a coding-focused system prompt.

## Local coding agent

Run `codex-local` from a repository. It uses the isolated `ollama-course` Codex
profile and does not replace the normal ChatGPT-backed Codex configuration.

## Troubleshooting

Confirm the service and GPU path:

```bash
curl http://127.0.0.1:11434/api/version
nvidia-smi
ollama ps
```

After a model request, `ollama ps` reports whether the model is fully on the GPU
or split between GPU and CPU. A larger context consumes more memory; reduce
`OLLAMA_NUM_CTX` in `.env` if memory pressure matters more than context length.

