namespace IOT_backend.DbConfig;
using Entities;
using Microsoft.EntityFrameworkCore;

public class AppDbContext : DbContext
{
    public AppDbContext(DbContextOptions<AppDbContext> options) : base(options) {}

    public DbSet<Device> Devices { get; set; }
    public DbSet<Session> Sessions { get; set; }
    public DbSet<Entities.Data> DataPoints { get; set; }
}