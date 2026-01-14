# GG Gateway Integration Documentation

This document describes the architecture, API, and event stream of the Python GG Gateway service. It is designed to help an AI agent implement the corresponding Laravel dashboard and worker consumers.

## 1. System Architecture

The system follows a **Multi-Bot Gateway** pattern:

*   **GG Gateway (Python)**: Holds persistent TCP socket connections to Gadu-Gadu servers for multiple bots simultaneously.
*   **Laravel Application**: Manages bot credentials, business logic, and user interactions.
*   **Redis**: Acts as the communication bridge.
    *   **Control Plane**: Laravel calls HTTP API on Python Gateway to Connect/Disconnect/Send.
    *   **Data Plane**: Python Gateway pushes events (messages, status changes) to a Redis List.

## 2. Redis Event Stream

All incoming events from all bots are pushed to a single Redis List.

*   **Key**: `gg:events`
*   **Type**: `List` (Use `BLPOP` or `RPOP` to consume)
*   **Format**: JSON

### Envelope Structure

Every event is wrapped in a standard envelope:

```json
{
  "bot_uin": 123456,          // The UIN of the bot that received the event
  "event": "message",         // Event Type: 'message', 'roulette', 'system', 'status', 'typing'
  "timestamp": 1678886655.12, // Unix timestamp (float)
  "data": { ... }             // Event-specific payload
}
```

### Event Types & Payloads

#### `message`
Triggered when a bot receives a private message.

```json
{
  "sender": 789012,           // UIN of the user who sent the message
  "content": "Hello world!",  // HTML/Text content of the message
  "packet_timestamp": 123456  // Internal GG protocol timestamp
}
```

#### `roulette`
Triggered when the random chat (roulette) finds a partner or result.

```json
{
  // Content varies based on GG API response
  "user": {
      "uin": 999888,
      "gender": 1,
      ...
  }
}
```

#### `system`
Internal system events regarding the bot's connection health.

```json
{
  "status": "logged_in"       // 'logged_in', 'login_failed'
}
```

#### `status`
Triggered when a contact changes their status. **Must be explicitly subscribed.**

```json
{
  "user_uin": 444555,
  "status": 2,                // Status ID (e.g., 2 = Available, 3 = Busy)
  "description": "At work"
}
```

#### `typing`
Triggered when a user starts/stops typing. **Must be explicitly subscribed.**

```json
{
  "sender": 789012,
  "type": 1                   // >0 = Typing, 0 = Stopped
}
```

## 3. HTTP Control API

The Gateway exposes a REST API on port `8080`.

### Bot Management

#### Connect Bot
`POST /bot/{uin}/login`

Connects a bot session. If already connected, returns error 400.

**Payload:**
```json
{
  "password": "secret_password",
  "events": ["message", "roulette", "system", "status", "typing"], // Events to subscribe to
  "settings": {             // Optional: Roulette filtering settings
    "gender": 1,            // 1=Male, 2=Female
    "min_age": 18,
    "max_age": 100
  }
}
```

**Response:**
```json
{ "status": "connecting", "uin": 123456 }
```

#### Disconnect Bot
`POST /bot/{uin}/logout`

Disconnects the bot and removes it from memory.

**Response:**
```json
{ "status": "disconnected", "uin": 123456 }
```

#### Get Bot Status
`GET /bot/{uin}`

Returns the connection state of a specific bot.

**Response:**
```json
{
  "uin": 123456,
  "connected": true,
  "events": ["message", "system"]
}
```

### Controls

#### Send Message
`POST /bot/{uin}/message`

Sends a private message to another user.

**Payload:**
```json
{
  "recipient": 789012,
  "content": "Hello from Laravel!"
}
```

#### Start Roulette
`POST /bot/{uin}/roulette`

Triggers the "Draw Stranger" action for the roulette.

**Response:**
```json
{ "status": "started", "api_response": { ... } }
```

### System Status

#### Global Status
`GET /status`

Returns a list of all active bots managed by the container.

**Response:**
```json
{
  "active_bots_count": 5,
  "bots": [
    { "uin": 123, "connected": true, "events": [...] },
    { "uin": 456, "connected": false, "events": [...] }
  ]
}
```

## 4. Default Configuration

The container can auto-start a default bot if credentials are provided in `.env`.

*   `GG_UIN`: Default Bot UIN
*   `GG_PASSWORD`: Default Bot Password
*   `REDIS_HOST`: Redis hostname (default: `redis`)
*   `REDIS_PORT`: Redis port (default: `6379`)
