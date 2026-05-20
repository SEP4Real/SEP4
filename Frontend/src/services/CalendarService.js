import { API_URL } from "./apiConfig";

export async function getCalendarEvents() {
  const response = await fetch(`${API_URL}/calendar-events`, {
    credentials: "include",
  });

  if (!response.ok) {
    throw new Error("Failed to fetch calendar events");
  }

  return response.json();
}

export async function createCalendarEvent(eventData) {
  const response = await fetch(`${API_URL}/calendar-events`, {
    method: "POST",
    credentials: "include",
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
  const response = await fetch(`${API_URL}/calendar-events/${eventId}`, {
    method: "PUT",
    credentials: "include",
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
  const response = await fetch(`${API_URL}/calendar-events/${eventId}`, {
    method: "DELETE",
    credentials: "include",
  });

  if (!response.ok) {
    throw new Error("Failed to delete event");
  }

  return response.json();
}
