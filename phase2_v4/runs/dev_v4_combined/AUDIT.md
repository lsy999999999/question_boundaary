# V3 记录审计

```json
{
  "forecast_order_errors": [],
  "forecast_hash_errors": [],
  "evaluation_order_errors": [],
  "source_counts": {
    "structured": {
      "counts": {
        "storage": 8,
        "none": 1,
        "memory_multiscale": 3,
        "external_clock": 1,
        "saturation": 3
      },
      "total": 16,
      "valid_non_none": 12,
      "invalid": 3
    },
    "no_active": {
      "counts": {
        "none": 3,
        "storage": 7,
        "external_clock": 4,
        "saturation": 2
      },
      "total": 16,
      "valid_non_none": 13,
      "invalid": 0
    },
    "shuffled": {
      "counts": {
        "storage": 8,
        "external_clock": 4,
        "saturation": 3,
        "none": 1
      },
      "total": 16,
      "valid_non_none": 15,
      "invalid": 0
    }
  },
  "representation_changes": {
    "shuffled": {
      "tasks": 4,
      "tasks_with_revision": 2,
      "transitions": 12,
      "revisions": 3
    },
    "plain": {
      "tasks": 4,
      "tasks_with_revision": 2,
      "transitions": 12,
      "revisions": 3
    },
    "history_cv": {
      "tasks": 4,
      "tasks_with_revision": 0,
      "transitions": 12,
      "revisions": 0
    },
    "retrieval": {
      "tasks": 4,
      "tasks_with_revision": 2,
      "transitions": 12,
      "revisions": 3
    },
    "no_active": {
      "tasks": 4,
      "tasks_with_revision": 2,
      "transitions": 12,
      "revisions": 2
    },
    "structured": {
      "tasks": 4,
      "tasks_with_revision": 3,
      "transitions": 12,
      "revisions": 4
    },
    "state_fixed": {
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
