using IOT_backend.DbConfig;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;

namespace IOT_backend.Controllers;

[ApiController]
[Route("[controller]")]
public class HealthController : ControllerBase
{
    private readonly AppDbContext _db;

    public HealthController(AppDbContext db)
    {
        _db = db;
    }

    [HttpGet("db")]
    public async Task<IActionResult> Db()
    {
        var canConnect = await _db.Database.CanConnectAsync();
        if (!canConnect)
        {
            return StatusCode(StatusCodes.Status503ServiceUnavailable, new { status = "unhealthy", database = "unreachable" });
        }

        var missingTables = new List<string>();

        foreach (var table in new[] { "devices", "sessions", "data" })
        {
            var exists = await _db.Database
                .SqlQueryRaw<bool>("SELECT to_regclass({0}) IS NOT NULL AS \"Value\"", $"public.{table}")
                .SingleAsync();

            if (!exists)
            {
                missingTables.Add(table);
            }
        }

        if (missingTables.Count > 0)
        {
            return StatusCode(StatusCodes.Status503ServiceUnavailable, new { status = "unhealthy", missingTables });
        }

        return Ok(new { status = "ok", tables = new[] { "devices", "sessions", "data" } });
    }
}
