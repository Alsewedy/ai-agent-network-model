# Network – Required Flows

<!--
  CATEGORY: Communication (normative) — OPTIONAL
  Include this folder only if the domain involves entity-to-entity communication.
  If this domain is purely about policies, roles, or configurations with no
  direct communication flows, skip this entire folder.
-->

## Purpose
Define communication flows required for the network domain to function.

---

## Flow: APP01 → IAM01

**Purpose:** Customer authentication through Keycloak OIDC  
**Required for operation:** yes  
**Current state:** Communication currently exists between APP01 and IAM01 for authentication and OIDC interaction.  
**Hardening note:** Restrict this flow to only the specific authentication-related communication required by APP01.  
**Confidence:** confirmed

---

## Flow: APP01 → DB01

**Purpose:** Portal-side database access  
**Required for operation:** yes  
**Current state:** Communication currently exists between APP01 and DB01 for portal-side database access.  
**Hardening note:** Restrict this flow to only the specific database communication required by APP01.  
**Confidence:** confirmed

---

## Flow: APP01 → Vault on DB01

**Purpose:** Retrieve database credentials and client certificates  
**Required for operation:** yes  
**Current state:** Communication currently exists between APP01 and Vault on DB01 for secret and certificate retrieval.  
**Hardening note:** Restrict this flow to only the specific Vault-related access required by APP01.  
**Confidence:** confirmed

---

## Flow: APP01 → Internal API on IAM01

**Purpose:** Create internal requests, retrieve status updates, and download final reports  
**Required for operation:** yes  
**Current state:** Communication currently exists between APP01 and the Internal API on IAM01 for internal workflow integration.  
**Hardening note:** Restrict this flow to only the API communication required by APP01.  
**Confidence:** confirmed

---

## Flow: APP01 → PROXY01

**Purpose:** Controlled outbound Internet access  
**Required for operation:** yes  
**Current state:** Communication currently exists between APP01 and PROXY01 for outbound Internet access.  
**Hardening note:** Restrict this flow to only the required proxy-related communication.  
**Confidence:** confirmed

---

## Flow: Nginx on APP01 → Local portal process on APP01

**Purpose:** Reverse proxy forwarding from HTTPS listener to the local portal application  
**Required for operation:** yes  
**Current state:** This hosted local flow currently exists on APP01.  
**Hardening note:** Keep this flow limited to the local host only.  
**Confidence:** confirmed

---

## Flow: APP02 → IAM01

**Purpose:** Employee authentication through Keycloak Device Flow with MFA  
**Required for operation:** yes  
**Current state:** Communication currently exists between APP02 and IAM01 for employee authentication.  
**Hardening note:** Restrict this flow to only the specific authentication-related communication required by APP02.  
**Confidence:** confirmed

---

## Flow: APP02 → DB01

**Purpose:** Direct access to audit_system_db for internal audit workflow operations  
**Required for operation:** yes  
**Current state:** Communication currently exists between APP02 and DB01 for internal audit workflow database access.  
**Hardening note:** Restrict this flow to only the specific database communication required by APP02.  
**Confidence:** confirmed

---

## Flow: APP02 → Vault on DB01

**Purpose:** Retrieve database credentials, certificates, and Keycloak-related configuration  
**Required for operation:** yes  
**Current state:** Communication currently exists between APP02 and Vault on DB01 for secret and certificate retrieval.  
**Hardening note:** Restrict this flow to only the specific Vault-related access required by APP02.  
**Confidence:** confirmed

---

## Flow: APP02 → PROXY01

**Purpose:** Controlled outbound Internet access  
**Required for operation:** yes  
**Current state:** Communication currently exists between APP02 and PROXY01 for outbound Internet access.  
**Hardening note:** Restrict this flow to only the required proxy-related communication.  
**Confidence:** confirmed

---

## Flow: IAM01 → DC01-CYBERAUDIT

**Purpose:** LDAP federation, DNS, and time-related dependency  
**Required for operation:** yes  
**Current state:** Communication currently exists between IAM01 and DC01-CYBERAUDIT for identity, DNS, and time-related functions.  
**Hardening note:** Restrict this flow to only the exact identity, DNS, and time-related communication required.  
**Confidence:** owner_confirmed

---

## Flow: IAM01 → DB01

**Purpose:** Internal API database access  
**Required for operation:** yes  
**Current state:** Communication currently exists between IAM01 and DB01 for Internal API database access.  
**Hardening note:** Restrict this flow to only the specific database communication required by IAM01.  
**Confidence:** confirmed

---

## Flow: IAM01 → Vault on DB01

**Purpose:** Retrieve database credentials and certificates for Internal API database access  
**Required for operation:** yes  
**Current state:** Communication currently exists between IAM01 and Vault on DB01 for secret and certificate retrieval.  
**Hardening note:** Restrict this flow to only the specific Vault-related access required by IAM01.  
**Confidence:** confirmed

---

## Flow: IAM01 → PROXY01

**Purpose:** Controlled outbound Internet access  
**Required for operation:** yes  
**Current state:** Communication currently exists between IAM01 and PROXY01 for outbound Internet access.  
**Hardening note:** Restrict this flow to only the required proxy-related communication.  
**Confidence:** confirmed

---

## Flow: DB01 → DC01-CYBERAUDIT

**Purpose:** DNS and time-related dependency for the database and Vault host  
**Required for operation:** yes  
**Current state:** Communication currently exists between DB01 and DC01-CYBERAUDIT for domain-related infrastructure functions.  
**Hardening note:** Restrict this flow to only the DNS and time-related communication required by DB01.  
**Confidence:** owner_confirmed

---

## Flow: DB01 → PROXY01

**Purpose:** Controlled outbound Internet access  
**Required for operation:** yes  
**Current state:** Communication currently exists between DB01 and PROXY01 for outbound Internet access.  
**Hardening note:** Restrict this flow to only the required proxy-related communication.  
**Confidence:** confirmed

---

## Flow: DC01-CYBERAUDIT → PROXY01

**Purpose:** Controlled outbound Internet access  
**Required for operation:** yes  
**Current state:** Communication currently exists between DC01-CYBERAUDIT and PROXY01 for outbound Internet access.  
**Hardening note:** Restrict this flow to only the required proxy-related communication.  
**Confidence:** confirmed

---

## Flow: Admin laptop → target systems

**Purpose:** Privileged administration and management access into the environment  
**Required for operation:** yes  
**Current state:** Broad access currently exists from the Admin laptop to target systems.  
**Hardening note:** Narrow this flow to approved targets, approved management protocols, and justified administrative tasks only.  
**Confidence:** owner_confirmed