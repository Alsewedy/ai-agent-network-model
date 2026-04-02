# Network Model v1 – Port and Protocol Matrix

## Purpose
This document records the known and required ports and protocols used by the main systems in the homelab environment.

It is intended to support:
- future firewall hardening,
- service-specific access control,
- AI-assisted reasoning about required communication,
- and later comparison between broad build-phase access and exact least-privilege communication needs.

This document should distinguish clearly between:
- confirmed communication details,
- and items that still require confirmation,
- and standard default values declared by the owner.

---

## Flow: Client -> APP01 (Nginx)
**Source:** Client / browser
**Destination:** APP01
**Service:** Nginx reverse proxy
**Protocol:** HTTPS
**Port:** 443
**Direction:** Inbound to APP01
**Purpose:** Customer-facing secure access to the portal
**Status:** Confirmed

---

## Flow: Nginx on APP01 -> local portal process on APP01
**Source:** Nginx on APP01
**Destination:** Local Node.js portal process on APP01
**Service:** Reverse proxy forwarding
**Protocol:** HTTPS
**Port:** 3000
**Direction:** Local internal flow on APP01
**Purpose:** Forward portal traffic from Nginx to the local Express application
**Status:** Confirmed

---

## Flow: APP01 -> IAM01
**Source:** APP01
**Destination:** IAM01
**Service:** Keycloak OIDC
**Protocol:** HTTP
**Port:** 8080
**Direction:** Outbound from APP01
**Purpose:** Customer authentication and OIDC interaction
**Status:** Confirmed for current observed environment

---

## Flow: APP01 -> DB01
**Source:** APP01
**Destination:** DB01
**Service:** MariaDB (saams_portal_db)
**Protocol:** MySQL over TLS / mTLS
**Port:** 3307
**Direction:** Outbound from APP01
**Purpose:** Portal-side database access
**Status:** Confirmed

---

## Flow: APP01 -> Vault on DB01
**Source:** APP01
**Destination:** DB01
**Service:** Vault
**Protocol:** HTTP
**Port:** 8200
**Direction:** Outbound from APP01
**Purpose:** Retrieve database credentials and client certificates
**Status:** Confirmed

---

## Flow: APP01 -> Internal API on IAM01
**Source:** APP01
**Destination:** IAM01
**Service:** Internal API
**Protocol:** HTTP
**Port:** 9090
**Direction:** Outbound from APP01
**Purpose:** Create internal requests, retrieve status updates, and download reports
**Status:** Confirmed

---

## Flow: APP02 -> IAM01
**Source:** APP02
**Destination:** IAM01
**Service:** Keycloak Device Flow
**Protocol:** HTTP
**Port:** 8080
**Direction:** Outbound from APP02
**Purpose:** Employee authentication through Device Flow and MFA
**Status:** Confirmed for current observed environment

---

## Flow: APP02 -> DB01
**Source:** APP02
**Destination:** DB01
**Service:** MariaDB (audit_system_db)
**Protocol:** MySQL over TLS / mTLS
**Port:** 3307
**Direction:** Outbound from APP02
**Purpose:** Internal audit workflow database access
**Status:** Confirmed

---

## Flow: APP02 -> Vault on DB01
**Source:** APP02
**Destination:** DB01
**Service:** Vault
**Protocol:** HTTP
**Port:** 8200
**Direction:** Outbound from APP02
**Purpose:** Retrieve database credentials, certificates, and Keycloak configuration
**Status:** Confirmed

---

## Flow: IAM01 / Internal API -> DB01
**Source:** IAM01
**Destination:** DB01
**Service:** MariaDB (audit_system_db)
**Protocol:** MySQL over TLS / mTLS
**Port:** 3307
**Direction:** Outbound from IAM01
**Purpose:** Internal API database access
**Status:** Confirmed

---

## Flow: IAM01 / Internal API -> Vault on DB01
**Source:** IAM01
**Destination:** DB01
**Service:** Vault
**Protocol:** HTTP
**Port:** 8200
**Direction:** Outbound from IAM01
**Purpose:** Retrieve database credentials and certificates for Internal API database access
**Status:** Confirmed

---

## Flow: IAM01 -> DC01-CYBERAUDIT (DNS)
**Source:** IAM01
**Destination:** DC01-CYBERAUDIT
**Service:** DNS
**Protocol:** UDP
**Port:** 53
**Direction:** Outbound from IAM01
**Purpose:** Internal name resolution
**Status:** Confirmed

---

## Flow: IAM01 -> DC01-CYBERAUDIT (LDAP)
**Source:** IAM01
**Destination:** DC01-CYBERAUDIT
**Service:** LDAP federation
**Protocol:** TCP
**Port:** 389
**Direction:** Outbound from IAM01
**Purpose:** Active Directory federation for Keycloak
**Status:** Standard default declared by owner

---

