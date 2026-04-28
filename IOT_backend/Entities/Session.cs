using System.Text.Json.Serialization;

namespace IOT_backend.Entities;
using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

[Table("sessions")]
public class Session
{
    [Key]
    [Column("id")]
    public long Id { get; set; }

    [Required]
    [Column("device_id")]
    public string DeviceId { get; set; }

    [Column("started_at")]
    public DateTimeOffset StartedAt { get; set; }

    [Column("ended_at")]
    public DateTimeOffset? EndedAt { get; set; }

    [Column("study_quality")]
    [Range(1, 10)]
    public int? StudyQuality { get; set; }
    
    [Column("last_pulse_at")]
    public DateTimeOffset? LastPulseAt { get; set; }

    [JsonIgnore]
    [ForeignKey("DeviceId")]
    public Device? Device { get; set; }

    [JsonIgnore]
    public ICollection<Data>? DataPoints { get; set; }
}