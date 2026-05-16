
<p align="center">
  <pre>
  ____                            ____              _   _  __ _
 |  _ \ _ __ ___  _ __ ___       |___ \ _ __   ___ | |_(_)/ _(_)_   _
 | |_) | '__/ _ \| '_ ` _ \ _____  __) | '_ \ / _ \| __| | |_| | | | |
 |  __/| | | (_) | | | | | |_____|/ __/| | | | (_) | |_| |  _| | |_| |
 |_|   |_|  \___/|_| |_| |_|     |_____|_| |_|\___/ \__|_|_| |_|\__, |
                                                                  |___/
  </pre>
</p>

<p align="center">
  <strong>Prometheus AlertManager  →  Multi-Platform Notification Relay</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/github/actions/workflow/status/zyqtron/prom2alert/ci.yml?branch=master&label=CI&logo=github" alt="CI">
  <img src="https://img.shields.io/badge/python-3.8_|_3.9_|_3.10_|_3.11_|_3.12_|_3.13_|_3.14-blue?logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/tests-28_%E2%9C%93-brightgreen" alt="Tests">
  <img src="https://img.shields.io/badge/license-MIT-yellow" alt="License">
  <img src="https://img.shields.io/badge/version-5.0.0-informational" alt="Version">
  <img src="https://img.shields.io/badge/docker-ready-blue?logo=docker" alt="Docker">
  <img src="https://img.shields.io/badge/helm-ready-blue?logo=helm" alt="Helm">
</p>

---

**prom2notify** is a lightweight Python service that receives [Prometheus Alertmanager](https://github.com/prometheus/alertmanager) webhook notifications and relays them to **Microsoft Teams, Slack, Discord, Telegram, or any generic HTTP endpoint** — simultaneously, with a single deployment.

Forked from [prom2teams](https://github.com/idealista/prom2teams) and fully modernized with a pluggable multi-backend architecture, YAML-first configuration, and a clean extensible design.

---

## ✨ Features

- **Multi-backend** — Teams (Adaptive Cards), Slack, Discord, Telegram, Generic Webhook. All from one service.
- **YAML-first config** — human-readable, version-control-friendly configuration.
- **Legacy INI support** — drop-in replacement for existing prom2teams deployments.
- **Alert grouping** — collapse multiple alerts by name, severity, instance, or any label.
- **Label/annotation filtering** — exclude noisy labels from forwarded payloads.
- **Retry with backoff** — configurable per-backend retry policy via `tenacity`.
- **Payload truncation** — prevents oversized messages from being rejected by platforms.
- **Prometheus metrics** — built-in `/metrics` endpoint via `prometheus_flask_exporter`.
- **Swagger UI** — interactive API docs at `/v1` and `/v2`.
- **Docker & Helm** — container image and Kubernetes chart ready to go.
- **28 tests, zero flakiness.**

---

## 📦 Quick Start

### 1. Install

```bash
pip install prom2notify
```

### 2. Write a minimal config

Create `config.yaml`:

```yaml
backends:
  slack-alerts:
    type: slack
    url: https://hooks.slack.com/services/YOUR/TEAMS/WEBHOOK
```

### 3. Launch

```bash
prom2notify --configpath config.yaml
```

The server starts on `0.0.0.0:8080`, ready to receive Alertmanager webhooks.

### 4. Point Prometheus Alertmanager at it

```yaml
receivers:
  - name: 'prom2notify'
    webhook_configs:
      - url: 'http://prom2notify:8080/v2/slack-alerts'
```

---

## 🔧 Configuration

### YAML Configuration (recommended)

```yaml
# config.yaml
host: 0.0.0.0
port: 8080
loglevel: INFO
group_alerts_by: alertname

labels_excluded:
  - monitor
  - pod
annotations_excluded:
  - runbook_url

backends:
  # Microsoft Teams (Adaptive Cards)
  teams-ops:
    type: teams
    url: https://your-org.webhook.office.com/webhookb2/...
    config:
      TIMEOUT: 15
      RETRY_ENABLE: true
      RETRY_WAIT_TIME: 30

  # Slack
  slack-critical:
    type: slack
    url: https://hooks.slack.com/services/YOUR/TEAMS/WEBHOOK

  # Discord
  discord-general:
    type: discord
    url: https://discord.com/api/webhooks/YOUR/DISCORD/WEBHOOK

  # Telegram
  telegram-oncall:
    type: telegram
    url: https://api.telegram.org/bot<TOKEN>/sendMessage
    config:
      PARSE_MODE: HTML

  # Generic Webhook (for PagerDuty, Opsgenie, custom systems, etc.)
  opsgenie-proxy:
    type: generic
    url: https://api.opsgenie.com/v2/alerts
