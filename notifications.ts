export type NotificationType = "Placement" | "Result" | "Event";

export interface Notification {
  ID: string;
  Type: NotificationType;
  Message: string;
  Timestamp: string;
}

export interface NotificationsResponse {
  notifications: Notification[];
}

// Type weights for priority scoring
export const TYPE_WEIGHT: Record<NotificationType, number> = {
  Placement: 3,
  Result: 2,
  Event: 1,
};

export function priorityScore(n: Notification): [number, number] {
  const weight = TYPE_WEIGHT[n.Type] ?? 0;
  const ts = new Date(n.Timestamp.replace(" ", "T")).getTime();
  return [weight, ts];
}

export function compareNotifications(a: Notification, b: Notification): number {
  const [wa, ta] = priorityScore(a);
  const [wb, tb] = priorityScore(b);
  if (wb !== wa) return wb - wa;   // higher weight first
  return tb - ta;                  // more recent first
}

const API_BASE = "/api/notifications";

export async function fetchNotifications(params?: {
  limit?: number;
  page?: number;
  notification_type?: NotificationType | "";
}): Promise<Notification[]> {
  const url = new URL(API_BASE, typeof window === "undefined" ? "http://localhost" : window.location.origin);
  if (params?.limit) url.searchParams.set("limit", String(params.limit));
  if (params?.page) url.searchParams.set("page", String(params.page));
  if (params?.notification_type) url.searchParams.set("notification_type", params.notification_type);

  const res = await fetch(url.toString(), { cache: "no-store" });
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  const data: NotificationsResponse = await res.json();
  return data.notifications ?? [];
}

export function getTopN(notifications: Notification[], n: number): Notification[] {
  return [...notifications].sort(compareNotifications).slice(0, n);
}
