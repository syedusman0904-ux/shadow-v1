# Shadow Mobile

This directory is reserved for the Android client.

Recommended Version 1 stack:
- Kivy/KivyMD UI
- `websocket-client` or an asyncio-compatible WebSocket implementation
- Android Keystore-backed storage for sensitive local secrets
- HTTPS/WSS only in production

Version 2 must add the established E2EE protocol integration here. Do not place private keys on the backend.
