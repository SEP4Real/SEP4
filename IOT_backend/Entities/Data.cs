using System.Text.Json.Serialization;

namespace IOT_backend.Entities;
using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

[Table("data")]
public class Data
{
    [Key]
    [Column("id")]
    public long Id { get; set; }

    [Required]
    [Column("session_id")]
    public long SessionId { get; set; }

    [Column("temperature")]
    public double? Temperature { get; set; }

    [Column("humidity")]
    public double? Humidity { get; set; }

    [Column("co2_level")]
    public double? Co2Level { get; set; }

    [Column("light_level")]
    public double? LightLevel { get; set; }

    [Column("sent_at")]
    public DateTimeOffset SentAt { get; set; }

    [JsonIgnore]
    [ForeignKey("SessionId")]
    public Session? Session { get; set; }
}