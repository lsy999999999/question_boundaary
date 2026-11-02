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
        "external_clock": 1,
        "memory_slow": 5,
        "saturation": 3,
        "none": 1,
        "memory_clock": 1
      },
      "total": 16,
      "valid_non_none": 4,
      "invalid": 11
    },
    "no_active": {
      "counts": {
        "none": 7,
        "external_clock": 1,
        "storage": 3,
        "memory_slow": 3,
        "clock": 1,
        "saturation": 1
      },
      "total": 16,
      "valid_non_none": 5,
      "invalid": 4
    },
    "shuffled": {
      "counts": {
        "memory_multiscale": 3,
        "none": 3,
        "clock": 3,
        "storage": 4,
        "saturation": 3
      },
      "total": 16,
      "valid_non_none": 7,
      "invalid": 6
    }
  },
  "representation_changes": {
    "no_active": {
      "tasks": 4,
      "tasks_with_revision": 4,
      "transitions": 12,
      "revisions": 4
    },
    "retrieval": {
      "tasks": 4,
      "tasks_with_revision": 2,
      "transitions": 12,
      "revisions": 3
    },
    "plain": {
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
    "shuffled": {
      "tasks": 4,
      "tasks_with_revision": 3,
      "transitions": 12,
      "revisions": 5
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
