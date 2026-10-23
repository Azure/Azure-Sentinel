using System;
using System.IO;
using System.Linq;
using System.Text;
using System.Text.Json;

// Edit only the root value's UTF-8 token, not reserialized metadata or nested names.
public static class AttributionMetadata
{
    public static void Save(string path, byte[] expected, string trackingId)
    {
        int bom = expected.Length >= 3 && expected[0] == 239 &&
            expected[1] == 187 && expected[2] == 191 ? 3 : 0;
        var reader = new Utf8JsonReader(expected.AsSpan(bom));
        if (!reader.Read() || reader.TokenType != JsonTokenType.StartObject)
            throw new InvalidDataException("Solution metadata must be a JSON object.");
        int start = -1, end = -1, first = -1, close = -1;
        while (reader.Read())
        {
            if (reader.TokenType == JsonTokenType.EndObject && reader.CurrentDepth == 0)
                close = checked((int)reader.TokenStartIndex) + bom;
            if (reader.TokenType != JsonTokenType.PropertyName || reader.CurrentDepth != 1)
                continue;
            if (first < 0) first = checked((int)reader.TokenStartIndex) + bom;
            bool matches = string.Equals(reader.GetString(), "trackingId", StringComparison.OrdinalIgnoreCase);
            reader.Read();
            if (matches)
            {
                if (start >= 0) throw new InvalidDataException("Duplicate root trackingId fields.");
                if (reader.TokenType != JsonTokenType.Null &&
                    (reader.TokenType != JsonTokenType.String || !string.IsNullOrWhiteSpace(reader.GetString())))
                    throw new InvalidDataException("Refusing to replace a nonblank trackingId.");
                start = checked((int)reader.TokenStartIndex) + bom;
                end = checked((int)reader.BytesConsumed) + bom;
            }
            reader.Skip();
        }
        if (close < 0) throw new InvalidDataException("Incomplete solution metadata.");
        string value = JsonSerializer.Serialize(trackingId);
        if (start < 0)
        {
            start = end = first < 0 ? close : first;
            string spacing = Encoding.UTF8.GetString(expected, bom + 1, start - bom - 1);
            value = "\"trackingId\": " + value + (first < 0 ? "" : "," + spacing);
        }
        byte[] replacement = Encoding.UTF8.GetBytes(value);
        byte[] updated = new byte[start + replacement.Length + expected.Length - end];
        Buffer.BlockCopy(expected, 0, updated, 0, start);
        Buffer.BlockCopy(replacement, 0, updated, start, replacement.Length);
        Buffer.BlockCopy(expected, end, updated, start + replacement.Length, expected.Length - end);

        // A same-directory replacement avoids partial JSON on failure. Check the
        // snapshot while holding a writer-excluding handle before atomic rename.
        string staging = path + ".attribution-" + Guid.NewGuid().ToString("N");
        try
        {
            using (var current = new FileStream(path, FileMode.Open, FileAccess.ReadWrite,
                FileShare.Read | FileShare.Delete))
            {
                using (var buffer = new MemoryStream())
                {
                    current.CopyTo(buffer);
                    if (!expected.SequenceEqual(buffer.ToArray()))
                        throw new IOException("Solution metadata changed during attribution lookup; retry packaging.");
                }
                using (var output = new FileStream(staging, FileMode.CreateNew, FileAccess.Write, FileShare.None))
                {
                    output.Write(updated, 0, updated.Length);
                    output.Flush(true);
                }
                // Unix mode APIs were added in .NET 7; keep earlier PowerShell 7
                // runtimes usable without introducing a new runtime dependency.
                var getMode = typeof(File).GetMethod("GetUnixFileMode", new[] { typeof(string) });
                if (Path.DirectorySeparatorChar == '/' && getMode != null)
                {
                    object mode = getMode.Invoke(null, new object[] { path });
                    typeof(File).GetMethod("SetUnixFileMode", new[] { typeof(string), mode.GetType() })
                        .Invoke(null, new object[] { staging, mode });
                }
                // Windows overwrite-move fails while the destination is open;
                // Replace supports the writer-excluding, delete-sharing handle.
                if (Path.DirectorySeparatorChar == '\\')
                    File.Replace(staging, path, null);
                else
                    File.Move(staging, path, true);
            }
        }
        finally
        {
            if (File.Exists(staging)) File.Delete(staging);
        }
    }
}
