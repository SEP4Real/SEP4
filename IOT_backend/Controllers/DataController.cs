using IOT_backend.DbConfig;
using IOT_backend.Entities;

namespace IOT_backend.Controllers;
using Microsoft.EntityFrameworkCore;
using Microsoft.AspNetCore.Mvc;

[ApiController]
[Route("[controller]")]
public class DataController : ControllerBase
{
    private readonly AppDbContext _db;

    public DataController(AppDbContext db)
    {
        _db = db;
    }

    [HttpGet]
    public async Task<IActionResult> GetAll()
    {
        var data = await _db.DataPoints.ToListAsync();
        return Ok(data);
    }

    [HttpGet("{id}")]
    public async Task<IActionResult> GetById(long id)
    {
        var data = await _db.DataPoints.FindAsync(id);
        if (data == null) return NotFound();
        return Ok(data);
    }

    [HttpGet("session/{sessionId}")]
    public async Task<IActionResult> GetBySession(long sessionId)
    {
        var data = await _db.DataPoints
            .Where(d => d.SessionId == sessionId)
            .ToListAsync();
        return Ok(data);
    }

    [HttpPost]
    public async Task<IActionResult> Post([FromBody] Data data)
    {
        if (data.SessionId <= 0)
        {
            return BadRequest("sessionId is required");
        }

        var session = await _db.Sessions.FindAsync(data.SessionId);
        if (session == null)
        {
            return NotFound($"Session {data.SessionId} does not exist");
        }

        if (session.EndedAt != null)
        {
            return Conflict("Cannot add data to an ended session");
        }

        data.SentAt = DateTimeOffset.UtcNow;
        _db.DataPoints.Add(data);
        await _db.SaveChangesAsync();
        return CreatedAtAction(nameof(GetById), new { id = data.Id }, data);
    }
}
