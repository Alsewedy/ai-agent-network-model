# Network Model v1 – Open Questions and Assumptions

## Purpose
This document records:
- confirmed facts used in the current network model,
- assumptions that should not be treated as final facts,
- and open questions that require later confirmation.

The goal is to avoid silent assumptions and keep the model grounded in confirmed information.

---

## Confirmed Facts

### 1. Network Segmentation
The homelab is segmented into the following main zones:
- WAN
- LAN / DATA
- APP_ZONE
- DMZ_ZONE
- SERVICE_ZONE
- MGMT
- ADMIN
- EMPLOYEE
- GUEST

### 2. Main Assets by Zone
- LAN / DATA:
  - DC01-CYBERAUDIT
  - DB01
- APP_ZONE:
  - APP01
  - APP02
- DMZ_ZONE:
  - PROXY01
- SERVICE_ZONE:
  - IAM01
- MGMT:
  - ESXi
  - Switch Management
- ADMIN:
  - Admin laptop
- EMPLOYEE:
  - Employee devices
- GUEST:
  - Guest devices

### 3. Main Service Placement
- APP01 hosts the customer-facing portal
- APP02 hosts the internal C# employee audit application
- IAM01 hosts Keycloak and the Internal API
- DB01 hosts MariaDB and Vault
- PROXY01 is the designated outbound proxy-related system
- DC01 provides Active Directory, DNS, and time-related services

### 4. Database Architecture
DB01 hosts two logically separated databases:
- saams_portal_db
- audit_system_db

### 5. Vault Usage
The following components are confirmed to retrieve secrets and/or certificates from Vault on DB01:
- APP01
- APP02
- Internal API on IAM01

### 6. Keycloak Usage
- APP01 depends on Keycloak for customer authentication
- APP02 depends on Keycloak for employee authentication through Device Flow with MFA
- IAM01 depends on DC01 for LDAP federation

### 7. Proxy Usage
The following systems currently rely on PROXY01 for outbound Internet access:
- APP01
- APP02
- IAM01
- DB01
- DC01

### 8. Firewall State
The current firewall state includes broad inter-zone allow rules in several internal zones.
This reflects a build-phase configuration rather than a final least-privilege policy baseline.

### 9. WAN Inbound
No inbound pass rules are currently defined on WAN.

### 10. Zone Policy Coverage
No active interface rules are currently defined for:
- MGMT_SEGMENT
- EMPLOYEE_SEGMENT
- GUEST_SEGMENT

---

## Current Assumptions Used in the Model

### Assumption 1
Broad inter-zone access currently exists for build-phase functionality and troubleshooting.

**Status:** Reasonable and supported by current firewall screenshots, but should not be treated as the final intended design.

---

### Assumption 2
MGMT, EMPLOYEE, and GUEST are present in the architecture but are not yet active parts of the current production communication model.

**Status:** Reasonable based on current firewall state, but may evolve later.

---

### Assumption 3
The current network model focuses on the main operational systems rather than every possible infrastructure dependency.

**Status:** Intentional scope choice for v1.

---

## Open Questions

### Open Question 1
What are the exact ports and protocols required for each confirmed dependency?

**Reasoning:**
The current model documents high-level required flows, but not yet exact port-level communication.

---

### Open Question 2
Which of the currently broad inter-zone rules are still genuinely needed for the build phase, and which are already unnecessary?

**Reasoning:**
Some current firewall permissions may no longer be required even for temporary operation.

---

### Open Question 3
What should the final least-privilege communication model look like for:
- LAN / DATA
- APP_ZONE
- SERVICE_ZONE
- DMZ_ZONE
- ADMIN_SEGMENT

**Reasoning:**
The current model documents broad build-phase access, not the final hardened target state.

---

### Open Question 4
What exact management policy should apply to MGMT_SEGMENT in the final design?

**Reasoning:**
MGMT exists architecturally, but does not yet have an active communication policy defined.

---

### Open Question 5
What exact access policy should apply to EMPLOYEE_SEGMENT in the final design?

**Reasoning:**
EMPLOYEE exists architecturally, but does not yet have an active communication policy defined.

---

### Open Question 6
What exact access policy should apply to GUEST_SEGMENT in the final design?

**Reasoning:**
GUEST exists architecturally, but does not yet have an active communication policy defined.

---

### Open Question 7
Should any WAN-facing exposure be introduced later, or should the environment remain without inbound WAN pass rules?

**Reasoning:**
The current posture is safer by default, but future design decisions may change this if external access is needed.

---

### Open Question 8
What is the final desired restriction model for the Admin laptop?

**Reasoning:**
The admin laptop currently has very broad access, but the final intended management model is not yet fully defined.

---

## Modeling Rule for This Project
If a dependency, flow, service, or trust relationship is not clearly confirmed by documentation, code, or direct owner confirmation, it must not be treated as a fact.

Instead, it should be recorded here as:
- an open question,
- a possible future clarification,
- or a scoped assumption that is explicitly marked as non-final.

---

## Notes
- This document exists to reduce hidden assumptions in the AI-ready model.
- It should be updated whenever new evidence confirms or rejects an open question.
- This file is especially important because the future AI agent must be grounded in confirmed knowledge rather than inferred but unverified claims.