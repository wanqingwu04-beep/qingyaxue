param(
    [string]$Repo = "qingyaxue",
    [string]$Branch = "main"
)

# 青崖雪一键发布脚本：打包 epub → 生成静态站点 → 推送到 GitHub
# 首次运行时请先设置远程仓库：git remote add origin https://github.com/<账号>/<仓库>.git
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$py = "C:\Users\28120\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
if (-not (Test-Path $py)) { $py = "python" }
$git = "C:\Users\28120\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\git\cmd\git.exe"
if (-not (Test-Path $git)) { $git = "git" }

Set-Location $root

& $py -X utf8 build_epub.py
& $py -X utf8 build_site.py

if (-not (Test-Path "$root\.git")) {
    & $git init -b $Branch
}

& $git add -A
& $git -c user.name="wanqingwu04-beep" -c user.email="wanqingwu04-beep@users.noreply.github.com" commit -m "更新青崖雪"

$remote = & $git remote get-url origin 2>$null
if (-not $remote) {
    Write-Host ""
    Write-Host "还没有配置远程仓库。请先运行："
    Write-Host "  git remote add origin https://github.com/<你的账号>/$Repo.git"
    Write-Host "然后重新运行本脚本。"
    exit 1
}

& $git push -u origin $Branch

Write-Host ""
Write-Host "发布完成！"
Write-Host "GitHub Pages 设置：Settings → Pages → Source 选择 main 分支 /docs 目录"
Write-Host "手机访问：https://<你的账号>.github.io/$Repo/"
