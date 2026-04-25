# Network – Technical Matrix

<!--
  CATEGORY: Communication (normative) — OPTIONAL
  ALL fields REQUIRED for every entry. Confidence tag MANDATORY.

  Map the fields to your domain:
    Network → port, protocol      |   AD → protocol, encryption
    IAM → endpoint, method        |   Cloud → API, region, IAM role
-->

## Purpose
Record exact technical details for each communication flow.

---

## Flow: Client / browser → APP01 (Nginx)

**Source:** Client / browser  
**Destination:** APP01  
**Service:** Nginx reverse proxy  
**Protocol:** HTTPS  
**Port / Endpoint:** 443  
**Direction:** inbound to APP01  
**Purpose:** Customer-facing secure access to the portal  
**Confidence:** confirmed

---

## Flow: Nginx on APP01 → Local portal process on APP01 (local internal flow)

**Source:** Nginx on APP01  
**Destination:** Local portal process on APP01  
**Service:** Reverse proxy forwarding  
**Protocol:** HTTPS  
**Port / Endpoint:** 3000  
**Direction:** outbound from Nginx on APP01  
**Purpose:** Forward portal traffic from Nginx to the local Express application  
**Confidence:** confirmed

---

## Flow: APP01 → IAM01 (Keycloak OIDC)

**Source:** APP01  
**Destination:** IAM01  
**Service:** Keycloak OIDC  
**Protocol:** HTTP  
**Port / Endpoint:** 8080  
**Direction:** outbound from APP01  
**Purpose:** Customer authentication and OIDC interaction  
**Confidence:** confirmed

---

## Flow: APP01 → DB01 (MariaDB)

**Source:** APP01  
**Destination:** DB01  
**Service:** MariaDB (saams_portal_db)  
**Protocol:** MySQL over TLS / mTLS  
**Port / Endpoint:** 3307  
**Direction:** outbound from APP01  
**Purpose:** Portal-side database access  
**Confidence:** confirmed

---

## Flow: APP01 → Vault on DB01

**Source:** APP01  
**Destination:** DB01  
**Service:** Vault  
**Protocol:** HTTP  
**Port / Endpoint:** 8200  
**Direction:** outbound from APP01  
**Purpose:** Retrieve database credentials and client certificates  
**Confidence:** confirmed

---

## Flow: APP01 → Internal API on IAM01

**Source:** APP01  
**Destination:** IAM01  
**Service:** Internal API  
**Protocol:** HTTP  
**Port / Endpoint:** 9090  
**Direction:** outbound from APP01  
**Purpose:** Create internal requests, retrieve status updates, and download reports  
**Confidence:** confirmed

---

## Flow: APP02 → IAM01 (Keycloak Device Flow)

**Source:** APP02  
**Destination:** IAM01  
**Service:** Keycloak Device Flow  
**Protocol:** HTTP  
**Port / Endpoint:** 8080  
**Direction:** outbound from APP02  
**Purpose:** Employee authentication through Device Flow and MFA  
**Confidence:** confirmed

---

## Flow: APP02 → DB01 (MariaDB)

**Source:** APP02  
**Destination:** DB01  
**Service:** MariaDB (audit_system_db)  
**Protocol:** MySQL over TLS / mTLS  
**Port / Endpoint:** 3307  
**Direction:** outbound from APP02  
**Purpose:** Internal audit workflow database access  
**Confidence:** confirmed

---

## Flow: APP02 → Vault on DB01

**Source:** APP02  
**Destination:** DB01  
**Service:** Vault  
**Protocol:** HTTP  
**Port / Endpoint:** 8200  
**Direction:** outbound from APP02  
**Purpose:** Retrieve database credentials, certificates, and Keycloak-related configuration  
**Confidence:** confirmed

---

## Flow: IAM01 → DB01 (Internal API database access)

**Source:** IAM01  
**Destination:** DB01  
**Service:** MariaDB (audit_system_db)  
**Protocol:** MySQL over TLS / mTLS  
**Port / Endpoint:** 3307  
**Direction:** outbound from IAM01  
**Purpose:** Internal API database access  
**Confidence:** confirmed

---

## Flow: IAM01 → Vault on DB01

**Source:** IAM01  
**Destination:** DB01  
**Service:** Vault  
**Protocol:** HTTP  
**Port / Endpoint:** 8200  
**Direction:** outbound from IAM01  
**Purpose:** Retrieve database credentials and certificates for Internal API database access  
**Confidence:** confirmed

---

## Flow: IAM01 → DC01-CYBERAUDIT (DNS)

**Source:** IAM01  
**Destination:** DC01-CYBERAUDIT  
**Service:** DNS  
**Protocol:** UDP  
**Port / Endpoint:** 53  
**Direction:** outbound from IAM01  
**Purpose:** Internal name resolution  
**Confidence:** confirmed

---

## Flow: IAM01 → DC01-CYBERAUDIT (LDAP federation)

