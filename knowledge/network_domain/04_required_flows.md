# Network Model v1 – Required Flows

## Purpose
This document defines the main communication flows required for the homelab environment to function.
It is intended to distinguish between:
- flows that are operationally required,
- flows that are currently allowed in the firewall during the build phase,
- and flows that should later be tightened into a more restrictive security baseline.

This document does not yet attempt to define final firewall rule syntax.
It focuses on architectural communication requirements.

---

## Flow: APP01 -> IAM01
**Purpose:** Customer authentication through Keycloak OIDC  
**Required for Operation:** Yes  
**Current State:** Broad inter-zone connectivity currently exists between APP_ZONE and SERVICE_ZONE  
**Hardening Note:** This should later be restricted to only the specific ports and protocols required for Keycloak-based authentication.

---

## Flow: APP01 -> DB01
**Purpose:** Portal-side database access to saams_portal_db  
**Required for Operation:** Yes  
**Current State:** Broad inter-zone connectivity currently exists between APP_ZONE and LAN / DATA  
**Hardening Note:** This should later be restricted to only the database communication required by APP01.

---

## Flow: APP01 -> Vault on DB01
**Purpose:** Retrieve database credentials and client certificates for secure database access  
**Required for Operation:** Yes  
**Current State:** Broad inter-zone connectivity currently exists between APP_ZONE and LAN / DATA  
**Hardening Note:** This should later be restricted to only the specific Vault-related access required by APP01.

---

## Flow: APP01 -> Internal API on IAM01
**Purpose:** Create internal audit requests, retrieve status updates, and download final reports  
**Required for Operation:** Yes  
**Current State:** Broad inter-zone connectivity currently exists between APP_ZONE and SERVICE_ZONE  
**Hardening Note:** This should later be restricted to only the API endpoint access required by the portal.

---

## Flow: APP01 -> PROXY01
**Purpose:** Outbound Internet access through the designated proxy path  
**Required for Operation:** Yes  
**Current State:** APP_ZONE currently has broad access toward DMZ_ZONE  
**Hardening Note:** This should later be restricted so APP01 uses only the required proxy-related outbound path rather than broad access to the DMZ.

---

## Flow: Nginx on APP01 -> local portal process on APP01
**Purpose:** Reverse proxy forwarding from HTTPS listener to the local Node.js portal application  
**Required for Operation:** Yes  
**Current State:** Hosted locally on the same asset  
**Hardening Note:** This co-location is acceptable for the current build phase, but long-term design may review whether reverse proxy and application hosting should remain combined.

---

## Flow: APP02 -> IAM01
**Purpose:** Employee authentication through Keycloak Device Flow with MFA  
**Required for Operation:** Yes  
**Current State:** Broad inter-zone connectivity currently exists between APP_ZONE and SERVICE_ZONE  
**Hardening Note:** This should later be restricted to only the specific authentication-related communication required by the internal employee application.

---

## Flow: APP02 -> DB01
**Purpose:** Direct access to audit_system_db for internal audit workflow operations  
**Required for Operation:** Yes  
**Current State:** Broad inter-zone connectivity currently exists between APP_ZONE and LAN / DATA  
**Hardening Note:** This should later be restricted to only the specific database communication required by APP02.

---

## Flow: APP02 -> Vault on DB01
**Purpose:** Retrieve database credentials, certificates, and Keycloak-related configuration  
**Required for Operation:** Yes  
**Current State:** Broad inter-zone connectivity currently exists between APP_ZONE and LAN / DATA  
**Hardening Note:** This should later be restricted to only the specific Vault-related access required by APP02.

---

## Flow: APP02 -> PROXY01
**Purpose:** Outbound Internet access through the designated proxy path  
**Required for Operation:** Yes  
**Current State:** APP_ZONE currently has broad access toward DMZ_ZONE  
**Hardening Note:** This should later be restricted so APP02 uses only the required proxy-related outbound path rather than broad access to the DMZ.

---

