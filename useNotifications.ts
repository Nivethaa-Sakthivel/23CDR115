import { useState, useEffect, useCallback, useRef } from "react";
import { Notification, fetchNotifications, NotificationType } from "./notifications";

interface UseNotificationsOptions {
  limit?: number;
  page?: number;
  notification_type?: NotificationType | "";
  autoRefresh?: boolean;
  refreshInterval?: number; // ms
}

export function useNotifications(options: UseNotificationsOptions = {}) {
  const { limit, page = 1, notification_type, autoRefresh = false, refreshInterval = 30000 } = options;

  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [readIds, setReadIds] = useState<Set<string>>(new Set());

  const seenIdsRef = useRef<Set<string>>(new Set());

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchNotifications({ limit, page, notification_type });
      setNotifications(data);
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : "Failed to fetch notifications";
      setError(message);
    } finally {
      setLoading(false);
    }
  }, [limit, page, notification_type]);

  useEffect(() => {
    load();
  }, [load]);

  useEffect(() => {
    if (!autoRefresh) return;
    const interval = setInterval(load, refreshInterval);
    return () => clearInterval(interval);
  }, [autoRefresh, load, refreshInterval]);

  // Mark notification as read
  const markRead = useCallback((id: string) => {
    setReadIds((prev) => new Set([...prev, id]));
    seenIdsRef.current.add(id);
  }, []);

  const markAllRead = useCallback(() => {
    setReadIds((prev) => {
      const next = new Set(prev);
      notifications.forEach((n) => next.add(n.ID));
      return next;
    });
  }, [notifications]);

  const isRead = useCallback(
    (id: string) => readIds.has(id),
    [readIds]
  );

  const unreadCount = notifications.filter((n) => !readIds.has(n.ID)).length;

  return {
    notifications,
    loading,
    error,
    reload: load,
    markRead,
    markAllRead,
    isRead,
    unreadCount,
  };
}
