using System.Text.Json.Serialization;

namespace IOT_backend.Entities;
using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

[Table("devices")]
public class Device
{
    [Key]
    [Column("public_key")]
    [MaxLength(255)]
    public string PublicKey { get; set; }

    [JsonIgnore]
    public ICollection<Session>? Sessions { get; set; }
}