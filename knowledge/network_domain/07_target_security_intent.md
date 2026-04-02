# Network Model v1 – Target Security Intent

## Purpose
This document defines the intended security direction of the network model.
It does not describe the current firewall state only.
Instead, it explains the target security intent that should guide future hardening, policy refinement, and AI-assisted reasoning.

The purpose of this file is to help the future AI agent understand not only what exists today, but what the environment is trying to become.

---

## 1. General Security Intent

The target network design should move from broad build-phase connectivity to a more controlled and auditable least-privilege model.

The current environment is functional and segmented, but many inter-zone permissions are still broader than the final intended posture.
The final design should reduce unnecessary trust between zones and allow only communication that is clearly justified by application, identity, management, or operational requirements.

---

## 2. Zone Separation Intent

### LAN / DATA
This zone should remain highly trusted and should host core internal infrastructure such as:
- Active Directory
- DNS
- Database services
- Vault

It should not be broadly reachable by other zones.
Only explicitly required communication to specific assets and services should be allowed.

### APP_ZONE
This zone should host business application systems only.
Application systems should not have broad trust into core infrastructure or identity services.
They should be allowed to communicate only with the exact systems and services they need.

### SERVICE_ZONE
This zone should host identity-related services and similar supporting functions.
It should not be treated as broadly trusted by application systems or by other internal zones.
Communication into and out of this zone should be tightly scoped to actual IAM and service integration needs.

### DMZ_ZONE
This zone should not become a broadly trusted transit area.
Its final purpose should remain narrow and controlled.
Only specifically justified communication to or from DMZ services should be allowed.

### ADMIN_SEGMENT
This zone should be used for privileged administration only.
It should not remain any-to-any in the final design.
Administrative access should be narrowed to approved targets, approved protocols, and clear operational justification.

### MGMT_SEGMENT
This zone should become the controlled management plane for infrastructure administration.
Its future policy should be explicit and management-only in nature.

### EMPLOYEE_SEGMENT
This zone should represent normal internal user systems.
Its future policy should allow only the minimum required access to internal services and block unnecessary direct access to trusted infrastructure.

### GUEST_SEGMENT
This zone should remain highly restricted and isolated.
It should not have direct access to trusted internal services.

### WAN
Inbound exposure from WAN should remain blocked by default.
Any future WAN-facing access should require explicit justification and tight security controls.

---

## 3. Identity and Trust Intent

Identity-related communication should be treated as critical infrastructure traffic, not generic internal communication.

The final model should ensure that:
- application systems only reach identity services when necessary,
- identity services only reach core infrastructure when required,
- and trust relationships are minimized rather than implied by broad zone-level allow rules.

Key identity dependencies such as Keycloak, Active Directory, LDAP federation, DNS, and time-related services should remain functional, but should not result in unnecessary reachability beyond their real operational need.

---

## 4. Database and Secret Access Intent

Database access should be tightly restricted to the systems that truly require it.

The final model should ensure that:
- APP01 only reaches the portal-side database functions it needs,
- APP02 only reaches the internal audit-side database functions it needs,
- the Internal API only reaches the internal audit-side database functions it needs,
- and Vault access is limited to the systems and functions that actually require secret retrieval.

Broad access to DB01 as an entire zone destination should not remain in the final design.

---

## 5. Proxy and Outbound Access Intent

Outbound Internet access should remain controlled through PROXY01.

The final model should avoid direct unrestricted Internet egress from internal systems.
Systems that require outbound access should use only the designated proxy path and only where there is an actual operational need.

Broad internal access to the entire DMZ should not remain part of the final baseline.
Communication should be narrowed to the exact proxy-related path required.

---

## 6. Administrative Access Intent

Administrative access should be privileged, controlled, and auditable.

The final model should avoid leaving the admin workstation with unrestricted any-to-any reachability.
Instead, administrative paths should be based on:
- approved targets,
- approved management protocols,
- and clearly justified administrative tasks.

This is especially important because ADMIN currently holds one of the broadest trust positions in the environment.

---

## 7. Build-Phase vs Final-State Intent

The current model includes temporary broad permissions to support integration, troubleshooting, and staged implementation.
These should not be interpreted as permanent design decisions.

The final intended state is:
- fewer broad zone-to-zone permissions,
- more asset-specific communication,
- more service-specific communication,
- and a clearer distinction between operational necessity and convenience.

---

## 8. Auditable Baseline Intent

The long-term target is not only a working environment, but an auditable environment.

That means the final network model should be easier to explain in terms of:
- why a flow exists,
- why a flow is allowed,
- what service depends on it,
- what risk is introduced if it remains too broad,
- and how the design aligns with least privilege and realistic enterprise control expectations.

The future AI agent should eventually be able to reason about this target posture, compare it with the current state, and help identify where the environment still needs tightening.

---

## 9. Modeling Rule for the AI Agent

The AI agent should not assume that currently allowed communication is automatically intended communication.

Instead, the AI agent should interpret the model using three layers:
1. current observed access,
2. confirmed required operational access,
3. target intended least-privilege access.

This distinction is essential for meaningful security reasoning.

---

## Notes
- This document defines the intended security direction of the network model, not only its current implementation state.
- It should be used together with:
  - required flows,
  - blocked or unnecessary flows,
  - and open questions / assumptions.
- The future AI agent should use this file to understand the difference between temporary build-phase allowances and the intended hardened architecture.