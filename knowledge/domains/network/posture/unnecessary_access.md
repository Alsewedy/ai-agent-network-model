# Network – Unnecessary or Overly Broad Access

<!--
  CATEGORY: Posture (differential) — REQUIRED

  Map to your domain:
    Network → broad firewall rules    |   AD → excessive group memberships
    IAM → overly broad roles         |   Cloud → public endpoints
-->

## Purpose
Document access or permissions broader than necessary that should be restricted in the final design.

---

## LAN → APP_ZONE (broad access)

**Current state:** Broad access currently exists  
**Should remain broad:** no  
**Reasoning:** Core infrastructure should not maintain unrestricted access to application systems unless specific service dependencies require it.  
**Target state:** Only explicitly required communication should remain.

---

## LAN → SERVICE_ZONE (broad access)

**Current state:** Broad access currently exists  
**Should remain broad:** no  
**Reasoning:** Core infrastructure should not maintain unrestricted access to identity services unless specific operational dependencies require it.  
**Target state:** Restrict to required infrastructure and identity-related communication only.

---

## LAN → DMZ_ZONE (broad access)

**Current state:** Broad access currently exists  
**Should remain broad:** no  
**Reasoning:** Broad access from core infrastructure into the DMZ increases unnecessary trust exposure.  
**Target state:** Limit communication to explicitly required proxy-related paths only.

---

## APP_ZONE → LAN (broad access)

**Current state:** Broad access currently exists  
**Should remain broad:** no  
**Reasoning:** APP01 and APP02 require communication into LAN, but only for specific functions such as database access, Vault access, and selected DC-related services.  
**Target state:** Restrict to asset-specific and service-specific communication only.

---

## APP_ZONE → SERVICE_ZONE (broad access)

**Current state:** Broad access currently exists  
**Should remain broad:** no  
**Reasoning:** APP01 and APP02 require access to IAM-related services, but not unrestricted access to the entire SERVICE_ZONE.  
**Target state:** Restrict to only the identity and internal API communication actually required.

---

## APP_ZONE → DMZ_ZONE (broad access)

**Current state:** Broad access currently exists  
**Should remain broad:** no  
**Reasoning:** APP systems should not have unrestricted access into the DMZ.  
**Target state:** Restrict to proxy-related communication to PROXY01 only.

---

## SERVICE_ZONE → LAN (broad access)

**Current state:** Broad access currently exists  
**Should remain broad:** no  
**Reasoning:** IAM01 requires selected access to DC01-CYBERAUDIT, DB01, and Vault on DB01, but broad access to the whole LAN is not justified.  
**Target state:** Restrict to only required identity, database, Vault, DNS, and time-related communication.

---

## SERVICE_ZONE → APP_ZONE (broad access)

**Current state:** Broad access currently exists  
**Should remain broad:** no  
**Reasoning:** Broad reverse trust from SERVICE_ZONE into application systems is not justified unless specific communication is confirmed.  
**Target state:** Keep only explicitly required return-path or service-specific access.

---

## SERVICE_ZONE → DMZ_ZONE (broad access)

**Current state:** Broad access currently exists  
**Should remain broad:** no  
**Reasoning:** IAM-related systems should not have unrestricted access into the DMZ.  
**Target state:** Restrict to proxy-related outbound communication to PROXY01 only.

---

## DMZ_ZONE → internal destinations (broad access)

**Current state:** Broad access currently appears to exist  
**Should remain broad:** no  
**Reasoning:** The DMZ should not act as a broadly trusted source into internal zones.  
**Target state:** Only explicitly required communication from PROXY01 should remain. Any unnecessary internal reachability from DMZ_ZONE should be blocked.

---

## Admin laptop → any destination

**Current state:** Broad access currently exists from Admin laptop to any destination  
**Should remain broad:** no  
**Reasoning:** Administrative access is operationally important, but unrestricted any-to-any access should not be treated as a permanent baseline.  
**Target state:** Restrict administrative access to approved targets, management protocols, and justified operational needs only.

---

## APP01 → entire SERVICE_ZONE

**Current state:** Broad zone-level access currently exists  
**Should remain broad:** no  
**Reasoning:** APP01 needs Keycloak and the Internal API on IAM01, but it does not need unrestricted access to all services in SERVICE_ZONE.  
**Target state:** Limit access to IAM01 and only the required authentication and API-related services.

---

## APP02 → entire SERVICE_ZONE

**Current state:** Broad zone-level access currently exists  
**Should remain broad:** no  
**Reasoning:** APP02 needs Keycloak on IAM01 for employee authentication, but not broad access across the entire SERVICE_ZONE.  
**Target state:** Limit access to IAM01 and only the required authentication-related services.

---

## APP01 → entire LAN

**Current state:** Broad zone-level access currently exists  
**Should remain broad:** no  
**Reasoning:** APP01 needs access to DB01 and Vault on DB01, but not unrestricted access to all systems in LAN.  
**Target state:** Limit access to DB01 and only the specific database and Vault-related services required.

---

## APP02 → entire LAN

**Current state:** Broad zone-level access currently exists  
**Should remain broad:** no  
**Reasoning:** APP02 needs access to DB01, Vault on DB01, and selected DC-related services, but not unrestricted access to all systems in LAN.  
**Target state:** Limit access to DB01, DC01-CYBERAUDIT, and only the exact required services.

---

## IAM01 → entire LAN

**Current state:** Broad zone-level access currently exists  
**Should remain broad:** no  
**Reasoning:** IAM01 requires communication with DC01-CYBERAUDIT, DB01, and Vault on DB01, but unrestricted access to all systems in LAN is broader than necessary.  
**Target state:** Limit access to the exact required infrastructure services only.

---

## DB01 → broad access to DMZ_ZONE

**Current state:** Broad zone-level access currently exists  
**Should remain broad:** no  
**Reasoning:** DB01 may need outbound proxy-related access, but it does not need unrestricted reachability to the DMZ.  
**Target state:** Restrict to only the required proxy path to PROXY01.

---

## DC01-CYBERAUDIT → broad access to DMZ_ZONE

**Current state:** Broad zone-level access currently exists  
**Should remain broad:** no  
**Reasoning:** DC01-CYBERAUDIT may need outbound proxy-related access, but it does not need unrestricted reachability to the DMZ.  
**Target state:** Restrict to only the required proxy path to PROXY01.

---

## MGMT_SEGMENT undefined access model

**Current state:** No active rules currently defined  
**Should remain broad:** no  
**Reasoning:** A management network should not remain policy-undefined in a mature environment.  
**Target state:** Define explicit management-only communication paths and block unnecessary access.

---

## EMPLOYEE_SEGMENT undefined access model

**Current state:** No active rules currently defined  
**Should remain broad:** no  
**Reasoning:** Employee systems should not be left without a clear communication policy in the final design.  
**Target state:** Define exactly what internal services employee systems may access and block unnecessary direct reachability to sensitive zones.

---

## GUEST_SEGMENT undefined access model

**Current state:** No active rules currently defined  
**Should remain broad:** no  
**Reasoning:** Guest systems should remain highly restricted and isolated from sensitive internal services.  
**Target state:** Explicitly restrict guest access and avoid direct communication with trusted internal zones.

---

## WAN inbound exposure

**Current state:** No inbound pass rules currently defined  
**Should remain broad:** no  
**Reasoning:** The absence of inbound WAN exposure is currently consistent with a safer default posture.  
**Target state:** Only add WAN-facing access if there is a clearly justified requirement and tightly scoped protection around it.