```

### INI Configuration (legacy prom2teams format)

```ini
[Microsoft Teams]
Connector: https://outlook.office.com/webhook/...

[Backends]
slack: slack|https://hooks.slack.com/services/YOUR/TEAMS/WEBHOOK
discord: discord|https://discord.com/api/webhooks/YOUR/DISCORD/WEBHOOK

[HTTP Server]
Host: 0.0.0.0
Port: 8080

[Group Alerts]
Field: alertname
```

### Environment Variables

| Variable | Description | Default |
|---|---|---|
| `APP_CONFIG_FILE` | Path to config file | — |
| `PROM2TEAMS_CONNECTOR` | Legacy single Teams webhook | — |
| `PROM2TEAMS_GROUP_ALERTS_BY` | Group alerts field | — |
| `PROM2TEAMS_PROMETHEUS_METRICS` | Enable `/metrics` | `false` |
| `APP_ENVIRONMENT` | Set to `pro` for file logging | — |

---

## 📨 Usage Examples

### Slack

```yaml
backends:
  slack:
    type: slack
    url: https://hooks.slack.com/services/YOUR/TEAMS/WEBHOOK
```

Alertmanager `POST` to `http://prom2notify:8080/v2/slack` produces:

```
[FIRING] HighCPU - 1 alert(s)
Attachment: ▐█▌ HighCPU
  alertname: HighCPU
  severity: critical
  instance: server01
```

### Discord

```yaml
backends:
  discord:
    type: discord
    url: https://discord.com/api/webhooks/YOUR/DISCORD/WEBHOOK
```

Embeds are rendered with color-coded status (red for firing, green for resolved), inline fields, and `username: Prometheus`.

### Telegram

```yaml
backends:
  telegram:
    type: telegram
    url: https://api.telegram.org/bot123456:ABC-DEF1234/sendMessage
    config:
      PARSE_MODE: HTML
```

Sends rich HTML messages with emoji indicators (`🔴` firing, `🟢` resolved) and bold/italic formatting.

### Microsoft Teams (Adaptive Cards)

```yaml
backends:
  teams:
    type: teams
    url: https://your-org.webhook.office.com/webhookb2/...
```

Uses the built-in Jinja2 Adaptive Card template (v1.4 cards with `FactSet` and `ColumnSet` layout) or your own custom template via `template: /path/to/teams.j2`.

### Generic Webhook

```yaml
backends:
  custom:
    type: generic
    url: https://my-monitoring-tool.internal/api/alerts
```

Forwards the raw Alertmanager JSON payload as-is to any HTTP endpoint — ideal for chaining with PagerDuty, Opsgenie, custom incident management tools, or middleware.

---

## 🏗 Architecture

```
                     ┌─────────────────────────────┐
                     │      Prometheus              │
                     │      Alertmanager            │
                     └──────────┬──────────────────┘
                                │ webhook POST
                                ▼
                     ┌─────────────────────────────┐
                     │       prom2notify            │
                     │  ┌───────────────────────┐   │
                     │  │   Flask REST API       │   │
                     │  │   /v1/<connector>      │   │
                     │  │   /v2/<connector>      │   │
                     │  └───────────┬───────────┘   │
                     │              │               │
                     │  ┌───────────▼───────────┐   │
                     │  │    AlertSender         │   │
                     │  │  · parse JSON          │   │
                     │  │  · group alerts        │   │
                     │  │  · route to backends   │   │
                     │  └───────────┬───────────┘   │
                     │              │               │
                     │    ┌─────────┼─────────┐     │
                     │    ▼         ▼         ▼     │
                     │  ┌─────┐ ┌─────┐ ┌───────┐  │
                     │  │Teams│ │Slack│ │Discord│  │
                     │  └──┬──┘ └──┬──┘ └───┬───┘  │
                     │     │       │        │       │
                     │  ┌──┴──┐ ┌──┴──┐ ┌───┴────┐ │
                     │  │Tele-│ │Gene-│ │  ...   │ │
                     │  │gram │ │ric  │ │        │ │
                     │  └─────┘ └─────┘ └────────┘ │
                     └─────────────────────────────┘
```

### Backend System

Each backend extends `NotifyBackend`, an abstract base class that provides:

- **Payload validation & truncation** — prevents oversized messages
- **HTTP session management** — `requests.Session` with JSON content-type
- **Retry with tenacity** — configurable wait time between attempts
- **Unified error handling** — all backends raise consistent exceptions

To add a new backend, subclass `NotifyBackend` and implement `_format_payload(alert_data) -> str`:

