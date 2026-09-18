import json
from pathlib import Path

ROUTES = Path('binary_hub/routes.json')
MANIFEST = Path('binary_hub/manifest.json')


def detect_type(name):
    ext = name.lower().split('.')[-1]
    if ext in ['png','jpg','jpeg','webp']:
        return 'images'
    if ext == 'pdf':
        return 'pdf'
    if ext in ['mp4','mov','mkv']:
        return 'video'
    if ext in ['mp3','wav']:
        return 'audio'
    return 'other'


def route_file(filename, destination='edit'):
    file_type = detect_type(filename)
    return {
        'file': filename,
        'type': file_type,
        'route': destination,
        'target': 'binary_hub/edit-queue' if destination == 'edit' else 'binary_hub/outbox/telegram'
    }

if __name__ == '__main__':
    print(json.dumps({'status':'ready','engine':'binary_intake_router'}))
