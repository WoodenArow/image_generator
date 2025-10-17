param(
  [string]$Script = "image_generator.py",
  [string]$Name = "image_generator",
  [string]$AddData = "template.jpg;."
)

function Fail($msg) { Write-Error $msg; exit 1 }

$python = (Get-Command python -ErrorAction SilentlyContinue)
if (-not $python) { Fail "Python не найден в PATH. Установите Python и повторите." }

Write-Host "Ensuring pyinstaller..."
python -m pip install --upgrade pyinstaller
if (-not $?) { Fail "Не удалось установить pyinstaller" }

if (Test-Path build) { Remove-Item build -Recurse -Force }
if (Test-Path dist) { Remove-Item dist -Recurse -Force }
if (Test-Path "$Name.exe") { Remove-Item "$Name.exe" -Force }

Write-Host "Building..."
python -m PyInstaller --clean --noconfirm --log-level=INFO --noconsole --name $Name --onefile --add-data $AddData $Script
if (-not $?) { Fail "PyInstaller завершился с ошибкой" }

$exe1 = Join-Path dist "$Name\$Name.exe"
$exe2 = Join-Path dist "$Name.exe"
$built = $null
if (Test-Path $exe1) { $built = $exe1 }
if (-not $built -and (Test-Path $exe2)) { $built = $exe2 }
if (-not $built) { Fail "Сборка завершилась без артефакта .exe. Проверьте вывод PyInstaller." }
Move-Item -Force $built "$Name.exe"
Write-Host "Built $Name.exe"

