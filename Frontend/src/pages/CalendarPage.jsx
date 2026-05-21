import { useState, useEffect } from 'react';
import FullCalendar from '@fullcalendar/react';
import dayGridPlugin from '@fullcalendar/daygrid';
import timeGridPlugin from '@fullcalendar/timegrid';
import interactionPlugin from '@fullcalendar/interaction';
import './CalendarPage.css';
import { useLanguage } from "../context/LanguageContext";
import {getCalendarEvents, createCalendarEvent, updateCalendarEvent, deleteCalendarEvent} from "../services/CalendarService";

const CalendarPage = () => {
const { language, t } = useLanguage();
  // popup + selection state
  const [popupOpen, setPopupOpen] = useState(false);
  const [popupPos, setPopupPos] = useState({ x: 0, y: 0 });
  const [selectedEvent, setSelectedEvent] = useState(null);

  // form data
  const [title, setTitle] = useState("");
  const [note, setNote] = useState("");
  const [timeInfo, setTimeInfo] = useState(null);
  const [events, setEvents] = useState([]);

  useEffect(() => {
    const loadEvents = async () => {
      try {
        const data = await getCalendarEvents();

        const formattedEvents = data.map(event => ({
          id: event.id,
          title: event.title,
          start: event.start_time,
          end: event.end_time,
          allDay: event.all_day,

          extendedProps: {
            note: event.note
          }
        }));

        setEvents(formattedEvents);

      } catch (e) {
        console.error("Error loading calendar events:", e);
      }
    };

    loadEvents();

  }, []);

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
      const editEvent = async () => {
  try {
    const updatedEvent = await updateCalendarEvent(
      selectedEvent.id,
      {
        title,
        note,
        start_time: selectedEvent.start.toLocaleString("sv-SE").replace(" ", "T"),
        end_time: selectedEvent.end.toLocaleString("sv-SE").replace(" ", "T"),
        all_day: selectedEvent.allDay
      }
    );

    setEvents(prev =>
      prev.map(event =>
        event.id === updatedEvent.id
          ? {
            id: updatedEvent.id,
            title: updatedEvent.title,
            start: updatedEvent.start_time,
            end: updatedEvent.end_time,
            allDay: updatedEvent.all_day,

              extendedProps: {
                note: updatedEvent.note
              }
            }
          : event
      )
    );

  } catch (e) {
    console.error(e);
  }};

  editEvent();
      } else {
        // create new event
        const createEvent = async () => {
        try {
          const createdEvent = await createCalendarEvent({
            title,
            note,
            start_time: timeInfo.startStr,
            end_time: timeInfo.endStr,
            all_day: timeInfo.allDay
          });

          setEvents(prev => [
            ...prev,
            {
              id: createdEvent.id,
              title: createdEvent.title,
              start: createdEvent.start_time,
              end: createdEvent.end_time,
              allDay: createdEvent.all_day,

              extendedProps: {
                note: createdEvent.note
              }
            }
          ]);

        } catch (e) {
          console.error(e);
        }
      };
      createEvent();
      }

      setPopupOpen(false);
    };

  // delete event
  const handleDelete = () => {
    if (selectedEvent) {
      const deleteEvent = async () => {
    try {
      await deleteCalendarEvent(selectedEvent.id);

      setEvents(prev =>
        prev.filter(event => event.id !== selectedEvent.id)
      );

    } catch (e) {
      console.error(e);
    }
  };

  deleteEvent();
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
     <h2>{t.calendar}</h2>

      {/* calendar component */}
      <FullCalendar
      allDayText={t.calendarAllDay}
      locale={language === "da" ? "da" : "en"}
      buttonText={{ today: t.calendarToday,month: t.calendarMonth,week: t.calendarWeek,day: t.calendarDay}}
        plugins={[dayGridPlugin, timeGridPlugin, interactionPlugin]}
        initialView="timeGridWeek"
        selectable={true}
        select={handleSelect} // create event
        editable={true} // drag + resize
        eventDurationEditable={true}
        events={events}
        timeZone="local"
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
   <h3>{selectedEvent? t.editEvent: t.newEvent}</h3>
<label className="popup-label">{t.eventTitle}</label>
          {/* event title */}
          <input
            type="text"
           placeholder={t.eventTitlePlaceholder}
            value={title}
            onChange={(e) => setTitle(e.target.value)}
          />
          <label className="popup-label">{t.eventNote}</label>

          {/* event note */}
          <textarea
            placeholder={t.eventTitle}
            value={note}
            onChange={(e) => setNote(e.target.value)}
          />

          {/* actions */}
          <div className="popup-buttons">
            <button onClick={handleSave}>{t.save}</button>

            {selectedEvent && (
  <button
    type="button"
    className="delete-button"
    onClick={handleDelete}
  >
    🗑 {t.delete}
  </button>
)}
          </div>

        </div>
      )}
    </div>
  );
};

export default CalendarPage;