**Source:** IAM01  
**Destination:** DC01-CYBERAUDIT  
**Service:** LDAP federation  
**Protocol:** TCP  
**Port / Endpoint:** 389  
**Direction:** outbound from IAM01  
**Purpose:** Active Directory federation for Keycloak  
**Confidence:** standard_default

---

## Flow: IAM01 → DC01-CYBERAUDIT (Time)

**Source:** IAM01  
**Destination:** DC01-CYBERAUDIT  
**Service:** Time / NTP  
**Protocol:** UDP  
**Port / Endpoint:** 123  
**Direction:** outbound from IAM01  
**Purpose:** Time synchronization  
**Confidence:** standard_default

---

## Flow: APP01 → DC01-CYBERAUDIT (DNS)

**Source:** APP01  
**Destination:** DC01-CYBERAUDIT  
**Service:** DNS  
**Protocol:** UDP  
**Port / Endpoint:** 53  
**Direction:** outbound from APP01  
**Purpose:** Internal name resolution  
**Confidence:** confirmed

---

## Flow: APP01 → DC01-CYBERAUDIT (Time)

**Source:** APP01  
**Destination:** DC01-CYBERAUDIT  
**Service:** Time / NTP  
**Protocol:** UDP  
**Port / Endpoint:** 123  
**Direction:** outbound from APP01  
**Purpose:** Time synchronization  
**Confidence:** standard_default

---

## Flow: APP02 → DC01-CYBERAUDIT (DNS)

**Source:** APP02  
**Destination:** DC01-CYBERAUDIT  
**Service:** DNS  
**Protocol:** UDP  
**Port / Endpoint:** 53  
**Direction:** outbound from APP02  
**Purpose:** Internal name resolution  
**Confidence:** confirmed

---

## Flow: APP02 → DC01-CYBERAUDIT (Time)

**Source:** APP02  
**Destination:** DC01-CYBERAUDIT  
**Service:** Time / NTP  
**Protocol:** UDP  
**Port / Endpoint:** 123  
**Direction:** outbound from APP02  
**Purpose:** Time synchronization  
**Confidence:** standard_default

---

## Flow: DB01 → DC01-CYBERAUDIT (DNS)

**Source:** DB01  
**Destination:** DC01-CYBERAUDIT  
**Service:** DNS  
**Protocol:** UDP  
**Port / Endpoint:** 53  
**Direction:** outbound from DB01  
**Purpose:** Internal name resolution  
**Confidence:** confirmed

---

## Flow: DB01 → DC01-CYBERAUDIT (Time)

**Source:** DB01  
**Destination:** DC01-CYBERAUDIT  
**Service:** Time / NTP  
**Protocol:** UDP  
**Port / Endpoint:** 123  
**Direction:** outbound from DB01  
**Purpose:** Time synchronization  
**Confidence:** standard_default

---

## Flow: DC01-CYBERAUDIT → PROXY01 (Outbound proxy path)

**Source:** DC01-CYBERAUDIT  
**Destination:** PROXY01  
**Service:** Outbound proxy path  
**Protocol:** HTTP proxy  
**Port / Endpoint:** 3128  
**Direction:** outbound from DC01-CYBERAUDIT  
**Purpose:** Controlled Internet egress  
**Confidence:** confirmed

---

## Flow: DB01 → PROXY01 (Outbound proxy path)

**Source:** DB01  
**Destination:** PROXY01  
**Service:** Outbound proxy path  
**Protocol:** HTTP proxy  
**Port / Endpoint:** 3128  
**Direction:** outbound from DB01  
**Purpose:** Controlled Internet egress  
**Confidence:** confirmed

---

## Flow: APP01 → PROXY01 (Outbound proxy path)

**Source:** APP01  
**Destination:** PROXY01  
**Service:** Outbound proxy path  
**Protocol:** HTTP proxy  
**Port / Endpoint:** 3128  
**Direction:** outbound from APP01  
**Purpose:** Controlled Internet egress  
**Confidence:** confirmed

---

## Flow: APP02 → PROXY01 (Outbound proxy path)

**Source:** APP02  
**Destination:** PROXY01  
**Service:** Outbound proxy path  
**Protocol:** HTTP proxy  
**Port / Endpoint:** 3128  
**Direction:** outbound from APP02  
**Purpose:** Controlled Internet egress  
**Confidence:** confirmed

---

## Flow: IAM01 → PROXY01 (Outbound proxy path)

**Source:** IAM01  
**Destination:** PROXY01  
**Service:** Outbound proxy path  
**Protocol:** HTTP proxy  
**Port / Endpoint:** 3128  
**Direction:** outbound from IAM01  
**Purpose:** Controlled Internet egress  
**Confidence:** confirmed

---

## Flow: Admin laptop → target systems (Administrative access)

**Source:** Admin laptop  
**Destination:** target systems  
**Service:** Administrative access  
**Protocol:** Broad open access  
**Port / Endpoint:** Any  
**Direction:** outbound from Admin laptop  
**Purpose:** Current privileged administration model  
**Confidence:** owner_confirmed