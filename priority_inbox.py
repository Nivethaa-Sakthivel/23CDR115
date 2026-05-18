"""
Campus Notifications - Priority Inbox (Stage 1)

Priority is determined by:
  1. Type weight: Placement (3) > Result (2) > Event (1)
  2. Recency: more recent = higher priority (tiebreaker)

Uses a max-heap (via heapq with negated values) to efficiently maintain top-N notifications.
New notifications arriving can be handled in O(log N) time.
"""

import heapq
import requests
from datetime import datetime

# ─── Configuration ───────────────────────────────────────────────────────────

API_URL = "http://4.224.186.213/evaluation-service/notifications"
TOP_N = 10  # configurable: 10, 15, 20, etc.

TYPE_WEIGHT = {
    "Placement": 3,
    "Result": 2,
    "Event": 1,
}

# ─── Priority Inbox Class ─────────────────────────────────────────────────────

class PriorityInbox:
    """
    Maintains top-N priority notifications efficiently using a min-heap of size N.
    
    Each notification's priority score = (type_weight, timestamp_epoch).
    A min-heap of size N lets us:
      - Add a new notification in O(log N)
      - Always keep only the top-N highest-priority items
    """

    def __init__(self, top_n: int = 10):
        self.top_n = top_n
        self._heap = []  # min-heap: (score_tuple, notification)

    def _score(self, notification: dict) -> tuple:
        """
        Returns a comparable score tuple for a notification.
        Higher is better. We negate for min-heap logic.
        """
        weight = TYPE_WEIGHT.get(notification["Type"], 0)
        ts = datetime.strptime(notification["Timestamp"], "%Y-%m-%d %H:%M:%S")
        epoch = ts.timestamp()
        return (weight, epoch)

    def add(self, notification: dict):
        """Add a notification, maintaining only top-N."""
        score = self._score(notification)
        # We store as (score, notification) in a MIN-heap
        # So the smallest (lowest priority) gets popped when heap exceeds N
        if len(self._heap) < self.top_n:
            heapq.heappush(self._heap, (score, notification))
        else:
            # Only replace if this notification has higher priority than the current min
            if score > self._heap[0][0]:
                heapq.heapreplace(self._heap, (score, notification))

    def get_top_n(self) -> list:
        """Return top-N notifications sorted by priority (highest first)."""
        return [item[1] for item in sorted(self._heap, key=lambda x: x[0], reverse=True)]

    def load_bulk(self, notifications: list):
        """Load a list of notifications in bulk."""
        for n in notifications:
            self.add(n)


# ─── Fetch Notifications ──────────────────────────────────────────────────────

def fetch_notifications(token: str = None) -> list:
    """Fetch notifications from the API."""
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    try:
        response = requests.get(API_URL, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data.get("notifications", [])
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Failed to fetch notifications: {e}")
        return []


# ─── Display ──────────────────────────────────────────────────────────────────

def display_priority_inbox(notifications: list, top_n: int):
    print(f"\n{'='*60}")
    print(f"  📬  PRIORITY INBOX  —  Top {top_n} Notifications")
    print(f"{'='*60}")
    print(f"{'#':<4} {'Type':<12} {'Weight':<8} {'Timestamp':<22} {'Message'}")
    print(f"{'-'*60}")

    for idx, n in enumerate(notifications, 1):
        weight = TYPE_WEIGHT.get(n["Type"], 0)
        print(f"{idx:<4} {n['Type']:<12} {weight:<8} {n['Timestamp']:<22} {n['Message']}")

    print(f"{'='*60}\n")


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    # If the API requires a token, set it here
    AUTH_TOKEN = None  # e.g. "your-token-here"

    print(f"[INFO] Fetching notifications from {API_URL} ...")
    all_notifications = fetch_notifications(token=AUTH_TOKEN)

    if not all_notifications:
        # Demo fallback data for local testing when API is unreachable
        print("[WARN] No notifications fetched. Using demo data.\n")
        all_notifications = [
            {"ID": "1", "Type": "Placement", "Message": "Google hiring", "Timestamp": "2026-04-22 18:00:00"},
            {"ID": "2", "Type": "Placement", "Message": "Amazon SDE drive", "Timestamp": "2026-04-22 17:55:00"},
            {"ID": "3", "Type": "Result", "Message": "Mid-sem results published", "Timestamp": "2026-04-22 17:51:30"},
            {"ID": "4", "Type": "Result", "Message": "Assignment 3 graded", "Timestamp": "2026-04-22 17:40:00"},
            {"ID": "5", "Type": "Event", "Message": "Farewell party tomorrow", "Timestamp": "2026-04-22 17:51:06"},
            {"ID": "6", "Type": "Placement", "Message": "CSX Corporation hiring", "Timestamp": "2026-04-22 17:51:18"},
            {"ID": "7", "Type": "Event", "Message": "Hackathon registration open", "Timestamp": "2026-04-22 17:30:00"},
            {"ID": "8", "Type": "Result", "Message": "End-sem timetable released", "Timestamp": "2026-04-22 17:20:00"},
            {"ID": "9", "Type": "Event", "Message": "Guest lecture: Dr. Smith", "Timestamp": "2026-04-22 16:00:00"},
            {"ID": "10", "Type": "Placement", "Message": "Microsoft internship drive", "Timestamp": "2026-04-22 15:45:00"},
            {"ID": "11", "Type": "Event", "Message": "Sports meet next week", "Timestamp": "2026-04-22 14:00:00"},
            {"ID": "12", "Type": "Result", "Message": "Quiz 2 marks updated", "Timestamp": "2026-04-22 13:30:00"},
        ]

    print(f"[INFO] Total notifications received: {len(all_notifications)}")

    inbox = PriorityInbox(top_n=TOP_N)
    inbox.load_bulk(all_notifications)

    top_notifications = inbox.get_top_n()
    display_priority_inbox(top_notifications, TOP_N)

    # Simulate a new notification arriving (streaming scenario)
    print("[INFO] Simulating a new incoming notification ...\n")
    new_notification = {
        "ID": "new-1",
        "Type": "Placement",
        "Message": "Apple Inc. campus drive",
        "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    inbox.add(new_notification)
    print(f"[INFO] Added: [{new_notification['Type']}] {new_notification['Message']}")
    print("[INFO] Updated Priority Inbox:\n")
    top_notifications = inbox.get_top_n()
    display_priority_inbox(top_notifications, TOP_N)


if __name__ == "__main__":
    main()
