param([string]$Archive=(Join-Path $PSScriptRoot 'Catalase_Open_Lab_v1.1.zip'),[string]$SshTarget='')
$ErrorActionPreference='Stop'
function Run-Git { & git @args; if($LASTEXITCODE -ne 0){throw "Git failed (exit $LASTEXITCODE)"} }
$expected='e2e0173c913f814d196a4c622f1ff1c8f0f8d471bb3c295bd0817e76537de84f'
if(!(Test-Path -LiteralPath $Archive -PathType Leaf)){throw "Original ZIP not found: $Archive"}
$Archive=(Resolve-Path -LiteralPath $Archive).Path
if((Get-FileHash -LiteralPath $Archive -Algorithm SHA256).Hash.ToLowerInvariant() -ne $expected){throw 'Archive checksum mismatch. No changes made.'}
Get-Command git -ErrorAction Stop | Out-Null
$tmp=Join-Path ([System.IO.Path]::GetTempPath()) ('atlas-openlab-'+[guid]::NewGuid().ToString('N'))
try {
  Run-Git clone --depth 1 --single-branch --branch atlas-web-preview https://github.com/RandoSY/project-atlas.git $tmp
  $rel='web/atlas/catalase-fem/downloads/v1.1/Catalase_Open_Lab_v1.1.zip'
  $dst=Join-Path $tmp $rel
  if(Test-Path -LiteralPath $dst){
    if((Get-FileHash -LiteralPath $dst -Algorithm SHA256).Hash.ToLowerInvariant() -ne $expected){throw 'Existing release has different bytes; refusing overwrite.'}
    Write-Host 'Exact ZIP already present on GitHub.'
  } else {
    Copy-Item -LiteralPath $Archive -Destination $dst
    Run-Git -C $tmp add -- $rel
    Run-Git -C $tmp commit -m 'Publish exact verified Catalase Open Lab v1.1 archive'
    Run-Git -C $tmp push origin HEAD:atlas-web-preview
    Write-Host 'Exact archive pushed successfully.'
  }
  if($SshTarget){
    $remote='curl -fsSL https://raw.githubusercontent.com/RandoSY/project-atlas/7d635a135c10d3ef25d893c09b62512cedaaad54/web/deploy-catalase-open-lab.sh -o /tmp/deploy-catalase-open-lab.sh && sudo bash /tmp/deploy-catalase-open-lab.sh'
    & ssh -t $SshTarget $remote
    if($LASTEXITCODE -ne 0){throw 'Server deployment did not complete. GitHub archive is preserved.'}
  } else {
    Write-Host 'GitHub step complete. Run the server deployment command in README or supply -SshTarget user@host.'
  }
} finally {
  if(Test-Path -LiteralPath $tmp){Remove-Item -LiteralPath $tmp -Recurse -Force}
}
