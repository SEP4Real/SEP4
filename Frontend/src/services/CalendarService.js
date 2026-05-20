import { apiFetch } from "./apiConfig";

export async function getCalendarEvents() {
  const response = await apiFetch("/calendar-events");

  if (!response.ok) {
    throw new Error("Failed to fetch calendar events");
  }

  return response.json();
}

export async function createCalendarEvent(eventData) {
  const response = await apiFetch("/calendar-events", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },

    body: JSON.stringify(eventData),
  });

  if (!response.ok) {
    throw new Error("Failed to create event");
  }

  return response.json();
}

export async function updateCalendarEvent(eventId, eventData) {
  const response = await apiFetch(`/calendar-events/${eventId}`, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
    },

    body: JSON.stringify(eventData),
  });

  if (!response.ok) {
    throw new Error("Failed to update event");
  }

  return response.json();
}

export async function deleteCalendarEvent(eventId) {
  const response = await apiFetch(`/calendar-events/${eventId}`, {
    method: "DELETE",
  });

  if (!response.ok) {
    throw new Error("Failed to delete event");
  }

  return response.json();
}
