# Stage 1 — Notification System Design

## Overview

The Priority Inbox ensures that students always see the **top N most important unread notifications** first, regardless of the total volume of incoming notifications.

---

## Priority Model

Each notification is scored using two factors:

| Factor       | Logic                                                                 |
|-------------|-----------------------------------------------------------------------|
| **Type Weight** | `Placement = 3`, `Result = 2`, `Event = 1`                        |
| **Recency**     | More recent timestamp → higher priority (used as tiebreaker)      |

The composite score is a tuple `(type_weight, timestamp_epoch)`. Tuples are compared lexicographically — type weight wins first; recency breaks ties.

---

## Data Structure: Min-Heap of Size N

### Why a Heap?

A naive approach (sort all, take top N) costs **O(M log M)** every time a new notification arrives, where M is the total number of notifications. This becomes expensive as M grows.

Instead, we maintain a **min-heap of exactly N elements**:

- The root of the heap is always the **lowest-priority item** among the current top-N.
- When a new notification arrives:
  - If its score > heap root → replace root and re-heapify → **O(log N)**
  - Otherwise → discard → **O(1)**

This gives us:
- **O(M log N)** for bulk loading M notifications
- **O(log N)** per new incoming notification
- **O(N log N)** to retrieve sorted top-N

Since N is small (10, 15, 20) and fixed, this is essentially **O(1) per new notification** in practice.

---

## Algorithm (Step-by-Step)

```
1. Fetch all notifications from API
2. For each notification:
     a. Compute score = (type_weight, timestamp_epoch)
     b. If heap size < N: push to heap
     c. Else if score > heap[0] (min): heapreplace(heap, new item)
3. Sort heap descending → top-N notifications
4. Display
```

---

## Handling Continuous Incoming Notifications

New notifications will keep arriving (real-time stream). The heap handles this gracefully:

```python
inbox.add(new_notification)  # O(log N) — heap stays bounded at size N
```

No need to re-process all historical notifications. The heap is always up-to-date.

---

## Code Structure

```
stage1/
└── priority_inbox.py   # PriorityInbox class + fetch + CLI display
```

### Key Classes / Functions

| Name | Responsibility |
|------|---------------|
| `PriorityInbox` | Maintains top-N heap; exposes `add()` and `get_top_n()` |
| `fetch_notifications()` | HTTP GET from the notifications API |
| `display_priority_inbox()` | CLI table output |
| `main()` | Orchestrates fetch → load → display → simulate new arrival |

---

## Trade-offs Considered

| Option | Pros | Cons | Decision |
|--------|------|------|----------|
| Sort all notifications | Simple | O(M log M) per update | ❌ Rejected |
| Min-heap of size N | O(log N) per update, O(N) space | Slightly more complex | ✅ Chosen |
| Priority Queue (DB) | Persistent, scalable | DB not required for this stage | ❌ Out of scope |

---

## Sample Output

```
============================================================
  📬  PRIORITY INBOX  —  Top 10 Notifications
============================================================
#    Type         Weight   Timestamp              Message
------------------------------------------------------------
1    Placement    3        2026-04-22 18:00:00    Google hiring
2    Placement    3        2026-04-22 17:55:00    Amazon SDE drive
3    Placement    3        2026-04-22 17:51:18    CSX Corporation hiring
4    Result       2        2026-04-22 17:51:30    Mid-sem results published
5    Result       2        2026-04-22 17:40:00    Assignment 3 graded
...
============================================================
```

---

## Stage 2 Preview

Stage 2 extends this with a full React/Next.js frontend using Material UI, supporting:
- All Notifications view (paginated)
- Priority Inbox view (top-N + type filter)
- Read/unread distinction
- Query parameters: `limit`, `page`, `notification_type`


