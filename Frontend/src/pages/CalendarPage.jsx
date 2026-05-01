import { useState } from 'react';
import FullCalendar from '@fullcalendar/react';
import dayGridPlugin from '@fullcalendar/daygrid';
import timeGridPlugin from '@fullcalendar/timegrid';
import interactionPlugin from '@fullcalendar/interaction';
import './CalendarPage.css';

const CalendarPage = () => {

  // popup + selection state
  const [popupOpen, setPopupOpen] = useState(false);
  const [popupPos, setPopupPos] = useState({ x: 0, y: 0 });
  const [selectedEvent, setSelectedEvent] = useState(null);

  // form data
  const [title, setTitle] = useState("");
  const [note, setNote] = useState("");
  const [timeInfo, setTimeInfo] = useState(null);

  // user selects a time range → open popup for new event
  const handleSelect = (info) => {
    const rect = info.jsEvent
      ? { left: info.jsEvent.clientX, top: info.jsEvent.clientY }
      : { left: 200, top: 200 };

    // popup position
    setPopupPos({ x: rect.left, y: rect.top });

    // reset form
    setSelectedEvent(null);
    setTitle("");
    setNote("");
    setTimeInfo(info);

    setPopupOpen(true);
  };

  // user clicks existing event → open popup for editing
  const handleEventClick = (info) => {
    const rect = info.el.getBoundingClientRect();

    // popup position
    setPopupPos({ x: rect.left, y: rect.top });

    // load event data into form
    setSelectedEvent(info.event);
    setTitle(info.event.title);
    setNote(info.event.extendedProps.note || "");
    setTimeInfo(null);

    setPopupOpen(true);
  };

  // save event
  const handleSave = () => {
    if (!title) return; // prevent empty events

    if (selectedEvent) {
      // update existing event
      selectedEvent.setProp("title", title);
      selectedEvent.setExtendedProp("note", note);
    } else {
      // create new event
      timeInfo.view.calendar.addEvent({
        title,
        start: timeInfo.start,
        end: timeInfo.end,
        allDay: timeInfo.allDay,
        extendedProps: { note }
      });
    }

    setPopupOpen(false);
  };

  // delete event
  const handleDelete = () => {
    if (selectedEvent) {
      selectedEvent.remove();
    }
    setPopupOpen(false);
  };

  // popup position
  const popupWidth = 260;
  const popupHeight = 240;
  const OFFSET = 40;

  const isRightSide = popupPos.x > window.innerWidth / 2;
  const isBottom = popupPos.y > window.innerHeight / 2;

  const left = isRightSide
    ? popupPos.x - popupWidth - 10
    : popupPos.x + 10;

  const top = isBottom
    ? popupPos.y - popupHeight - OFFSET
    : popupPos.y + 10;

  return (
    <div className="calendar-container">
      <h2>Calendar</h2>

      {/* calendar component */}
      <FullCalendar
        plugins={[dayGridPlugin, timeGridPlugin, interactionPlugin]}
        initialView="timeGridWeek"
        selectable={true}
        select={handleSelect} // create event
        editable={true} // drag + resize
        eventDurationEditable={true}
        eventClick={handleEventClick} // edit event
        slotLabelFormat={{
          hour: '2-digit',
          minute: '2-digit',
          hour12: false
        }}
        headerToolbar={{
          left: "prev,next today",
          center: "title",
          right: "dayGridMonth,timeGridWeek,timeGridDay"
        }}
      />

      {/* popup for create and edit */}
      {popupOpen && (
        <div className="popup" style={{ top, left }}>

          {/* close popup */}
          <div className="popup-close">
            <span onClick={() => setPopupOpen(false)}>✕</span>
          </div>

          {/* dynamic title */}
          <h3>{selectedEvent ? "Edit Event" : "New Event"}</h3>

          {/* event title */}
          <input
            type="text"
            placeholder="Title"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
          />

          {/* event note */}
          <textarea
            placeholder="Note"
            value={note}
            onChange={(e) => setNote(e.target.value)}
          />

          {/* actions */}
          <div className="popup-buttons">
            <button onClick={handleSave}>Save</button>

            {selectedEvent && (
              <span
                className="delete-icon"
                onClick={handleDelete}
              >
                🗑
              </span>
            )}
          </div>

        </div>
      )}
    </div>
  );
};

export default CalendarPage;