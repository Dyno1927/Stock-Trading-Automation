# STA — Project Setup Script
# Run this from the root of your cloned repo:
#   .\setup.ps1
# If blocked by execution policy, run first:
#   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

Write-Host "Creating STA project structure..." -ForegroundColor Cyan

# ── Folders ───────────────────────────────────────────────────────────────────
$dirs = @(
    ".github\workflows",
    "docs\adr",
    "docs\diagrams",
    "scripts",
    "src\sta\core",
    "src\sta\adapters\broker",
    "src\sta\modules\market_data",
    "src\sta\modules\strategy",
    "src\sta\modules\signal",
    "src\sta\modules\risk",
    "src\sta\modules\orders",
    "src\sta\modules\execution",
    "src\sta\modules\portfolio",
    "src\sta\modules\audit",
    "src\sta\infrastructure",
    "src\sta\api",
    "src\sta\config",
    "tests\unit",
    "tests\integration"
)

foreach ($dir in $dirs) {
    New-Item -ItemType Directory -Force -Path $dir | Out-Null
    Write-Host "  [dir]  $dir" -ForegroundColor DarkGray
}

# ── Empty Python package markers ──────────────────────────────────────────────
$inits = @(
    "src\sta\__init__.py",
    "src\sta\core\__init__.py",
    "src\sta\adapters\__init__.py",
    "src\sta\adapters\broker\__init__.py",
    "src\sta\modules\__init__.py",
    "src\sta\modules\market_data\__init__.py",
    "src\sta\modules\strategy\__init__.py",
    "src\sta\modules\signal\__init__.py",
    "src\sta\modules\risk\__init__.py",
    "src\sta\modules\orders\__init__.py",
    "src\sta\modules\execution\__init__.py",
    "src\sta\modules\portfolio\__init__.py",
    "src\sta\modules\audit\__init__.py",
    "src\sta\infrastructure\__init__.py",
    "src\sta\api\__init__.py",
    "src\sta\config\__init__.py",
    "tests\__init__.py",
    "tests\unit\__init__.py",
    "tests\integration\__init__.py"
)

foreach ($init in $inits) {
    New-Item -ItemType File -Force -Path $init | Out-Null
    Write-Host "  [py]   $init" -ForegroundColor DarkGray
}

# ── Config files (populated by the content files you download) ────────────────
$placeholders = @(
    "pyproject.toml",
    "docker-compose.yml",
    ".gitignore",
    ".env.example",
    ".github\workflows\ci.yml",
    "src\sta\core\types.py",
    "src\sta\core\events.py",
    "src\sta\adapters\broker\base.py",
    "src\sta\config\settings.py",
    "src\sta\infrastructure\logging_config.py",
    "src\sta\api\main.py",
    "README.md",
    "PROJECT.md",
    "ARCHITECTURE.md",
    "DECISIONS.md",
    "ROADMAP.md",
    "SECURITY.md"
)

foreach ($file in $placeholders) {
    if (-not (Test-Path $file)) {
        New-Item -ItemType File -Force -Path $file | Out-Null
        Write-Host "  [file] $file" -ForegroundColor DarkGray
    }
}

Write-Host ""
Write-Host "Done. Folder structure created." -ForegroundColor Green
Write-Host ""
Write-Host "Next: copy the content files from the chat into each file listed above." -ForegroundColor Yellow
Write-Host "Then run:" -ForegroundColor Yellow
Write-Host "  py -3.12 -m venv .venv" -ForegroundColor White
Write-Host "  .venv\Scripts\Activate.ps1" -ForegroundColor White
Write-Host "  pip install -e .[dev]" -ForegroundColor White
