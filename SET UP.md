# Setup

Use two terminals.

## Terminal 1: Backend

```powershell
cd "e:\Java\Project\Project Ai"
E:/Anaconda/Installed/python.exe -m uvicorn backend.main:app --host 127.0.0.1 --port 8012
```

## Terminal 2: Frontend

```powershell
cd "e:\Java\Project\Project Ai\frontend"
npm.cmd run dev -- --host 127.0.0.1 --port 5173
```

## Open

- http://127.0.0.1:5173/index.html
- http://127.0.0.1:8012/docs

## Notes

- Task analysis path is local-model based.
- OpenAI is used in chat assistant flow.
