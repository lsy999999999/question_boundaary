# V3 记录审计

```json
{
  "forecast_order_errors": [],
  "forecast_hash_errors": [],
  "evaluation_order_errors": [],
  "source_counts": {
    "structured": {
      "counts": {
        "none": 8,
        "storage": 4,
        "external_clock": 4
      },
      "total": 16,
      "valid_non_none": 8,
      "invalid": 0
    },
    "no_active": {
      "counts": {
        "none": 10,
        "storage": 4,
        "external_clock": 2
      },
      "total": 16,
      "valid_non_none": 6,
      "invalid": 0
    },
    "shuffled": {
      "counts": {
        "none": 10,
        "storage": 1,
        "saturation": 3,
        "external_clock": 2
      },
      "total": 16,
      "valid_non_none": 6,
      "invalid": 0
    }
  },
  "representation_changes": {
    "no_active": {
      "tasks": 4,
      "tasks_with_revision": 0,
      "transitions": 12,
      "revisions": 0
    },
    "retrieval": {
      "tasks": 4,
      "tasks_with_revision": 1,
      "transitions": 12,
      "revisions": 1
    },
    "state_fixed": {
      "tasks": 4,
      "tasks_with_revision": 0,
      "transitions": 12,
      "revisions": 0
    },
    "history_cv": {
      "tasks": 4,
      "tasks_with_revision": 0,
      "transitions": 12,
      "revisions": 0
    },
    "plain": {
      "tasks": 4,
      "tasks_with_revision": 1,
      "transitions": 12,
      "revisions": 1
    },
    "structured": {
      "tasks": 4,
      "tasks_with_revision": 1,
      "transitions": 12,
      "revisions": 1
    },
    "shuffled": {
      "tasks": 4,
      "tasks_with_revision": 0,
      "transitions": 12,
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
