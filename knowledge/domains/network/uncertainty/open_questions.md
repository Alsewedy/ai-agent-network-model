# Network – Open Questions and Assumptions

<!--
  CATEGORY: Uncertainty — REQUIRED
  Every domain has unknowns. Documenting them prevents silent assumptions.
-->

## Purpose
Record what is confirmed, what is assumed, and what is unresolved.

---

### Confirmed fact: Network segmentation
The network domain currently includes the following scope units:
- WAN
- LAN
- APP_ZONE
- DMZ_ZONE
- SERVICE_ZONE
- MGMT_SEGMENT
- ADMIN_SEGMENT
- EMPLOYEE_SEGMENT
- GUEST_SEGMENT

---

### Confirmed fact: Main entity placement
The currently documented entities are placed as follows:
- LAN:
  - DC01-CYBERAUDIT
  - DB01
- APP_ZONE:
  - APP01
  - APP02
- DMZ_ZONE:
  - PROXY01
- SERVICE_ZONE:
  - IAM01
- MGMT_SEGMENT:
  - ESXi
  - Switch Management
- ADMIN_SEGMENT:
  - Admin laptop

---

### Confirmed fact: Main service placement
The currently documented service placement includes:
- APP01 hosts the customer-facing portal
- APP02 hosts the internal C# employee audit application
- IAM01 hosts Keycloak and the Internal API
- DB01 hosts MariaDB and Vault
- PROXY01 is the designated outbound proxy-related system
- DC01-CYBERAUDIT provides Active Directory, DNS, and time-related services

---

### Confirmed fact: Database architecture
DB01 hosts two logically separated databases:
- saams_portal_db
- audit_system_db

---

### Confirmed fact: Vault usage
The following components are currently documented as retrieving secrets and/or certificates from Vault on DB01:
- APP01
- APP02
- Internal API on IAM01

---

### Confirmed fact: Keycloak usage
The currently documented authentication relationships include:
- APP01 depends on Keycloak for customer authentication
- APP02 depends on Keycloak for employee authentication through Device Flow with MFA
- IAM01 depends on DC01-CYBERAUDIT for LDAP federation

---

### Confirmed fact: Proxy usage
The following systems currently rely on PROXY01 for outbound Internet access:
- APP01
- APP02
- IAM01
- DB01
- DC01-CYBERAUDIT

---

### Confirmed fact: Current firewall posture
The current firewall state includes broad inter-zone allow rules in several internal zones.
This reflects a build-phase configuration rather than a final least-privilege policy baseline.

---

### Confirmed fact: WAN inbound posture
No inbound pass rules are currently defined on WAN.

---

### Confirmed fact: Policy coverage gaps
No active interface rules are currently defined for:
- MGMT_SEGMENT
- EMPLOYEE_SEGMENT
- GUEST_SEGMENT

---

### Assumption: Broad build-phase access
Broad inter-zone access currently exists for build-phase functionality and troubleshooting.

**Status:** reasonable  
**Impact if wrong:** The current model of temporary broad access would need to be revised, and some current required-flow reasoning may need to be narrowed or reclassified.

---

### Assumption: Future-use segments
MGMT_SEGMENT, EMPLOYEE_SEGMENT, and GUEST_SEGMENT are present in the architecture but are not yet active parts of the current production communication model.

**Status:** reasonable  
**Impact if wrong:** The communication model would need to include currently undocumented active flows and enforcement logic for these segments.

---

### Assumption: Scoped v1 model
The current network model focuses on the main operational systems rather than every possible infrastructure dependency.

**Status:** reasonable  
**Impact if wrong:** Additional entities, dependencies, and technical flows may need to be added to make the network model complete enough for future reasoning.

---

### Open question: Exact technical details per dependency

**Question:** What are the exact ports and protocols required for each confirmed dependency?
**Reasoning:** The current model documents high-level required flows, but exact technical details are still important for least-privilege hardening.
**Affected entities:** APP01, APP02, IAM01, DB01, DC01-CYBERAUDIT
**Cross-domain:** no

---

### Open question: Broad build-phase rules still needed

**Question:** Which of the currently broad inter-zone rules are still genuinely needed for the build phase, and which are already unnecessary?
**Reasoning:** Some current firewall permissions may no longer be required even for temporary operation.
**Affected entities:** LAN, APP_ZONE, SERVICE_ZONE, DMZ_ZONE
**Cross-domain:** no

---

### Open question: Final least-privilege model for core zones

**Question:** What should the final least-privilege communication model look like for LAN, APP_ZONE, SERVICE_ZONE, DMZ_ZONE, and ADMIN_SEGMENT?
**Reasoning:** The current model documents broad build-phase access, not the final hardened target state.
**Affected entities:** LAN, APP_ZONE, SERVICE_ZONE, DMZ_ZONE, ADMIN_SEGMENT
**Cross-domain:** no

---

### Open question: Management policy for MGMT_SEGMENT

**Question:** What exact management policy should apply to MGMT_SEGMENT in the final design?
**Reasoning:** MGMT_SEGMENT exists architecturally, but does not yet have an active communication policy defined.
**Affected entities:** MGMT_SEGMENT, ESXi, Switch Management
**Cross-domain:** no

---

### Open question: Access policy for EMPLOYEE_SEGMENT

**Question:** What exact access policy should apply to EMPLOYEE_SEGMENT in the final design?
**Reasoning:** EMPLOYEE_SEGMENT exists architecturally, but does not yet have an active communication policy defined.
**Affected entities:** EMPLOYEE_SEGMENT
**Cross-domain:** no

---

### Open question: Access policy for GUEST_SEGMENT

**Question:** What exact access policy should apply to GUEST_SEGMENT in the final design?
**Reasoning:** GUEST_SEGMENT exists architecturally, but does not yet have an active communication policy defined.
**Affected entities:** GUEST_SEGMENT
**Cross-domain:** no

---

### Open question: Future WAN-facing exposure

**Question:** Should any WAN-facing exposure be introduced later, or should the environment remain without inbound WAN pass rules?
**Reasoning:** The current posture is safer by default, but future design decisions may change this if external access is needed.
**Affected entities:** WAN, Firewall01
**Cross-domain:** no

---

### Open question: Final restriction model for Admin laptop

**Question:** What is the final desired restriction model for the Admin laptop?
**Reasoning:** The Admin laptop currently has very broad access, but the final intended management model is not yet fully defined.
**Affected entities:** Admin laptop, ADMIN_SEGMENT
**Cross-domain:** no

---

## Modeling Rule

If a fact is not confirmed through documentation, code, configuration,
or owner declaration, it must NOT be treated as fact. It belongs here.