import json, os, time

PATH = os.path.expanduser('~/.termux-ai/history.jsonl')

def record(kind, data):
    os.makedirs(os.path.dirname(PATH), exist_ok=True)
    with open(PATH, 'a', encoding='utf-8') as f:
        f.write(json.dumps({'time': time.time(), 'kind': kind, **data}, ensure_ascii=False) + '\n')