## Flow: IAM01 -> DC01-CYBERAUDIT
**Purpose:** LDAP federation, internal directory dependency, DNS, and time-related dependency  
**Required for Operation:** Yes  
**Current State:** Broad inter-zone connectivity currently exists between SERVICE_ZONE and LAN / DATA  
**Hardening Note:** This should later be restricted to only the exact identity and infrastructure services required by Keycloak and related components.

---

## Flow: IAM01 -> DB01
**Purpose:** Internal API access to audit_system_db  
**Required for Operation:** Yes  
**Current State:** Broad inter-zone connectivity currently exists between SERVICE_ZONE and LAN / DATA  
**Hardening Note:** This should later be restricted to only the specific database communication required by the Internal API.

---

## Flow: IAM01 -> Vault on DB01
**Purpose:** Retrieve database credentials and certificates for Internal API database access  
**Required for Operation:** Yes  
**Current State:** Broad inter-zone connectivity currently exists between SERVICE_ZONE and LAN / DATA  
**Hardening Note:** This should later be restricted to only the specific Vault-related access required by IAM01.

---

## Flow: IAM01 -> PROXY01
**Purpose:** Outbound Internet access through the designated proxy path  
**Required for Operation:** Yes  
**Current State:** SERVICE_ZONE currently has broad access toward DMZ_ZONE  
**Hardening Note:** This should later be restricted so IAM01 uses only the required proxy-related outbound path rather than broad access to the DMZ.

---

## Flow: DB01 -> DC01-CYBERAUDIT
**Purpose:** Domain, DNS, and time-related dependency for the database and Vault host  
**Required for Operation:** Yes  
**Current State:** Broad access currently exists within LAN / DATA  
**Hardening Note:** This should later be limited to only the infrastructure services required by DB01.

---

## Flow: DB01 -> PROXY01
**Purpose:** Outbound Internet access through the designated proxy path  
**Required for Operation:** Yes  
**Current State:** LAN / DATA currently has broad access toward DMZ_ZONE  
**Hardening Note:** This should later be restricted so DB01 uses only the required proxy-related outbound path rather than broad access to the DMZ.

---

## Flow: DC01-CYBERAUDIT -> PROXY01
**Purpose:** Outbound Internet access through the designated proxy path  
**Required for Operation:** Yes  
**Current State:** LAN / DATA currently has broad access toward DMZ_ZONE  
**Hardening Note:** This should later be restricted so DC01 uses only the required proxy-related outbound path rather than broad access to the DMZ.

---

## Flow: ADMIN laptop -> target systems
**Purpose:** Privileged administration and management access into the environment  
**Required for Operation:** Yes  
**Current State:** ADMIN segment currently allows very broad access from the admin laptop to any destination  
**Hardening Note:** This should later be narrowed to management-specific access only, based on actual administrative need and approved target systems.

---

## Flow: LAN / DATA -> APP_ZONE
**Purpose:** Current build-phase inter-zone communication  
**Required for Operation:** Partially confirmed  
**Current State:** Broad access currently exists from LAN / DATA to APP_ZONE  
**Hardening Note:** This broad access should not be treated as final policy. It should be reviewed and reduced to only confirmed required flows.

---

## Flow: LAN / DATA -> SERVICE_ZONE
**Purpose:** Current build-phase inter-zone communication  
**Required for Operation:** Partially confirmed  
**Current State:** Broad access currently exists from LAN / DATA to SERVICE_ZONE  
**Hardening Note:** This broad access should not be treated as final policy. It should be reviewed and reduced to only confirmed required flows.

---

## Flow: LAN / DATA -> DMZ_ZONE
**Purpose:** Current build-phase inter-zone communication  
**Required for Operation:** Partially confirmed  
**Current State:** Broad access currently exists from LAN / DATA to DMZ_ZONE  
**Hardening Note:** This broad access should not be treated as final policy. It should be reviewed and reduced to only confirmed required flows.

---

## Flow: APP_ZONE -> LAN / DATA
**Purpose:** Current build-phase inter-zone communication  
**Required for Operation:** Yes, but only for specific services  
**Current State:** Broad access currently exists from APP_ZONE to LAN / DATA  
**Hardening Note:** This must later be narrowed to only APP01/APP02 access required for DB, Vault, and DC-related dependencies where applicable.