## Flow: IAM01 -> DC01-CYBERAUDIT (Time)
**Source:** IAM01
**Destination:** DC01-CYBERAUDIT
**Service:** Time / NTP
**Protocol:** UDP
**Port:** 123
**Direction:** Outbound from IAM01
**Purpose:** Time synchronization
**Status:** Standard default declared by owner

---

## Flow: APP01 -> DC01-CYBERAUDIT (DNS)
**Source:** APP01
**Destination:** DC01-CYBERAUDIT
**Service:** DNS
**Protocol:** UDP
**Port:** 53
**Direction:** Outbound from APP01
**Purpose:** Internal name resolution
**Status:** Standardized across domain-joined systems, confirmed by owner

---

## Flow: APP01 -> DC01-CYBERAUDIT (Time)
**Source:** APP01
**Destination:** DC01-CYBERAUDIT
**Service:** Time / NTP
**Protocol:** UDP
**Port:** 123
**Direction:** Outbound from APP01
**Purpose:** Time synchronization
**Status:** Standard default declared by owner

---

## Flow: APP02 -> DC01-CYBERAUDIT (DNS)
**Source:** APP02
**Destination:** DC01-CYBERAUDIT
**Service:** DNS
**Protocol:** UDP
**Port:** 53
**Direction:** Outbound from APP02
**Purpose:** Internal name resolution
**Status:** Standardized across domain-joined systems, confirmed by owner

---

## Flow: APP02 -> DC01-CYBERAUDIT (Time)
**Source:** APP02
**Destination:** DC01-CYBERAUDIT
**Service:** Time / NTP
**Protocol:** UDP
**Port:** 123
**Direction:** Outbound from APP02
**Purpose:** Time synchronization
**Status:** Standard default declared by owner

---

## Flow: DB01 -> DC01-CYBERAUDIT (DNS)
**Source:** DB01
**Destination:** DC01-CYBERAUDIT
**Service:** DNS
**Protocol:** UDP
**Port:** 53
**Direction:** Outbound from DB01
**Purpose:** Internal name resolution
**Status:** Standardized across domain-joined systems, confirmed by owner

---

## Flow: DB01 -> DC01-CYBERAUDIT (Time)
**Source:** DB01
**Destination:** DC01-CYBERAUDIT
**Service:** Time / NTP
**Protocol:** UDP
**Port:** 123
**Direction:** Outbound from DB01
**Purpose:** Time synchronization
**Status:** Standard default declared by owner

---

## Flow: DC01-CYBERAUDIT -> PROXY01
**Source:** DC01-CYBERAUDIT
**Destination:** PROXY01
**Service:** Outbound proxy path
**Protocol:** HTTP proxy
**Port:** 3128
**Direction:** Outbound from DC01
**Purpose:** Controlled Internet egress
**Status:** Confirmed for current observed environment

---

## Flow: DB01 -> PROXY01
**Source:** DB01
**Destination:** PROXY01
**Service:** Outbound proxy path
**Protocol:** HTTP proxy
**Port:** 3128
**Direction:** Outbound from DB01
**Purpose:** Controlled Internet egress
**Status:** Confirmed for current observed environment

---

## Flow: APP01 -> PROXY01
**Source:** APP01
**Destination:** PROXY01
**Service:** Outbound proxy path
**Protocol:** HTTP proxy
**Port:** 3128
**Direction:** Outbound from APP01
**Purpose:** Controlled Internet egress
**Status:** Confirmed for current observed environment

---

## Flow: APP02 -> PROXY01
**Source:** APP02
**Destination:** PROXY01
**Service:** Outbound proxy path
**Protocol:** HTTP proxy
**Port:** 3128
**Direction:** Outbound from APP02
**Purpose:** Controlled Internet egress
**Status:** Confirmed for current observed environment

---

## Flow: IAM01 -> PROXY01
**Source:** IAM01
**Destination:** PROXY01
**Service:** Outbound proxy path
**Protocol:** HTTP proxy
**Port:** 3128
**Direction:** Outbound from IAM01
**Purpose:** Controlled Internet egress
**Status:** Confirmed for current observed environment

---

## Flow: Admin laptop -> target systems
**Source:** Admin laptop
**Destination:** Any destination
**Service:** Administrative access
**Protocol:** Broad open access
**Port:** Any
**Direction:** Outbound from Admin laptop
**Purpose:** Current privileged administration model
**Status:** Confirmed current firewall state

---

## Notes
- This file focuses on service-specific communication details rather than broad zone-level permissions.
- A "Standard default declared by owner" status means the value was intentionally accepted for the model, even if it was not directly observed in packet capture or configuration screenshots.
- The current firewall is broader than this matrix and should not be treated as proof that every currently allowed path is actually required.
- This file should later become one of the most important inputs for firewall refinement and AI-assisted least-privilege reasoning.
- Keycloak is currently observed running in development mode on HTTP/8080, which should not be treated as the final hardened exposure model.