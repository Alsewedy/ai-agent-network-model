# Phase 2 – Agent Test Questions v1

## Purpose
This document defines the first official test questions for the network AI agent.

These questions are intended to verify whether the first version of the agent can:
- retrieve structured facts,
- reason over dependencies,
- identify required communication,
- compare current and target states,
- and handle uncertainty honestly.

The scope of these test questions is the network domain only.

---

## Test Question 1 – Dependency Lookup
**Question:**  
What does APP01 depend on?

**What this tests:**  
- whether the agent can retrieve direct dependencies correctly
- whether it understands APP01’s relationship with IAM01, DB01, Vault, Internal API, and PROXY01

**Expected answer characteristics:**  
- clear dependency list
- no invented systems
- grounded in the documented model

---

## Test Question 2 – Required Flow Lookup
**Question:**  
What communication must remain open for APP02?

**What this tests:**  
- whether the agent can identify APP02’s required communication paths
- whether it can distinguish required flows from broad current firewall permissions

**Expected answer characteristics:**  
- mentions IAM01, DB01, Vault on DB01, and PROXY01
- avoids treating broad APP_ZONE access as automatically required
- explains purpose of each communication path

---

## Test Question 3 – Port and Protocol Lookup
**Question:**  
What exact port and protocol does APP01 use to reach the Internal API?

**What this tests:**  
- whether the agent can retrieve exact technical details from the structured model
- whether it prefers confirmed values over assumptions

**Expected answer characteristics:**  
- HTTP
- port 9090
- destination on IAM01
- clear statement of certainty level

---

## Test Question 4 – Current vs Target Comparison
**Question:**  
Is broad APP_ZONE access aligned with the target security intent?

**What this tests:**  
- whether the agent can compare current state with target intent
- whether it understands the difference between build-phase access and final least-privilege design

**Expected answer characteristics:**  
- says broad APP_ZONE access is not aligned with the final intended model
- explains that current broad access is a temporary build-phase condition
- refers to narrowing communication to asset-specific and service-specific access

---

## Test Question 5 – Uncertainty-Aware Answering
**Question:**  
What parts of the network model are still unresolved or not fully confirmed?

**What this tests:**  
- whether the agent can identify open questions and uncertainty honestly
- whether it avoids presenting unresolved items as final facts

**Expected answer characteristics:**  
- mentions open questions such as:
  - final MGMT policy
  - final EMPLOYEE policy
  - final GUEST policy
  - future WAN exposure decisions
  - final admin laptop restriction model
- clearly distinguishes confirmed facts from open questions

---

## Notes
- These are the first core test questions only.
- The goal is not to test everything at once.
- The first version of the agent should succeed on these before expanding to more advanced use cases.