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
        var deviceExists = await _db.Devices.AnyAsync(d => d.PublicKey == session.DeviceId);
        if (!deviceExists) return NotFound($"Device {session.DeviceId} does not exist");

        session.StartedAt = DateTimeOffset.UtcNow;
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

    [HttpDelete("{id}")]
    public async Task<IActionResult> Delete(long id)
    {
        var session = await _db.Sessions.FindAsync(id);
        if (session == null) return NotFound();

        _db.Sessions.Remove(session);
        await _db.SaveChangesAsync();
        return NoContent();
    }
}