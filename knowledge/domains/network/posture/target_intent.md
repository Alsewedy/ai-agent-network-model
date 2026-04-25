# Network – Target Intent

<!--
  CATEGORY: Posture (differential) — REQUIRED
  
  Defines what this domain is TRYING TO BECOME, not what it is now.
  
  IMPORTANT: This file describes DIRECTION and INTENTION only.
  It must NOT contain:
    - compliant / non-compliant judgments
    - pass / fail statements
    - findings, gaps, or risk levels
    - any verdict about the current environment
  See _meta/RULES.md Rule 9.
-->

## Purpose
Define the intended security direction for the Network domain.

---

### General intent: Least-privilege target direction

The target network design should move from broad build-phase connectivity to a more controlled and auditable least-privilege model.

The current environment is functional and segmented, but many inter-scope-unit permissions are still broader than the final intended posture.
The final design should reduce unnecessary trust between scope units and allow only communication clearly justified by application, identity, management, or operational requirements.

**Alignment direction:** Move toward tighter segmentation, reduced unnecessary trust, auditable communications, and clearly justified least-privilege access paths.

---

### Scope-unit intent: WAN

**Current context:** No inbound pass rules are currently defined on WAN.  
**Target posture:** Inbound exposure from WAN should remain blocked by default unless there is a clearly justified future requirement.  
**Key restrictions:** Avoid broad or unnecessary WAN-facing exposure.  
**Open items:** Whether any future WAN-facing exposure will be introduced later.

**Alignment direction:** Keep the external boundary tightly controlled, default-deny by design, and only open narrowly justified WAN-facing paths if a future requirement is confirmed.

---

### Scope-unit intent: LAN

**Current context:** LAN currently hosts core internal infrastructure including DC01-CYBERAUDIT and DB01. Broad inter-scope-unit communication still exists in the build phase.  
**Target posture:** LAN should remain a highly trusted infrastructure segment and should not be broadly reachable by other scope units.  
**Key restrictions:** Limit access to asset-specific and service-specific communication only.  
**Open items:** What the final least-privilege communication model should be for LAN in the hardened design.

**Alignment direction:** Treat LAN as critical infrastructure, minimize broad reachability into it, and reduce access to tightly scoped infrastructure-only communication paths.

---

### Scope-unit intent: APP_ZONE

**Current context:** APP_ZONE currently hosts APP01 and APP02, and broad build-phase access still exists toward other scope units.  
**Target posture:** APP_ZONE should host business application systems only and should not have broad trust into infrastructure or identity-related scope units.  
**Key restrictions:** Restrict access to only the exact systems and services required by APP01 and APP02.  
**Open items:** What the final least-privilege communication model should be for APP_ZONE in the hardened design.

**Alignment direction:** Reduce application trust boundaries so APP systems only reach the exact identity, database, secret, and egress-related services they operationally require.

---

### Scope-unit intent: DMZ_ZONE

**Current context:** DMZ_ZONE currently hosts PROXY01, but broad internal access toward the DMZ exists in the build phase.  
**Target posture:** DMZ_ZONE should remain narrow and controlled and should not become a broadly trusted transit area.  
**Key restrictions:** Limit communication to explicitly required proxy-related paths only.  
**Open items:** Whether any additional DMZ-facing communication will be needed later beyond the proxy role.

**Alignment direction:** Keep DMZ communication narrow, controlled, and purpose-specific so it remains an explicitly bounded intermediary rather than a generally trusted internal path.

---

### Scope-unit intent: SERVICE_ZONE

**Current context:** SERVICE_ZONE currently hosts IAM01 and broad build-phase access still exists between SERVICE_ZONE and other scope units.  
**Target posture:** SERVICE_ZONE should host identity-related services only and should not be treated as broadly trusted by applications or other internal scope units.  
**Key restrictions:** Restrict communication into and out of SERVICE_ZONE to actual IAM and service-integration needs only.  
**Open items:** What the final least-privilege communication model should be for SERVICE_ZONE in the hardened design.

**Alignment direction:** Protect identity-related services as critical infrastructure and narrow communication to explicit operational IAM and service-integration requirements only.

---

### Scope-unit intent: MGMT_SEGMENT

