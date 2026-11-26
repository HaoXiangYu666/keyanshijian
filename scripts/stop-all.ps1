<#
  本草心智 · 停止全部
  只停本项目相关进程（按 jar 名 / 端口 / Neo4j 主类匹配），不碰系统里其它 java、node。
  PostgreSQL 保留不关：数据在 D:\pgdata，常驻下次启动更快。
#>

$OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

function Stop-Port([int]$Port, [string]$Name) {
    $conns = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
    foreach ($c in $conns) {
        if ($c.OwningProcess -and $c.OwningProcess -ne 0) {
            Stop-Process -Id $c.OwningProcess -Force -ErrorAction SilentlyContinue
            Write-Host "[停止] $Name ($Port)"
        }
    }
}

Write-Host ''
Write-Host '正在停止本草心智的服务...'
Write-Host ''

# 1) 八个 Java 服务：按命令行里的 jar 名匹配，避免误杀别人的 java
$names = @('svc-identity', 'svc-catalog', 'svc-search', 'svc-training',
           'svc-graph', 'svc-insight', 'herbmind-bff', 'herbmind-gateway')
$procs = Get-CimInstance Win32_Process -Filter "Name = 'java.exe'" -ErrorAction SilentlyContinue
foreach ($p in $procs) {
    foreach ($n in $names) {
        if ($p.CommandLine -like "*$n-2.0.0-SNAPSHOT.jar*") {
            Stop-Process -Id $p.ProcessId -Force -ErrorAction SilentlyContinue
            Write-Host "[停止] $n"
            break
        }
    }
}

# 2) Neo4j：认主类，不认端口（它可能还没起来）
foreach ($p in $procs) {
    if ($p.CommandLine -like '*CommunityEntryPoint*') {
        Stop-Process -Id $p.ProcessId -Force -ErrorAction SilentlyContinue
        Write-Host '[停止] Neo4j'
        break
    }
}

# 3) Agent 与前端：按监听端口停
Stop-Port 8091 'Agent'
Stop-Port 5173 '前端'

Write-Host ''
Write-Host '完成。PostgreSQL(5432) 未停止 —— 数据库常驻即可，需要停请手动操作。'
Write-Host ''
Read-Host '按回车关闭'
