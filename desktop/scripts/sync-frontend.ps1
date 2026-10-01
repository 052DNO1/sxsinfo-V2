<#
.SYNOPSIS
    把前端源码（或从原 frontend 目录更新）同步到桌面端自己的前端目录。

.DESCRIPTION
    桌面端工程使用自己的一份前端源码：desktop/frontend/
    这样可以直接在桌面端里改前端代码、直接构建，不需要回到原 frontend 目录。

    代价是前端会有两份代码。为了抑制「两份代码越走越远」，
    这个脚本提供从原 frontend 拉取更新的能力：

      默认模式  ：新增 + 覆盖，不动 desktop/frontend 里独有的文件
                  （适合把前端的新修复拉过来，同时保住桌面端自己的改动）
      -Mirror   ：完全镜像，会删掉 desktop/frontend 里多出来的文件
                  （适合桌面端前端被改乱、想回到与原前端一致的状态）

.PARAMETER Source
    来源前端源码目录，通常为 <仓库>/frontend

.PARAMETER Target
    桌面端前端目录，默认为本脚本上一级的 frontend/

.PARAMETER Mirror
    完全镜像模式，会删除目标目录中多余的文件（危险，会丢失桌面端独有改动）

.EXAMPLE
    .\sync-frontend.ps1 -Source ..\..\frontend

.EXAMPLE
    .\sync-frontend.ps1 -Source D:\project\sxsinfo-v2\frontend -Mirror
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$Source,

    [string]$Target,

    [switch]$Mirror
)

$ErrorActionPreference = 'Stop'

if (-not $Target) {
    $Target = Join-Path (Split-Path -Parent $PSScriptRoot) 'frontend'
}

if (-not (Test-Path -LiteralPath $Source -PathType Container)) {
    throw "源目录不存在：$Source"
}

$Source = (Resolve-Path -LiteralPath $Source).Path
$Target = [System.IO.Path]::GetFullPath($Target)

if ($Source -eq $Target) {
    throw '源目录与目标目录相同，已中止。'
}

# 确认源目录确实是前端工程
foreach ($required in @('package.json', 'vite.config.pc.js')) {
    if (-not (Test-Path -LiteralPath (Join-Path $Source $required) -PathType Leaf)) {
        throw "源目录里没有 $required，看起来不是前端工程目录：$Source"
    }
}

Write-Host "源目录  : $Source"
Write-Host "目标目录: $Target"
Write-Host "模式    : $(if ($Mirror) { '完全镜像（会删除多余文件）' } else { '增量同步（保留目标独有文件）' })"
Write-Host ''

if (-not (Test-Path -LiteralPath $Target -PathType Container)) {
    New-Item -ItemType Directory -Path $Target -Force | Out-Null
}

# /E 含子目录(含空目录) /NFL /NDL /NJH /NJS /NP 精简输出
# /XD 排除 node_modules 与 dist：依赖重装、产物本地构建，都不该被复制
#
# 【桌面端独有文件必须排除】以下文件是"桌面外壳"专用的，原 frontend/ 里没有对应版本，
# 一旦被覆盖，自绘标题栏/无边框窗口就会退回系统标题栏：
#   src/App.vue          —— 挂载 TitleBar、包一层 lims-shell 布局
#   src/main.js          —— 引入 desktop-shell.css、跟随系统暗色、启动占位淡出
#   index.pc.html        —— 启动占位移出 #app（否则 mount 会把它清掉造成白闪）
#   assets/css/desktop-shell.css、components/desktop/（TitleBar.vue）
$roboArgs = @(
    $Source, $Target,
    '/E', '/NFL', '/NDL', '/NJH', '/NJS', '/NP',
    '/XD', 'node_modules', 'dist',
    '/XF', 'App.vue', 'main.js', 'index.pc.html', 'desktop-shell.css',
    '/XD', 'desktop'
)
if ($Mirror) { $roboArgs += '/PURGE' }

robocopy @roboArgs | Out-Null
$code = $LASTEXITCODE

# robocopy 退出码 0-7 为成功，8 及以上为失败
if ($code -ge 8) {
    throw "robocopy 同步失败，退出码 $code"
}

$files = Get-ChildItem -LiteralPath $Target -Recurse -File
$totalMb = [math]::Round((($files | Measure-Object -Property Length -Sum).Sum / 1MB), 2)

Write-Host "同步完成：$($files.Count) 个文件，共 $totalMb MB" -ForegroundColor Green
Write-Host ''
Write-Host '下一步（首次需要装依赖）：' -ForegroundColor Cyan
Write-Host "    cd `"$Target`""
Write-Host '    yarn install    # 必须用 yarn：本工程只有 yarn.lock，npm 会重新解析依赖版本'
