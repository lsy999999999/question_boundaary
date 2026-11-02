# V3 记录审计

```json
{
  "forecast_order_errors": [],
  "forecast_hash_errors": [],
  "evaluation_order_errors": [],
  "source_counts": {
    "structured": {
      "counts": {
        "storage": 48,
        "none": 32,
        "external_clock": 15,
        "saturation": 1
      },
      "total": 96,
      "valid_non_none": 64,
      "invalid": 0
    },
    "no_active": {
      "counts": {
        "storage": 38,
        "none": 19,
        "external_clock": 10,
        "saturation": 2
      },
      "total": 69,
      "valid_non_none": 50,
      "invalid": 0
    },
    "shuffled": {
      "counts": {
        "none": 37,
        "external_clock": 11,
        "storage": 3,
        "saturation": 4
      },
      "total": 55,
      "valid_non_none": 18,
      "invalid": 0
    }
  },
  "representation_changes": {
    "plain": {
      "tasks": 24,
      "tasks_with_revision": 9,
      "transitions": 72,
      "revisions": 15
    },
    "history_cv": {
      "tasks": 24,
      "tasks_with_revision": 10,
      "transitions": 72,
      "revisions": 16
    },
    "retrieval": {
      "tasks": 24,
      "tasks_with_revision": 8,
      "transitions": 72,
      "revisions": 12
    },
    "structured": {
      "tasks": 24,
      "tasks_with_revision": 9,
      "transitions": 72,
      "revisions": 13
    },
    "state_fixed": {
      "tasks": 24,
      "tasks_with_revision": 0,
      "transitions": 72,
      "revisions": 0
    }
  },
  "semantic_review": "Nonempty valid references establish invocation only, not semantic correctness.",
  "fits_per_task": {
    "state_fixed": 7,
    "history_cv": 51,
    "agents": 52
  }
}
```
