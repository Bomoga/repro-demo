# Notewise (repro-demo)

A deliberately vulnerable demo target for [Repro](https://github.com/Bomoga/repro): a small notes
app with an AI assistant, with planted issues for Repro to detect, reproduce, repair, and prove
fixed. The list of planted issues is kept with the Repro team, outside this repo, so Repro's
agents work from the code alone.

**Don't deploy this.** The API keys and secrets in it are fake (random values, never valid
anywhere), and the third-party hosts are reserved `.example` and `.test` domains.

## What's in it

- `api/`: the notes API, AWS Lambda-style Python handlers over SQLite. Standard library only.
- `src/`: the assistant service ("ask about my notes"), an Express app that calls a hosted model.

## Run it

```
python3 -m api.dev_server        # notes API on :8000 (the X-User header stands in for sign-in)
npm install && npm start         # assistant service on :3000
```

```
curl -X POST localhost:8000/notes -H 'x-user: u-alice' -d '{"title": "groceries", "body": "eggs"}'
curl 'localhost:8000/notes?sort=title' -H 'x-user: u-alice'
curl 'localhost:3000/preview/formula?expr=12*4.5'
```

## Test it

```
npm test
```

Runs the Node tests and the Python tests. Neither needs `npm install` or network access, so the
suite runs as-is inside Repro's sandbox.
