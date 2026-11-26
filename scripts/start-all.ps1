<#
  本草心智 · 一键启动（Windows 本机版）

  由 启动全部.bat 调用，也可以右键「使用 PowerShell 运行」。
  按需启动：PostgreSQL → Neo4j → 8 个 Java 服务 → Python Agent → 前端。
  已在监听端口的会跳过，重复运行不会起两份。

  换机器只需要改下面「路径配置」四行。
#>

$ErrorActionPreference = 'Continue'
$OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

# ---------------- 路径配置 ----------------
$JavaHome = 'D:\tools\jdk17'
$PgData   = 'D:\pgdata'
$PgExe    = 'D:\tools\pg17\bin\postgres.exe'
$Neo4jDir = 'D:\tools\neo4j\neo4j-community-5.26.0'
$Python   = 'D:\tools\venvs\herbmind\Scripts\python.exe'
# ----------------------------------------

$Java  = Join-Path $JavaHome 'bin\java.exe'
$Root  = Split-Path -Parent $PSScriptRoot
$LogDir = Join-Path $Root 'logs'
if (-not (Test-Path $LogDir)) { New-Item -ItemType Directory -Path $LogDir | Out-Null }
$env:npm_config_cache = 'D:\npm-cache'

# PowerShell 5.1 的 Start-Process：环境里同时存在 HTTP_PROXY 与 http_proxy 时，
# 内部字典会因大小写重复而报「已添加项」直接失败。统一成一份大写即可。
foreach ($name in 'HTTP_PROXY', 'HTTPS_PROXY', 'ALL_PROXY', 'NO_PROXY') {
    $val = [Environment]::GetEnvironmentVariable($name)
    [Environment]::SetEnvironmentVariable($name.ToLower(), $null)
    [Environment]::SetEnvironmentVariable($name, $null)
    if ($val) { [Environment]::SetEnvironmentVariable($name, $val) }
}

function Test-Port([int]$Port) {
    try { $null = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction Stop; return $true }
    catch { return $false }
}

function Wait-Port([int]$Port, [int]$Seconds) {
    for ($i = 0; $i -lt $Seconds; $i++) {
        if (Test-Port $Port) { return $true }
        Start-Sleep -Milliseconds 1000
    }
    return $false
}

function Write-Step($Text) { Write-Host $Text }

Write-Host ''
Write-Host '============================================' -ForegroundColor Cyan
Write-Host '  本草心智 · 正在启动' -ForegroundColor Cyan
Write-Host '============================================' -ForegroundColor Cyan

if (-not (Test-Path $Java)) {
    Write-Host "[错误] 找不到 Java：$Java" -ForegroundColor Red
    Write-Host '       请修改 scripts\start-all.ps1 顶部的路径配置。' -ForegroundColor Red
    Read-Host '按回车退出'
    exit 1
}

# ---------- 1. PostgreSQL ----------
if (Test-Port 5432) {
    Write-Step '[跳过] PostgreSQL 5432 已在运行'
} else {
    Write-Step '[启动] PostgreSQL ...'
    $pidFile = Join-Path $PgData 'postmaster.pid'
    if (Test-Path $pidFile) { Remove-Item $pidFile -Force -ErrorAction SilentlyContinue }
    Start-Process -FilePath $PgExe -ArgumentList @('-D', $PgData) -WindowStyle Minimized `
        -RedirectStandardOutput (Join-Path $LogDir 'pg.out.log') `
        -RedirectStandardError  (Join-Path $LogDir 'pg.err.log')
}

# ---------- 2. Neo4j ----------
if (Test-Port 7474) {
    Write-Step '[跳过] Neo4j 7474 已在运行'
} else {
    Write-Step '[启动] Neo4j ...'
    $neoArgs = @(
        '-cp', 'lib/*',
        "-Dbasedir=$Neo4jDir",
        'org.neo4j.server.CommunityEntryPoint',
        "--home-dir=$Neo4jDir",
        "--config-dir=$Neo4jDir\conf"
    )
    Start-Process -FilePath $Java -ArgumentList $neoArgs -WorkingDirectory $Neo4jDir -WindowStyle Minimized `
        -RedirectStandardOutput (Join-Path $LogDir 'neo4j.out.log') `
        -RedirectStandardError  (Join-Path $LogDir 'neo4j.err.log')
}

