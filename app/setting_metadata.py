import json
from pathlib import Path


with (Path(__file__).parent / 'logic' / 'setting' / 'metadata.json').open(encoding='utf-8') as metadata_file:
    SETTING_METADATA = json.load(metadata_file)
