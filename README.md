# Xeno Channel Service — Asynchronous Delivery Simulator & Webhook Dispatcher 📡

[![Python CI](https://github.com/LAKSHYA-NIGAM/xeno-channel-service/actions/workflows/ci.yml/badge.svg)](https://github.com/LAKSHYA-NIGAM/xeno-channel-service/actions/workflows/ci.yml)
[![Python Version](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue.svg)](https://www.python.org/)
[![Framework](https://img.shields.io/badge/framework-FastAPI-teal.svg)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Xeno Channel Service is a high-throughput, non-blocking messaging dispatcher microservice built with **FastAPI** and **asyncio**. It simulates realistic third-party messaging providers (WhatsApp, Email, SMS) for the [Xeno CRM](https://github.com/LAKSHYA-NIGAM/xeno-crm) ecosystem by generating progressive probabilistic delivery funnels and firing asynchronous webhook delivery receipts back to the CRM.

---

## 🏗️ Architecture & Asynchronous Callback Flow

```
[ Xeno CRM Gateway ]
         │
         │  1. POST /send (Batch of recipient messages)
         ▼
[ FastAPI Channel Service ]
         │
         ├──► 2. Immediate HTTP 202 Accepted (batch_id returned; CRM does not wait)
         │
         ▼  3. BackgroundTasks enqueues simulate_batch()
[ Probabilistic State Machine ]
         │
         ├─── WhatsApp : sent ➔ (95% delivered) ➔ (85% read) ➔ (75% clicked)
         ├─── Email    : sent ➔ (90% delivered) ➔ (75% opened) ➔ (60% clicked)
         └─── SMS      : sent ➔ (95% delivered) ➔ (50% clicked)
         │
         ▼  4. HTTP Webhook Callbacks (Exponential Backoff & Retries)
[ POST /api/receipts on Xeno CRM ]
```

---

## 🌟 Key Features

- **Non-Blocking Ingestion:** Acknowledges message batches immediately (`HTTP 202 Accepted`) and delegates all delivery simulation to background event loops.
- **Progressive Delivery Funnel:** Enforces realistic state transitions (e.g. messages cannot transition to `read` or `clicked` unless `delivered` succeeded first).
- **Resilient Webhook Dispatcher:** Includes exponential backoff retries (up to 3 attempts) via `httpx.AsyncClient` with custom timeouts.
- **Concurrency Throttling:** Governed by an `asyncio.Semaphore(15)` pool to protect webhook receivers from socket and port exhaustion.
- **Robust Schema Validation:** Powered by Pydantic models with custom channel whitelist validators and empty-batch guards.
- **Container Ready:** Includes production-optimized multi-stage `Dockerfile` and `render.yaml` configuration.

---

## 🔌 API Reference

### 1. Ingest Message Batch
`POST /send`

Enqueues an array of messages to be simulated asynchronously.

**Request Payload:**
```json
{
  "campaign_id": "cmp_8a9f3b12",
  "channel": "email",
  "messages": [
    {
      "recipient_id": "rec_001",
      "destination": "sarah.connor@example.com",
      "message": "Hi Sarah, your exclusive discount code is READY10!",
      "metadata": {
        "campaign_recipient_id": "cr_9012"
      }
    }
  ]
}
```

**Response (`202 Accepted`):**
```json
{
  "accepted": true,
  "batch_id": "batch_4f7e2a89c1",
  "message_count": 1
}
```

### 2. Health & Metrics Check
`GET /health`

**Response (`200 OK`):**
```json
{
  "status": "healthy",
  "service": "xeno-channel-service",
  "version": "1.0.0",
  "supported_channels": ["email", "sms", "whatsapp"],
  "timestamp": "2026-11-21T08:15:00.000000+00:00"
}
```

---

## 🔄 Webhook Callback Schema (Dispatched to CRM)

For each simulated lifecycle stage, the service POSTs an event receipt to `CRM_RECEIPT_URL` (default: `http://localhost:8000/api/receipts`):

```json
{
  "campaign_recipient_id": "cr_9012",
  "provider_message_id": "msg_0a8b2c4d6e8f",
  "event_type": "delivered",
  "event_timestamp": "2026-11-21T08:15:03.456123+00:00",
  "metadata": {
    "channel": "email"
  },
  "dedupe_key": "msg_0a8b2c4d6e8f:delivered"
}
```

---

## 🚀 Getting Started

### Local Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/LAKSHYA-NIGAM/xeno-channel-service.git
   cd xeno-channel-service
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the service:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
   ```

### Docker Setup
```bash
docker build -t xeno-channel-service .
docker run -p 8001:8001 xeno-channel-service
```

---

## 🧪 Running Automated Tests

The repository includes a comprehensive unit and integration test suite with zero external mock libraries required:

```bash
python -m unittest discover tests
```

### Test Coverage Highlights
- ✅ **Channel Whitelist:** Verifies support and error responses for WhatsApp, Email, and SMS.
- ✅ **Progressive Probability Chains:** Validates linear event hierarchy and failure branches.
- ✅ **Async Task Scheduling:** Mocks background task queues and verifies immediate `HTTP 202` response times.
- ✅ **Empty Payload Validation:** Enforces non-empty message batches.

---

## 📄 License
This project is licensed under the MIT License.
