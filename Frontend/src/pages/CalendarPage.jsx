import FullCalendar from '@fullcalendar/react';
import dayGridPlugin from '@fullcalendar/daygrid';
import interactionPlugin from '@fullcalendar/interaction';
import timeGridPlugin from '@fullcalendar/timegrid';

const CalendarPage = () => {

  const handleSelect = (info) => {
    const title = prompt("Event title:");
    if (title) {
      info.view.calendar.addEvent({
        title: title,
        start: info.start,
        end: info.end,
        allDay: info.allDay
      });
    }
  };

  return (
    <div style={{ padding: "20px" }}>
      <h2>Calendar</h2>

      <FullCalendar
        plugins={[dayGridPlugin, timeGridPlugin, interactionPlugin]}
        initialView="timeGridWeek"
        selectable={true}
        select={handleSelect}
        editable={true}
        eventDurationEditable={true}
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
    </div>
  );
};

export default CalendarPage;