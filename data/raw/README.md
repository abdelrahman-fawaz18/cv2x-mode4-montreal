# Raw simulation exports

The two OMNeT++ `scavetool` CSV exports are stored with gzip compression.

| File | Original size | Compressed size | Decompressed SHA-256 |
| --- | ---: | ---: | --- |
| `Map1.csv.gz` | 108,596,233 bytes | 17,502,900 bytes | `F10D53602984178CC64CCF5705C632CE789E2E802EDC1EC2DDB6BB788A03A2FC` |
| `Map2.csv.gz` | 105,403,199 bytes | 16,139,142 bytes | `74DFD51FE7FED938AD999E5F96329723C43B6B6CD7FFF898E197675A8F6EBEBD` |

Decompress a file with PowerShell:

```powershell
$source = [IO.File]::OpenRead("Map1.csv.gz")
$gzip = [IO.Compression.GzipStream]::new($source, [IO.Compression.CompressionMode]::Decompress)
$target = [IO.File]::Create("Map1.csv")
$gzip.CopyTo($target)
$target.Dispose()
$gzip.Dispose()
$source.Dispose()
```

The CSV files use generic map names. Their embedded configuration records associate Map1 with `highway/006vpm` and Map2 with `highway/2006vpm`.
