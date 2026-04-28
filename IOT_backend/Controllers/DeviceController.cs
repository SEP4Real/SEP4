using IOT_backend.DbConfig;
using IOT_backend.Entities;

namespace IOT_backend.Controllers;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;

[ApiController]
[Route("[controller]")]
public class DeviceController : ControllerBase
{
    private readonly AppDbContext _db;

    public DeviceController(AppDbContext db)
    {
        _db = db;
    }

    [HttpGet]
    public async Task<IActionResult> GetAll()
    {
        var devices = await _db.Devices.ToListAsync();
        return Ok(devices);
    }

    [HttpGet("{publicKey}")]
    public async Task<IActionResult> GetByKey(string publicKey)
    {
        var device = await _db.Devices.FindAsync(publicKey);
        if (device == null) return NotFound();
        return Ok(device);
    }

    [HttpPost]
    public async Task<IActionResult> Post([FromBody] Device device)
    {
        if (string.IsNullOrWhiteSpace(device.PublicKey))
        {
            return BadRequest("Device publicKey is required");
        }

        device.PublicKey = device.PublicKey.Trim();

        var exists = await _db.Devices.AnyAsync(d => d.PublicKey == device.PublicKey);
        if (exists) return Conflict($"Device {device.PublicKey} already exists");

        _db.Devices.Add(device);
        await _db.SaveChangesAsync();
        return CreatedAtAction(nameof(GetByKey), new { publicKey = device.PublicKey }, device);
    }

    [HttpDelete("{publicKey}")]
    public async Task<IActionResult> Delete(string publicKey)
    {
        var device = await _db.Devices.FindAsync(publicKey);
        if (device == null) return NotFound();

        var hasSessions = await _db.Sessions.AnyAsync(s => s.DeviceId == publicKey);
        if (hasSessions)
        {
            return Conflict("Device has sessions and cannot be deleted without losing IoT history");
        }

        _db.Devices.Remove(device);
        await _db.SaveChangesAsync();
        return NoContent();
    }
}
