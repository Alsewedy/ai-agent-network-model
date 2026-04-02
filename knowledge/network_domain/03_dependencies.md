# Network Model v1 – Dependencies

## Purpose
This document defines the main logical dependencies between major assets in the homelab environment.
At this stage, it focuses on system-to-system dependency relationships only.
It does not yet define ports, protocols, or firewall rules.

---

## Asset: DC01-CYBERAUDIT
**Depends on:**
- PROXY01

**Reasoning:**
DC01 is currently the internal directory and DNS foundation of the environment.
It also provides time-related services within the internal environment.
For outbound Internet access, it depends on PROXY01.

---

## Asset: DB01
**Depends on:**
- DC01-CYBERAUDIT
- PROXY01

**Reasoning:**
DB01 is joined to the domain and relies on internal directory, DNS, and time-related services provided by DC01.
It hosts the logically separated database layers used by both the portal-side and internal audit-side systems, and also hosts Vault.
For outbound Internet access, it depends on PROXY01.

---

## Asset: APP01
**Depends on:**
- DC01-CYBERAUDIT
- IAM01
- DB01
- Vault on DB01
- Internal API on IAM01

**Reasoning:**
APP01 is joined to the domain and relies on internal directory, DNS, and time-related services provided by DC01.
APP01 hosts the customer-facing portal.
It also hosts the Nginx reverse proxy layer that listens on HTTPS and forwards traffic to the local portal application process on the same server.
Customer authentication depends on Keycloak on IAM01.
The application also depends on the portal-side database on DB01 and retrieves database credentials and certificates from Vault on DB01.
It communicates with the internal API on IAM01 to create internal requests, retrieve status updates, and download final reports.
For outbound Internet access, it depends on PROXY01.

---

## Asset: APP02
**Depends on:**
- IAM01
- DB01
- Vault on DB01
- PROXY01

**Reasoning:**
APP02 hosts the internal C# employee audit application.
Employee authentication depends on Keycloak on IAM01 through Device Flow and MFA.
The application also connects directly to audit_system_db on DB01 and retrieves database credentials, certificates from Vault.
For outbound Internet access, it depends on PROXY01.

---

## Asset: IAM01
**Depends on:**
- DC01-CYBERAUDIT
- DB01
- Vault on DB01
- PROXY01

**Reasoning:**
IAM01 hosts Keycloak and the internal realm is federated with Active Directory through LDAP.
It also hosts the internal API, which depends on the internal audit-side database on DB01 and retrieves credentials and certificates from Vault on DB01.
For outbound Internet access, it depends on PROXY01.

---

## Asset: PROXY01
**Depends on:**
- Firewall01

**Reasoning:**
PROXY01 is the designated egress-related system in the design.
At the current stage, it represents the main outbound path for most systems, although final enforcement still needs refinement through Firewall01.

---

## Asset: ESXi
**Depends on:**
- Firewall01
- Switch Management

**Reasoning:**
ESXi is part of the infrastructure management layer and depends on the surrounding network and management design.

**Status:** Needs owner confirmation

---

## Asset: Switch Management
**Depends on:**
- Firewall01

**Reasoning:**
The switch management plane exists within the segmented infrastructure and depends on the overall network design.

**Status:** Needs owner confirmation

---

## Asset: Admin laptop
**Depends on:**
- Firewall01
- Managed access to target systems

**Reasoning:**
The admin laptop is used for privileged administrative access into the environment.

**Status:** Needs owner confirmation

---

## Notes
- This document captures logical dependencies only.
- Communication paths, ports, and firewall requirements will be documented separately.
- The portal-side and internal-side systems are intentionally separated through different application paths and logically separated databases.
- Vault is hosted on DB01 and Internal API is hosted on IAM01, so they are documented as hosted components rather than separate standalone assets.
- Outbound access is conceptually centralized through PROXY01, but final enforcement still requires firewall refinement.