```python
from prom2notify.backends import NotifyBackend

class MyBackend(NotifyBackend):
    def _format_payload(self, alert_data: dict) -> str:
        # transform Alertmanager JSON into your platform's format
        return json.dumps({"text": alert_data["commonLabels"]["alertname"]})
```

Then register it in `prom2notify/app/sender.py` → `BACKEND_REGISTRY`.

---

## 🔄 Migration from prom2teams

prom2notify is a **drop-in replacement** for [prom2teams](https://github.com/idealista/prom2teams). Your existing INI config, Docker deployment, and Helm chart will work unchanged.

### Step-by-step

1. **Replace the package:**

   ```bash
   pip uninstall prom2teams
   pip install prom2notify
   ```

2. **Keep your config.** Your `config.ini` is fully backward-compatible:

   ```ini
   [Microsoft Teams]
   Connector: https://outlook.office.com/webhook/...
   ```

3. **Start as before:**

   ```bash
   prom2notify --configpath config.ini
   ```

### What's new after migration

| prom2teams | prom2notify |
|---|---|
| Teams only | Teams + Slack + Discord + Telegram + Generic |
| INI config only | INI + YAML |
| Single connector per instance | Multiple backends per instance |
| Apache 2.0 license | MIT license |

### Upgrade to YAML (recommended)

Once migrated, convert your INI config to YAML with one `sed`:

```bash
sed -n '/Connector:/s/.*Connector: //p' config.ini \
  | while read url; do
      echo "backends:"
      echo "  teams:"
      echo "    type: teams"
      echo "    url: $url"
    done > config.yaml
```

---

## 🐳 Docker

```bash
docker run -d \
  -e PROM2TEAMS_CONNECTOR="https://outlook.office.com/webhook/..." \
  -p 8089:8089 \
  idealista/prom2notify:5.0.0
```

Mount a custom config:

```bash
docker run -d \
  -v $(pwd)/config.yaml:/opt/prom2notify/config.yaml \
  -e APP_CONFIG_FILE=/opt/prom2notify/config.yaml \
  -p 8080:8080 \
  idealista/prom2notify:5.0.0
```

---

## ☸️ Helm

```bash
helm install prom2notify ./helm \
  --set prom2notify.connectors.teams=https://outlook.office.com/webhook/... \
  --set prom2notify.connectors.slack=https://hooks.slack.com/services/YOUR/TEAMS/WEBHOOK
```

---

## 🧪 Testing

```bash
git clone https://github.com/zyqtron/prom2notify
cd prom2notify
pip install -r requirements.txt
pytest tests/ -v
```

28 tests covering all backends, configuration loading, alert validation, JSON field handling, and edge cases.

---

## 📚 API Documentation

Interactive Swagger UI available at:

- **v1** — `http://localhost:8080/` (legacy single-connector endpoint)
- **v2** — `http://localhost:8080/v2` (multi-backend per-connector routing)

### Endpoints

| Method | Path | Description |
|---|---|---|
| `POST` | `/v2/<connector>` | Send alerts to a specific backend |
| `POST` | `/v1/<connector>` | Legacy v1 endpoint |
| `GET` | `/alive` | Liveness probe |
| `GET` | `/ready` | Readiness probe |
| `GET` | `/metrics` | Prometheus metrics (if enabled) |

---

## 🤝 Contributing

Contributions are welcome and appreciated!

1. **Fork** the repository at [github.com/zyqtron/prom2notify](https://github.com/zyqtron/prom2notify)
2. **Create a branch** — `feature/my-awesome-backend` or `fix/slack-timeout`
3. **Write tests** — every new backend or feature should include test coverage
4. **Run the suite** — `pytest tests/ -v` must pass with zero failures
5. **Submit a PR** against the `main` branch

### Adding a new backend

1. Create `prom2notify/backends/<platform>.py` extending `NotifyBackend`
2. Implement `_format_payload(self, alert_data: dict) -> str`
3. Register it in `BACKEND_REGISTRY` in `prom2notify/app/sender.py`
4. Add tests in `tests/test_backends.py`
5. Document the backend in this README

### Code style

- Python 3.8+ compatible
- Follow PEP 8 (flake8 linting is part of `setup_requires`)
- Use type hints for public methods
- Keep backends small and focused — single responsibility

---

## 📄 License

MIT © 2025 [Zyqtron](https://github.com/zyqtron)

Based on [prom2teams](https://github.com/idealista/prom2teams) by Idealista S.A.U.

---

<p align="center">
  <sub>Built with Python · Flask · Jinja2 · tenacity · requests</sub>
</p>