**Current context:** MGMT_SEGMENT exists in the architecture, but no active communication policy is currently defined for it.  
**Target posture:** MGMT_SEGMENT should become the controlled management plane for infrastructure administration.  
**Key restrictions:** Limit access to explicit management-only communication paths and protocols.  
**Open items:** What exact management policy should apply to MGMT_SEGMENT in the final design.

**Alignment direction:** Establish MGMT_SEGMENT as a dedicated, narrow, auditable management plane with tightly scoped management-only reachability.

---

### Scope-unit intent: ADMIN_SEGMENT

**Current context:** ADMIN_SEGMENT currently includes the Admin laptop, which currently has broad access into the environment.  
**Target posture:** ADMIN_SEGMENT should be used for privileged administration only and should not remain any-to-any in the final design.  
**Key restrictions:** Restrict administrative access to approved targets, approved protocols, and justified administrative tasks only.  
**Open items:** What the final restriction model should be for the Admin laptop and privileged administration paths.

**Alignment direction:** Treat administrative access as highly privileged and reduce it from broad reachability to explicitly approved, auditable, task-bounded administration paths.

---

### Scope-unit intent: EMPLOYEE_SEGMENT

**Current context:** EMPLOYEE_SEGMENT exists in the architecture, but no active communication policy is currently defined for it and no active entities are currently documented in the model.  
**Target posture:** EMPLOYEE_SEGMENT should represent normal internal user systems with only the minimum required access to internal services.  
**Key restrictions:** Block unnecessary direct reachability to trusted infrastructure and sensitive systems.  
**Open items:** What exact access policy should apply to EMPLOYEE_SEGMENT in the final design.

**Alignment direction:** Limit standard user-system reachability to business-justified internal services only and prevent broad access into sensitive infrastructure.

---

### Scope-unit intent: GUEST_SEGMENT

**Current context:** GUEST_SEGMENT exists in the architecture, but no active communication policy is currently defined for it and no active entities are currently documented in the model.  
**Target posture:** GUEST_SEGMENT should remain highly restricted and isolated from trusted internal services.  
**Key restrictions:** Avoid direct communication between GUEST_SEGMENT and sensitive internal zones.  
**Open items:** What exact access policy should apply to GUEST_SEGMENT in the final design.

**Alignment direction:** Keep guest access strongly isolated, minimally trusted, and separated from sensitive internal services and infrastructure zones.

---

### Cross-cutting intent: Identity and trust handling

Identity-related communication should be treated as critical infrastructure traffic, not generic internal communication.

**Alignment direction:** Treat identity paths as explicit trust boundaries and tightly scope identity-related communication and dependencies.

---

### Cross-cutting intent: Database and secret access restriction

Database access should be tightly restricted to the systems that truly require it, and Vault access should be limited to systems and functions that actually require secret retrieval.

**Alignment direction:** Minimize sensitive-service access to exact operational need and avoid broad or convenience-based access to databases and secret systems.

---

### Cross-cutting intent: Proxy and outbound access control

Outbound Internet access should remain controlled through PROXY01 rather than through direct unrestricted egress from internal systems.

**Alignment direction:** Keep outbound access mediated, bounded, and routed through controlled egress paths rather than through direct unrestricted Internet access.

---

### Cross-cutting intent: Administrative access control

Administrative access should be privileged, controlled, and auditable.

**Alignment direction:** Keep administrative reachability explicit, reviewed, auditable, and limited to approved systems, protocols, and tasks.

---

### Cross-cutting intent: Build-phase versus final-state distinction

Temporary broad permissions used for integration, troubleshooting, and staged implementation should not be interpreted as permanent design decisions.

**Alignment direction:** Preserve a clear separation between temporary build-phase convenience and the final hardened least-privilege baseline.

---

### Cross-cutting intent: Auditable baseline direction

The long-term target is not only a working environment, but an auditable environment in which flows, permissions, and trust paths can be clearly justified.

**Alignment direction:** Move toward an environment where communication paths, trust boundaries, and permissions are explainable, reviewable, and defensible.

---

## Modeling Rule

The AI agent should distinguish three layers:
1. Current observed state
2. Confirmed required state
3. Target intended state

This file expresses intended direction only.
It does NOT prove that the direction has been implemented.

If structured control comparison is needed, use:
`control_references.yaml`