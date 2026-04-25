# Network – Evidence Notes

<!--
  CATEGORY: Evidence (traceability) — OPTIONAL
  Include this folder only when facts come from multiple evidence
  sources and traceability adds value. For simpler domains, inline
  confidence tags in other files may be sufficient.
-->

## Purpose
Record where and how important facts were confirmed.
This is supporting traceability, not the main model.

---

## From Code

### APP01 local portal process
- **Observed:** The local Node.js portal process listens on `127.0.0.1:3000` and is reached locally by the Nginx HTTPS front-end on APP01.
- **Location:** `index.js`
- **Related entry:** Technical matrix entry for `Nginx on APP01 → Local portal process on APP01`

### Internal API application port
- **Observed:** The Internal API service listens on port `9090`.
- **Location:** Internal API code
- **Related entry:** Technical matrix entry for `APP01 → Internal API on IAM01`

### MariaDB port
- **Observed:** MariaDB-related database communication uses port `3307`.
- **Location:** APP01 `db.js`, Internal API `db.js`, APP02 C# code
- **Related entry:** Technical matrix entries for `APP01 → DB01`, `APP02 → DB01`, and `IAM01 → DB01`

### APP01 → Internal API
- **Observed:** APP01 uses `INTERNAL_API_BASE_URL = http://192.168.30.10:9090`
- **Location:** APP01 `.env`
- **Related entry:** Technical matrix entry for `APP01 → Internal API on IAM01`

### APP01 → Vault
- **Observed:** APP01 uses `VAULT_ADDR = http://192.168.128.131:8200`
- **Location:** APP01 `.env`
- **Related entry:** Technical matrix entry for `APP01 → Vault on DB01`

### IAM01 → Vault
- **Observed:** IAM01 uses `VAULT_ADDR = http://192.168.128.131:8200`
- **Location:** Internal API `.env`
- **Related entry:** Technical matrix entry for `IAM01 → Vault on DB01`

### APP02 → Vault
- **Observed:** APP02 uses a default Vault address that points to `http://192.168.128.131:8200`
- **Location:** APP02 C# code
- **Related entry:** Technical matrix entry for `APP02 → Vault on DB01`

---

## From Configuration

### Nginx on APP01
- **Observed:** The local Nginx HTTPS front-end on APP01 listens on `443` and forwards traffic to `https://127.0.0.1:3000`
- **Location:** Nginx configuration
- **Related entry:** Technical matrix entries for `Client / browser → APP01 (Nginx)` and `Nginx on APP01 → Local portal process on APP01`

### Keycloak current port
- **Observed:** The current observed Keycloak listener is `http://0.0.0.0:8080`
- **Location:** Running Keycloak output on IAM01
- **Related entry:** Technical matrix entries for `APP01 → IAM01 (Keycloak OIDC)` and `APP02 → IAM01 (Keycloak Device Flow)`

### Proxy port on PROXY01
- **Observed:** PROXY01 is observed at `192.168.10.10` and proxy port `3128`
- **Location:** Proxy configuration screenshot
- **Related entry:** Technical matrix entries for outbound proxy path flows to `PROXY01`

### Vault current port
- **Observed:** The current observed Vault listener is `http://192.168.128.131:8200`
- **Location:** Vault startup screen
- **Related entry:** Technical matrix entries for Vault-related flows to `DB01`

---

## From Observation

### IAM01 → DC01-CYBERAUDIT (DNS)
- **Observed:** Source `192.168.30.10` communicates with destination `192.168.128.10` over `UDP` destination port `53`
- **Method:** Wireshark
- **Related entry:** Technical matrix entry for `IAM01 → DC01-CYBERAUDIT (DNS)`

---

## From Owner Declaration

### Domain-joined systems using DC01 for DNS and time
- **Confirmed:** IAM01, APP01, APP02, and DB01 are domain-joined systems and use DC01 for DNS and time-related services.
- **Method:** Owner confirmation
- **Related entry:** Technical matrix entries for DNS and time-related flows from IAM01, APP01, APP02, and DB01 to `DC01-CYBERAUDIT`

### Proxy usage
- **Confirmed:** APP01, APP02, IAM01, DB01, and DC01 currently use PROXY01 for outbound Internet access.
- **Method:** Owner confirmation
- **Related entry:** Required flow and technical matrix entries for outbound proxy path flows to `PROXY01`

### Admin laptop access model
- **Confirmed:** The Admin laptop currently has broad open outbound access.
- **Method:** Owner confirmation
- **Related entry:** Required flow and technical matrix entries for `Admin laptop → target systems`

---

## Standard Defaults Accepted

### IAM01 → DC01-CYBERAUDIT (LDAP federation)
- **Value:** `389/TCP`
- **Basis:** Standard default accepted by owner

### Domain-joined systems → DC01-CYBERAUDIT (Time service)
- **Value:** `123/UDP`
- **Basis:** Standard default accepted by owner