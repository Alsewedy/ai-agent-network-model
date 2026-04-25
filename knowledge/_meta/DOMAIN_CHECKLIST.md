# Domain Expansion Checklist

Follow these steps when adding any new domain.

## Step 1: Create the Domain
```
cp -r domains/_template domains/[domain_name]
```

## Step 2: Fill In Domain Metadata
- [ ] Edit `domain.yaml`: set name, owner, categories_used
- [ ] Mark standards_mapped as false (update later if applicable)

## Step 3: Decide Which Categories Apply
- [ ] `scope/` — Required
- [ ] `communication/` — Does this domain have entity-to-entity flows? If no, delete the folder.
- [ ] `posture/` — Required
- [ ] `evidence/` — Are facts from multiple evidence sources? If no, delete the folder.
- [ ] `uncertainty/` — Required

## Step 4: Fill In Scope
- [ ] Define scope units and list entities in each
- [ ] Document services per entity
- [ ] Document dependencies with confidence tags

## Step 5: Fill In Communication (if applicable)
- [ ] Document required flows
- [ ] Document technical details with confidence tags

## Step 6: Fill In Posture
- [ ] Document unnecessary or overly broad access
- [ ] Define target intent per scope unit
- [ ] Add intended_alignment references to relevant external controls (if known)
- [ ] Verify: no verdict language in any posture file (Rule 9)

## Step 7: Fill In Uncertainty
- [ ] List confirmed facts as baseline
- [ ] List assumptions with status
- [ ] List open questions with reasoning

## Step 8: Build the YAML Model
- [ ] Consolidate structured facts into model.yaml
- [ ] Add confidence tags to all technical entries
- [ ] Add intended_alignment references to target_intent section
- [ ] Include metadata.confidence_model
- [ ] Verify: no verdict language anywhere in the YAML

## Step 9: Update Shared Knowledge
- [ ] Cross-domain entities → `shared/relationships/shared_entities.md`
- [ ] Cross-domain flows → `shared/relationships/cross_domain_flows.md`
- [ ] Cross-domain questions → `shared/relationships/global_open_questions.md`
- [ ] New terminology → `shared/conventions/glossary.md`
- [ ] Environment-wide decisions → `shared/conventions/architecture_decisions.md`

## Step 10: Update Standards (if applicable)
- [ ] Add relevant controls to `standards/mappings/control_references.yaml`
- [ ] Set `standards_mapped: true` in domain.yaml

## Step 11: Update KB Index
- [ ] Add domain to `index.yaml` domains list
- [ ] Update total_domains count
- [ ] Update last_full_review date

## Step 12: Rebuild and Test
- [ ] Run chunker to include new domain files
- [ ] Run eval suite for retrieval quality
- [ ] Test 5+ domain-specific questions manually
- [ ] Verify existing domain questions still work
