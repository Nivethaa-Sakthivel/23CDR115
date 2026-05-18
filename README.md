# Campus Notifications Microservice

A full-stack campus notification platform with Priority Inbox.

---

## Repository Structure

```
campus-notifications/
├── Notification_System_Design.md   ← Stage 1 design explanation
├── stage1/
│   └── priority_inbox.py           ← Stage 1: Priority Inbox logic (Python)
└── stage2/
    ├── package.json
    ├── next.config.js
    ├── tsconfig.json
    ├── lib/
    │   ├── theme.ts                 ← MUI theme
    │   ├── notifications.ts         ← API client + priority logic
    │   └── useNotifications.ts      ← React hook
    ├── components/
    │   ├── Layout.tsx               ← Sidebar navigation layout
    │   └── NotificationCard.tsx     ← Individual notification card
    └── pages/
        ├── _app.tsx                 ← MUI/Emotion setup
        ├── _document.tsx            ← SSR emotion
        ├── index.tsx                ← All Notifications page
        └── priority.tsx             ← Priority Inbox page
```

---

## Stage 1 — Priority Inbox (Python)

### Run

```bash
cd stage1
pip install requests
python priority_inbox.py
```

### Approach

- **Data structure**: Min-heap of size N (`heapq`)
- **Priority score**: `(type_weight, timestamp_epoch)` tuple
  - Placement (3) > Result (2) > Event (1)
  - More recent = higher priority (tiebreaker)
- **Efficiency**: O(log N) per new notification, O(N) space
- Handles continuous incoming notifications without reprocessing history

See `Notification_System_Design.md` for full design explanation.

---

## Stage 2 — React/Next.js Frontend

### Setup & Run

```bash
cd stage2
npm install
npm run dev
# Open http://localhost:3000
```

### Pages

| Page | Route | Description |
|------|-------|-------------|
| All Notifications | `/` | Paginated list with type filter, mark read/unread |
| Priority Inbox | `/priority` | Top-N by priority with type filter and N selector |

### Features

- **Material UI** styling (no ShadCN, no Tailwind)
- **Read/Unread distinction**: unread cards highlighted with blue border + "New" badge
- **Priority ranking**: rank badge (1–N) shown in Priority Inbox
- **Auto-refresh** every 30 seconds
- **Responsive**: mobile drawer + desktop sidebar
- **Filters**: by notification type (All / Placement / Result / Event)
- **Pagination**: `limit` + `page` query params
- **Error handling**: retry button on API failure
- **Loading skeletons**: smooth loading state

### API Used

```
GET http://4.224.186.213/evaluation-service/notifications
Query params: limit, page, notification_type
```

### Priority Logic (Frontend)

Same algorithm as Stage 1, implemented in TypeScript (`lib/notifications.ts`):
- All notifications fetched → client-side top-N computed via sort
- Score = `[type_weight, timestamp_epoch]` descending
