# V3 记录审计

```json
{
  "forecast_order_errors": [],
  "forecast_hash_errors": [],
  "evaluation_order_errors": [],
  "source_counts": {
    "structured": {
      "counts": {
        "memory_multiscale": 5,
        "memory_slow": 5,
        "external_clock": 1,
        "memory_clock": 1,
        "saturation": 3,
        "none": 1
      },
      "total": 16,
      "valid_non_none": 4,
      "invalid": 11
    },
    "no_active": {
      "counts": {
        "none": 7,
        "external_clock": 1,
        "memory_slow": 3,
        "clock": 1,
        "storage": 3,
        "saturation": 1
      },
      "total": 16,
      "valid_non_none": 5,
      "invalid": 4
    },
    "shuffled": {
      "counts": {
        "memory_multiscale": 3,
        "clock": 3,
        "none": 3,
        "saturation": 3,
        "storage": 4
      },
      "total": 16,
      "valid_non_none": 7,
      "invalid": 6
    }
  },
  "representation_changes": {
    "shuffled": {
      "tasks": 4,
      "tasks_with_revision": 3,
      "transitions": 12,
      "revisions": 5
    },
    "plain": {
      "tasks": 4,
      "tasks_with_revision": 2,
      "transitions": 12,
      "revisions": 2
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
      "tasks_with_revision": 4,
      "transitions": 12,
      "revisions": 4
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
