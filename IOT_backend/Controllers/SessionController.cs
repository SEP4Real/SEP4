using IOT_backend.DbConfig;
using IOT_backend.Entities;

namespace IOT_backend.Controllers;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;

[ApiController]
[Route("[controller]")]
public class SessionController : ControllerBase
{
    private readonly AppDbContext _db;

    public SessionController(AppDbContext db)
    {
        _db = db;
    }

    [HttpGet]
    public async Task<IActionResult> GetAll()
    {
        var sessions = await _db.Sessions.ToListAsync();
        return Ok(sessions);
    }

    [HttpGet("{id}")]
    public async Task<IActionResult> GetById(long id)
    {
        var session = await _db.Sessions.FindAsync(id);
        if (session == null) return NotFound();

        if (session.EndedAt == null && session.LastPulseAt != null)
        {
            var elapsed = DateTimeOffset.UtcNow - session.LastPulseAt.Value;
            if (elapsed.TotalSeconds > 15)
            {
                session.EndedAt = session.LastPulseAt.Value;
                await _db.SaveChangesAsync();
            }
        }

        return Ok(session);
    }

    [HttpGet("device/{publicKey}")]
    public async Task<IActionResult> GetByDevice(string publicKey)
    {
        var sessions = await _db.Sessions
            .Where(s => s.DeviceId == publicKey)
            .ToListAsync();
        return Ok(sessions);
    }

    [HttpPost]
    public async Task<IActionResult> Post([FromBody] Session session)
    {
        if (string.IsNullOrWhiteSpace(session.DeviceId))
        {
            return BadRequest("deviceId is required");
        }

        session.DeviceId = session.DeviceId.Trim();

        var deviceExists = await _db.Devices.AnyAsync(d => d.PublicKey == session.DeviceId);
        if (!deviceExists) return NotFound($"Device {session.DeviceId} does not exist");

        session.StartedAt = DateTimeOffset.UtcNow;
        session.LastPulseAt = session.StartedAt;
        _db.Sessions.Add(session);
        await _db.SaveChangesAsync();
        return CreatedAtAction(nameof(GetById), new { id = session.Id }, session);
    }

    [HttpPatch("{id}/end")]
    public async Task<IActionResult> EndSession(long id, [FromBody] int? studyQuality)
    {
        var session = await _db.Sessions.FindAsync(id);
        if (session == null) return NotFound();
        if (session.EndedAt != null) return Conflict("Session already ended");

        session.EndedAt = DateTimeOffset.UtcNow;
        session.StudyQuality = studyQuality;
        await _db.SaveChangesAsync();
        return Ok(session);
    }
    
    [HttpPatch("{id}/pulse")]
    public async Task<IActionResult> Pulse(long id)
    {
        var session = await _db.Sessions.FindAsync(id);
        if (session == null) return NotFound();
        if (session.EndedAt != null) return Ok(new { alive = false });

        session.LastPulseAt = DateTimeOffset.UtcNow;
        await _db.SaveChangesAsync();
        return Ok(new { alive = true });
    }

    [HttpDelete("{id}")]
    public async Task<IActionResult> Delete(long id)
    {
        var session = await _db.Sessions.FindAsync(id);
        if (session == null) return NotFound();

        var hasData = await _db.DataPoints.AnyAsync(d => d.SessionId == id);
        if (hasData)
        {
            return Conflict("Session has data points and cannot be deleted without losing IoT history");
        }

        _db.Sessions.Remove(session);
        await _db.SaveChangesAsync();
        return NoContent();
    }
    
}
