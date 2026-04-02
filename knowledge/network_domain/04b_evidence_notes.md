# Network Model v1 – Evidence Notes

## Purpose
This document records where important communication details were obtained from.

It helps distinguish between:
- information confirmed directly from code,
- information confirmed from environment or configuration files,
- information observed through packet capture,
- and standard default values declared by the owner.

This file is not the main communication model.
It is only a supporting traceability note.

---

## Confirmed from Code

### APP01 local portal process
- Observed in `index.js`
- Local Node.js application listens on `127.0.0.1:3000`
- Used behind Nginx reverse proxy

### Internal API application port
- Observed in Internal API code
- Internal API listens on port `9090`

### MariaDB port
- Observed in:
  - APP01 `db.js`
  - Internal API `db.js`
  - APP02 C# code
- Database communication uses port `3307`

### APP01 -> Internal API
- Observed in APP01 `.env`
- `INTERNAL_API_BASE_URL = http://192.168.30.10:9090`

### APP01 -> Vault
- Observed in APP01 `.env`
- `VAULT_ADDR = http://192.168.128.131:8200`

### Internal API -> Vault
- Observed in Internal API `.env`
- `VAULT_ADDR = http://192.168.128.131:8200`

### APP02 -> Vault
- Observed in APP02 C# code
- Default Vault address points to `http://192.168.128.131:8200`

---

## Confirmed from Configuration

### Nginx on APP01
- Observed in Nginx configuration
- Reverse proxy listens on `443`
- Proxies traffic to `https://127.0.0.1:3000`

### Keycloak current port
- Observed from running Keycloak output on IAM01
- Current observed state: `http://0.0.0.0:8080`
- This reflects the current environment and should not be treated as the final hardened exposure model

### Proxy port on PROXY01
- Observed from proxy configuration screenshot
- Proxy address: `192.168.10.10`
- Proxy port: `3128`

### Vault current port
- Observed from Vault startup screen
- Current observed state: `http://192.168.128.131:8200`

---

## Confirmed from Packet Capture

### IAM01 -> DC01 DNS
- Observed in Wireshark
- Source: `192.168.30.10`
- Destination: `192.168.128.10`
- Protocol: `UDP`
- Destination Port: `53`

---

## Confirmed by Owner

### Domain-joined systems using DC01 for DNS and time
The owner confirmed that the following systems are inside the domain and use DC01 for DNS and time:
- IAM01
- APP01
- APP02
- DB01

### Proxy usage
The owner confirmed that the following systems currently rely on PROXY01 for outbound Internet access:
- APP01
- APP02
- IAM01
- DB01
- DC01

### Admin laptop access model
The owner confirmed that the admin laptop currently has broad open access.

---

## Standard Default Values Declared by Owner

### IAM01 -> DC01 LDAP
- Port: `389/TCP`
- Used as the accepted standard default for the current model

### Domain-joined systems -> DC01 time service
- Port: `123/UDP`
- Used as the accepted standard default for the current model

---

## Notes
- This file is optional support documentation.
- The main model should still be read primarily from:
  - required flows,
  - port and protocol matrix,
  - blocked or unnecessary flows,
  - open questions and assumptions,
  - and target security intent.
- This file exists only to preserve traceability and confidence level for selected technical details.