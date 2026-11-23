param(
  [string]$ImgDir = 'E:\skills\material\aesthetics\build\_ocr\img2',
  [string]$OutDir = 'E:\skills\material\aesthetics\build\_ocr\ocr2',
  [int]$Limit = 0
)
$ErrorActionPreference = 'Stop'
try { Add-Type -AssemblyName System.Runtime.WindowsRuntime -ErrorAction SilentlyContinue } catch {}
try { [System.Reflection.Assembly]::Load('System.Runtime.WindowsRuntime, Version=4.0.0.0, Culture=neutral, PublicKeyToken=b77a5c561934e089') | Out-Null } catch {}

$null = [Windows.Media.Ocr.OcrEngine,Windows.Foundation,ContentType=WindowsRuntime]
$null = [Windows.Storage.StorageFile,Windows.Foundation,ContentType=WindowsRuntime]
$null = [Windows.Graphics.Imaging.BitmapDecoder,Windows.Foundation,ContentType=WindowsRuntime]
$null = [Windows.Globalization.Language,Windows.Foundation,ContentType=WindowsRuntime]

$lang = New-Object Windows.Globalization.Language 'zh-Hans-CN'
$engine = [Windows.Media.Ocr.OcrEngine]::TryCreateFromLanguage($lang)
if ($null -eq $engine) { throw 'OCR engine zh-Hans-CN unavailable' }

$asTaskGeneric = ([System.WindowsRuntimeSystemExtensions].GetMethods() | Where-Object {
    $_.Name -eq 'AsTask' -and $_.IsGenericMethodDefinition -and
    $_.GetParameters().Count -eq 1 -and
    $_.GetParameters()[0].ParameterType.Name -eq 'IAsyncOperation`1'
} | Select-Object -First 1)
if ($null -eq $asTaskGeneric) { throw 'AsTask generic method not found' }

function Await($WinRtTask, $ResultType) {
    $m = $asTaskGeneric.MakeGenericMethod($ResultType)
    $t = $m.Invoke($null, @($WinRtTask))
    $t.Wait(-1) | Out-Null
    return $t.Result
}

New-Item -ItemType Directory -Force -Path $OutDir | Out-Null
$files = @(Get-ChildItem -Path $ImgDir -Filter *.jpg | Sort-Object Name)
if ($Limit -gt 0) { $files = @($files | Select-Object -First $Limit) }
"ENGINE OK | files=$($files.Count)"
$ok = 0; $fail = 0
foreach ($f in $files) {
    $out = Join-Path $OutDir ($f.BaseName + '.txt')
    if (Test-Path $out) { $ok++; continue }
    try {
        $sf = Await ([Windows.Storage.StorageFile]::GetFileFromPathAsync($f.FullName)) ([Windows.Storage.StorageFile])
        $stream = Await ($sf.OpenAsync([Windows.Storage.FileAccessMode]::Read)) ([Windows.Storage.Streams.IRandomAccessStream])
        $dec = Await ([Windows.Graphics.Imaging.BitmapDecoder]::CreateAsync($stream)) ([Windows.Graphics.Imaging.BitmapDecoder])
        $bmp = Await ($dec.GetSoftwareBitmapAsync()) ([Windows.Graphics.Imaging.SoftwareBitmap])
        $res = Await ($engine.RecognizeAsync($bmp)) ([Windows.Media.Ocr.OcrResult])
        [System.IO.File]::WriteAllText($out, $res.Text, (New-Object System.Text.UTF8Encoding($false)))
        $stream.Dispose()
        if ($bmp -ne $null) { $bmp.Dispose() }
        $ok++
        if (($ok + $fail) % 25 -eq 0) { "progress $($ok+$fail)/$($files.Count) ok=$ok fail=$fail" }
    } catch {
        $fail++
        "FAIL $($f.Name) : $($_.Exception.Message)"
    }
}
"DONE ok=$ok fail=$fail"
