# V3 记录审计

```json
{
  "forecast_order_errors": [],
  "forecast_hash_errors": [],
  "evaluation_order_errors": [],
  "source_counts": {
    "structured": {
      "counts": {
        "none": 30,
        "saturation": 4,
        "storage": 49,
        "external_clock": 13
      },
      "total": 96,
      "valid_non_none": 66,
      "invalid": 0
    },
    "no_active": {
      "counts": {
        "none": 26,
        "saturation": 3,
        "storage": 55,
        "external_clock": 12
      },
      "total": 96,
      "valid_non_none": 70,
      "invalid": 0
    },
    "shuffled": {
      "counts": {
        "none": 57,
        "transport": 5,
        "storage": 10,
        "external_clock": 15,
        "saturation": 9
      },
      "total": 96,
      "valid_non_none": 39,
      "invalid": 0
    }
  },
  "representation_changes": {
    "no_active": {
      "tasks": 24,
      "tasks_with_revision": 10,
      "transitions": 72,
      "revisions": 12
    },
    "retrieval": {
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
    },
    "history_cv": {
      "tasks": 24,
      "tasks_with_revision": 10,
      "transitions": 72,
      "revisions": 16
    },
    "plain": {
      "tasks": 24,
      "tasks_with_revision": 8,
      "transitions": 72,
      "revisions": 14
    },
    "structured": {
      "tasks": 24,
      "tasks_with_revision": 9,
      "transitions": 72,
      "revisions": 14
    },
    "shuffled": {
      "tasks": 24,
      "tasks_with_revision": 8,
      "transitions": 72,
      "revisions": 12
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