---

## Flow: APP_ZONE -> SERVICE_ZONE
**Purpose:** Current build-phase inter-zone communication  
**Required for Operation:** Yes, but only for specific services  
**Current State:** Broad access currently exists from APP_ZONE to SERVICE_ZONE  
**Hardening Note:** This must later be narrowed to only the identity and API communication required by APP01 and APP02.

---

## Flow: APP_ZONE -> DMZ_ZONE
**Purpose:** Current build-phase inter-zone communication  
**Required for Operation:** Yes, but only for proxy-related outbound paths  
**Current State:** Broad access currently exists from APP_ZONE to DMZ_ZONE  
**Hardening Note:** This must later be narrowed to only proxy-related communication to PROXY01.

---

## Flow: SERVICE_ZONE -> LAN / DATA
**Purpose:** Current build-phase inter-zone communication  
**Required for Operation:** Yes, but only for specific services  
**Current State:** Broad access currently exists from SERVICE_ZONE to LAN / DATA  
**Hardening Note:** This must later be narrowed to only the DC01, DB01, and Vault-related communication required by IAM01 and the Internal API.

---

## Flow: SERVICE_ZONE -> APP_ZONE
**Purpose:** Current build-phase inter-zone communication  
**Required for Operation:** Partially confirmed  
**Current State:** Broad access currently exists from SERVICE_ZONE to APP_ZONE  
**Hardening Note:** This should be reviewed carefully. Only specifically required return-path or application-related communication should remain in the final policy.

---

## Flow: SERVICE_ZONE -> DMZ_ZONE
**Purpose:** Current build-phase inter-zone communication  
**Required for Operation:** Yes, but only for proxy-related outbound paths  
**Current State:** Broad access currently exists from SERVICE_ZONE to DMZ_ZONE  
**Hardening Note:** This must later be narrowed to only proxy-related communication to PROXY01.

---

## Flow: DMZ_ZONE -> any internal destination
**Purpose:** Current build-phase communication model  
**Required for Operation:** Not fully confirmed  
**Current State:** DMZ_ZONE currently appears broadly allowed outbound  
**Hardening Note:** This should be reviewed carefully. The final design should avoid treating the DMZ as a broadly trusted source. Only explicitly required communication from PROXY01 should remain.

---

## Flow: MGMT_SEGMENT
**Purpose:** Reserved management area in the current design  
**Required for Operation:** Not yet modeled in active firewall policy  
**Current State:** No active rules currently defined  
**Hardening Note:** Future policy should define exactly what management systems may reach and which protocols are allowed.

---

## Flow: EMPLOYEE_SEGMENT
**Purpose:** Internal employee workstation zone in the current design  
**Required for Operation:** Not yet modeled in active firewall policy  
**Current State:** No active rules currently defined  
**Hardening Note:** Future policy should define exactly which internal services employee systems may access and block all unnecessary direct access to sensitive zones.

---

## Flow: GUEST_SEGMENT
**Purpose:** Guest or untrusted access zone in the current design  
**Required for Operation:** Not yet modeled in active firewall policy  
**Current State:** No active rules currently defined  
**Hardening Note:** Future policy should remain highly restrictive and avoid direct access to sensitive internal services.

---

## Flow: WAN inbound
**Purpose:** External inbound exposure  
**Required for Operation:** No confirmed inbound pass rules currently required  
**Current State:** No inbound pass rules currently defined on WAN  
**Hardening Note:** This is consistent with a safer default posture. Any future WAN exposure should be explicitly justified and tightly scoped.

---

## Notes
- This document defines the main architectural flows required by the current environment.
- It intentionally distinguishes between operational requirements and the broader build-phase firewall permissions currently present.
- Several currently allowed inter-zone paths are broader than necessary and should not be treated as the final intended security baseline.
- Final firewall hardening should move from broad zone-to-zone access toward asset-specific and service-specific communication only.
- MGMT, EMPLOYEE, and GUEST are present in the network design, but they are not yet active parts of the current firewall communication model.