# 数据库没起来的话，Java 服务会连不上库直接退出，所以先等
Write-Step ''
Write-Step '[等待] 数据库就绪（最多 40 秒）'
if (Wait-Port 5432 40) { Write-Step '[完成] PostgreSQL 已就绪' }
else { Write-Host '[警告] PostgreSQL 40 秒内没起来，先继续；服务可能连不上库' -ForegroundColor Yellow }

# ---------- 3. 八个 Java 服务 ----------
$Services = @(
    @{ Name = 'svc-identity';  Port = 8081 },
    @{ Name = 'svc-catalog';   Port = 8082 },
    @{ Name = 'svc-search';    Port = 8083 },
    @{ Name = 'svc-training';  Port = 8084 },
    @{ Name = 'svc-graph';     Port = 8085 },
    @{ Name = 'svc-insight';   Port = 8086 },
    @{ Name = 'herbmind-bff';  Port = 8090 },
    @{ Name = 'herbmind-gateway'; Port = 8080 }
)

foreach ($s in $Services) {
    if (Test-Port $s.Port) {
        Write-Step "[跳过] $($s.Name) :$($s.Port) 已在运行"
        continue
    }
    $jar = Join-Path $Root "backend\$($s.Name)\target\$($s.Name)-2.0.0-SNAPSHOT.jar"
    if (-not (Test-Path $jar)) {
        Write-Host "[缺失] $jar 不存在，需先在 backend 里 mvn package" -ForegroundColor Red
        continue
    }
    Write-Step "[启动] $($s.Name) :$($s.Port)"
    Start-Process -FilePath $Java -ArgumentList @('-jar', $jar, "--server.port=$($s.Port)") -WindowStyle Minimized `
        -RedirectStandardOutput (Join-Path $LogDir "$($s.Name).log") `
        -RedirectStandardError  (Join-Path $LogDir "$($s.Name).err.log")
}

# ---------- 4. Python Agent ----------
if (Test-Port 8091) {
    Write-Step '[跳过] Agent 8091 已在运行'
} elseif (Test-Path $Python) {
    Write-Step '[启动] Agent 8091'
    Start-Process -FilePath $Python -ArgumentList @('run.py', '--host', '0.0.0.0', '--port', '8091') `
        -WorkingDirectory (Join-Path $Root 'agent') -WindowStyle Minimized `
        -RedirectStandardOutput (Join-Path $LogDir 'agent.log') `
        -RedirectStandardError  (Join-Path $LogDir 'agent.err.log')
} else {
    Write-Host "[缺失] 找不到 Python 环境：$Python" -ForegroundColor Red
}

# ---------- 5. 前端 ----------
if (Test-Port 5173) {
    Write-Step '[跳过] 前端 5173 已在运行'
} else {
    Write-Step '[启动] 前端 5173'
    Start-Process -FilePath 'cmd.exe' -ArgumentList @('/c', 'npm run dev') `
        -WorkingDirectory (Join-Path $Root 'frontend') -WindowStyle Minimized `
        -RedirectStandardOutput (Join-Path $LogDir 'frontend.log') `
        -RedirectStandardError  (Join-Path $LogDir 'frontend.err.log')
}

# ---------- 6. 等网关 ----------
Write-Step ''
Write-Step '[等待] 网关 8080 就绪（最多 90 秒）'
if (Wait-Port 8080 90) {
    Write-Step '[完成] 网关已就绪'
} else {
    Write-Host '[警告] 网关 90 秒内没起来，看 logs\herbmind-gateway.err.log' -ForegroundColor Yellow
}

# ---------- 输出地址 ----------
$lanIp = (Get-NetIPAddress -AddressFamily IPv4 -ErrorAction SilentlyContinue |
          Where-Object { $_.IPAddress -notlike '127.*' -and $_.IPAddress -notlike '169.254.*' } |
          Select-Object -First 1).IPAddress

Write-Host ''
Write-Host '============================================' -ForegroundColor Green
Write-Host '  启动完成' -ForegroundColor Green
Write-Host '============================================' -ForegroundColor Green
Write-Host "  电脑打开： http://localhost:5173/"
if ($lanIp) { Write-Host "  手机打开： http://$lanIp`:5173/   （需同一个 WiFi）" }
Write-Host '  账号 demo  密码 demo123456'
Write-Host ''
Write-Host "  日志目录： $LogDir"
Write-Host '  停止全部： 双击 停止全部.bat'
Write-Host '============================================' -ForegroundColor Green
Write-Host ''
Write-Host '服务在最小化的窗口里跑，这个窗口可以直接关掉。'
Write-Host ''
Read-Host '按回车关闭'
