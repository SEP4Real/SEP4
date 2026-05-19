const API_URL = "http://localhost:8080";

export async function getCalendarEvents() {
  const token = localStorage.getItem("token");

  const response = await fetch(`${API_URL}/calendar-events`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    throw new Error("Failed to fetch calendar events");
  }

  return response.json();
}

export async function createCalendarEvent(eventData) {
  const token = localStorage.getItem("token");

  const response = await fetch(`${API_URL}/calendar-events`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },

    body: JSON.stringify(eventData),
  });

  if (!response.ok) {
    throw new Error("Failed to create event");
  }

  return response.json();
}

export async function updateCalendarEvent(eventId, eventData) {
  const token = localStorage.getItem("token");

  const response = await fetch(`${API_URL}/calendar-events/${eventId}`, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },

    body: JSON.stringify(eventData),
  });

  if (!response.ok) {
    throw new Error("Failed to update event");
  }

  return response.json();
}

export async function deleteCalendarEvent(eventId) {
  const token = localStorage.getItem("token");

  const response = await fetch(`${API_URL}/calendar-events/${eventId}`, {
    method: "DELETE",
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    throw new Error("Failed to delete event");
  }

  return response.json();
}