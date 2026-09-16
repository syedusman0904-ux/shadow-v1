# Shadow Security Notes

## Version 1 security boundary

This release provides transport/application security controls but **does not provide end-to-end encryption**.

The backend can read Version 1 message bodies. This is intentional for the first incremental milestone and must be replaced before an E2EE privacy claim.

## Passwords

Passwords are hashed with Argon2id. Plaintext passwords are never stored or logged.

## Sessions

Refresh tokens are random opaque values. Only a SHA-256 digest is stored server-side. Refresh-token rotation invalidates the previous token.

Access tokens are short-lived JWTs.

## WebSockets

A WebSocket must authenticate using an access token. It is authorized to send only as the authenticated user. Message IDs are server-generated UUIDs.

## Database

SQLAlchemy uses parameterized queries/ORM operations. Never concatenate SQL from user input.

## Threat model items for later versions

- Account takeover
- Token theft
- Malicious clients
- Replay/duplicate messages
- Device compromise
- Metadata leakage
- Key compromise
- Multi-device synchronization
- Group membership changes
- Push-notification leakage
- Malicious media
- Abuse/rate-limit bypass

## E2EE roadmap

Version 2 must integrate an established, independently reviewed messaging protocol/library. Private keys must remain on devices. The server should receive ciphertext and protocol metadata only.

Do not implement a new ratchet, key exchange, group protocol, or encryption scheme from scratch.

## Operational rules

Never log passwords, tokens, private keys, encryption keys, or plaintext messages.

Use HTTPS/WSS in production and rotate secrets.
