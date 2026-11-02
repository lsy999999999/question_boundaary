# V3 记录审计

```json
{
  "forecast_order_errors": [],
  "forecast_hash_errors": [],
  "evaluation_order_errors": [],
  "source_counts": {
    "structured": {
      "counts": {
        "none": 4,
        "external_clock": 13,
        "saturation": 12,
        "storage": 54,
        "memory_clock": 10,
        "history_all": 2,
        "memory_slow": 1
      },
      "total": 96,
      "valid_non_none": 79,
      "invalid": 13
    },
    "no_active": {
      "counts": {
        "none": 6,
        "external_clock": 10,
        "storage": 51,
        "memory_clock": 7,
        "history_all": 6,
        "saturation": 11,
        "memory_multiscale": 2,
        "memory_slow": 1,
        "nonlinear_delay": 2
      },
      "total": 96,
      "valid_non_none": 72,
      "invalid": 18
    },
    "shuffled": {
      "counts": {
        "none": 9,
        "external_clock": 14,
        "storage": 49,
        "memory_clock": 10,
        "history_all": 3,
        "saturation": 10,
        "memory_multiscale": 1
      },
      "total": 96,
      "valid_non_none": 73,
      "invalid": 14
    }
  },
  "representation_changes": {
    "no_active": {
      "tasks": 24,
      "tasks_with_revision": 14,
      "transitions": 72,
      "revisions": 22
    },
    "retrieval": {
      "tasks": 24,
      "tasks_with_revision": 14,
      "transitions": 72,
      "revisions": 15
    },
    "plain": {
      "tasks": 24,
      "tasks_with_revision": 13,
      "transitions": 72,
      "revisions": 15
    },
    "structured": {
      "tasks": 24,
      "tasks_with_revision": 12,
      "transitions": 72,
      "revisions": 17
    },
    "shuffled": {
      "tasks": 24,
      "tasks_with_revision": 12,
      "transitions": 72,
      "revisions": 17
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
