# Network – Dependencies

<!--
  CATEGORY: Scope (descriptive) — REQUIRED
  Use "Service on Host" for compound references: "Vault on DB01"
-->

## Purpose
Define logical dependencies between entities in the network domain.

---

## Notes
- Inter-scope-unit communication in this network design is routed through Firewall01, which acts as the gateway and routing boundary for the segmented environment.

---

## Entity: DC01-CYBERAUDIT

**Depends on:**
- PROXY01

**Reasoning:** DC01-CYBERAUDIT is the internal directory, DNS, and time-service foundation of the environment. For outbound Internet access, it depends on PROXY01.

**Confidence:** confirmed  
**Cross-domain:** None currently documented

---

## Entity: DB01

**Depends on:**
- DC01-CYBERAUDIT
- PROXY01

**Reasoning:** DB01 is joined to the domain and relies on DC01-CYBERAUDIT for DNS and time-related services. It also depends on PROXY01 for outbound Internet access.

**Confidence:** confirmed  
**Cross-domain:** None currently documented

---

## Entity: APP01

**Depends on:**
- DC01-CYBERAUDIT
- IAM01
- DB01
- Vault on DB01
- Internal API on IAM01
- PROXY01

**Reasoning:** APP01 is joined to the domain and relies on DC01-CYBERAUDIT for DNS and time-related services. It depends on IAM01 for customer authentication through Keycloak, on DB01 for portal-side database access, on Vault on DB01 for database credentials and certificates, on the Internal API on IAM01 for internal workflow integration, and on PROXY01 for outbound Internet access.

**Confidence:** confirmed  
**Cross-domain:** None currently documented

---

## Entity: APP02

**Depends on:**
- DC01-CYBERAUDIT
- IAM01
- DB01
- Vault on DB01
- PROXY01

**Reasoning:** APP02 is joined to the domain and relies on DC01-CYBERAUDIT for DNS and time-related services. It depends on IAM01 for employee authentication through Keycloak Device Flow with MFA, on DB01 for direct access to audit_system_db, on Vault on DB01 for database credentials, certificates, and Keycloak-related configuration, and on PROXY01 for outbound Internet access.

**Confidence:** confirmed  
**Cross-domain:** None currently documented

---

## Entity: IAM01

**Depends on:**
- DC01-CYBERAUDIT
- DB01
- Vault on DB01
- PROXY01

**Reasoning:** IAM01 depends on DC01-CYBERAUDIT for LDAP federation, DNS, and time-related services. It also depends on DB01 and Vault on DB01 for Internal API database access and secret retrieval, and on PROXY01 for outbound Internet access.

**Confidence:** confirmed  
**Cross-domain:** None currently documented

---

## Entity: PROXY01

**Depends on:**
- Firewall01

**Reasoning:** PROXY01 is the designated egress-related system in the design and depends on Firewall01 as the surrounding network and routing boundary.

**Confidence:** confirmed  
**Cross-domain:** None currently documented

---

## Entity: ESXi

**Depends on:**
- Firewall01
- Switch Management

**Reasoning:** ESXi is part of the infrastructure management layer and depends on the surrounding network and management design.

**Confidence:** needs_confirmation  
**Cross-domain:** None currently documented

---

## Entity: Switch Management

**Depends on:**
- Firewall01

**Reasoning:** The switch management plane exists within the segmented infrastructure and depends on the overall network design.

**Confidence:** needs_confirmation  
**Cross-domain:** None currently documented

---

## Entity: Admin laptop

**Depends on:**
- Firewall01
- Managed access to target systems

**Reasoning:** The Admin laptop is used for privileged administrative access into the environment and depends on managed connectivity to target systems.

**Confidence:** needs_confirmation  
**Cross-domain:** None currently documented