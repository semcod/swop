# Swop Manifest — Multi-format System Definition

This manifest demonstrates how a single README.md can host **multiple
definition formats** in codeblocks, all validated and synchronized with the
actual filesystem.

---

## 1. DOQL Data Layer (YAML)

Entities and databases are declared in DOQL format inside a `markpact:doql`
block. Swop parses this into a ``DoqlSpec`` and then into a ``ProjectGraph``.

```yaml markpact:doql
app_name: "SensorHub"
version: "0.1.0"

domain: "sensorhub.local"
languages:
  - python
  - typescript

entities:
  - name: Device
    fields:
      - name: id
        type: string
        required: true
      - name: serial
        type: string
        required: true
      - name: status
        type: string
        default: "active"
    audit: true

  - name: Reading
    fields:
      - name: id
        type: string
        required: true
      - name: device_id
        type: string
        required: true
      - name: value
        type: float
        required: true
      - name: unit
        type: string
        default: "celsius"
      - name: timestamp
        type: datetime
        required: true

databases:
  - name: main
    type: sqlite
    file: "data/sensorhub.db"

interfaces:
  - name: dashboard
    type: spa
    framework: react
    pages:
      - name: Devices
        path: /devices
        public: true
      - name: Readings
        path: /readings
        public: false

deploy:
  target: docker-compose
  rootless: false
```

---

## 2. Swop Graph Fragment (JSON)

Extra graph primitives can be injected directly via a `markpact:graph`
block. This merges into the ProjectGraph after the DOQL layer.

```json markpact:graph
{
  "services": {
    "mqtt-broker": {
      "routes": ["/publish", "/subscribe"]
    }
  }
}
```

---

## 3. Source Files (Python)

`markpact:file` blocks declare source files that are kept in sync with
the filesystem. Use ``swop generate --from-markpact manifest.md`` to
materialise them.

```python markpact:file path=src/models.py
from dataclasses import dataclass
from datetime import datetime

@dataclass
class Device:
    id: str
    serial: str
    status: str = "active"

@dataclass
class Reading:
    id: str
    device_id: str
    value: float
    unit: str = "celsius"
    timestamp: datetime
```

```python markpact:file path=src/api.py
from fastapi import FastAPI
from src.models import Device, Reading

app = FastAPI()

@app.get("/devices")
def list_devices():
    return {"devices": []}

@app.post("/readings")
def create_reading(reading: Reading):
    return {"id": reading.id, "value": reading.value}
```

---

## 4. Config Block (YAML)

Infrastructure and environment overrides live in a dedicated config block.

```yaml markpact:config
services:
  api:
    image: sensorhub/api:latest
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=sqlite:///data/sensorhub.db
  mqtt:
    image: eclipse-mosquitto:2
    ports:
      - "1883:1883"
```

---

## 5. Bootstrap Script

The bootstrap block is a special `markpact:bootstrap` script that can
be extracted and run to provision the system from scratch.

```python markpact:bootstrap
#!/usr/bin/env python3
"""Bootstrap the SensorHub runtime from this manifest."""
import subprocess
import sys
from pathlib import Path

MANIFEST = Path(sys.argv[1] if len(sys.argv) > 1 else "manifest.md")
assert MANIFEST.exists(), f"Manifest not found: {MANIFEST}"

# Extract markpact:file blocks and write them to disk.
# (Normally done by swop generate, shown here for completeness.)
print(f"[bootstrap] Manifest: {MANIFEST}")
print("[bootstrap] Run: swop generate --from-markpact manifest.md --sync")
```

---

## Usage

```bash
# Generate ProjectGraph from manifest
swop generate --from-markpact examples/manifest.md

# Generate + run sync + export YAML state
swop generate --from-markpact examples/manifest.md --sync --output-yaml state.yaml

# Generate + export docker-compose
swop generate --from-markpact examples/manifest.md --output-docker docker-compose.yml

# Check file sync status
python -m swop.markpact.sync_engine examples/manifest.md
```

---

<!-- markpact:include path=examples/shared.md -->
