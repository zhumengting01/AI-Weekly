#!/usr/bin/env pwsh
<#
.SYNOPSIS
    设置 AI Weekly 周刊自动生成的 Windows 定时任务

.DESCRIPTION
    创建一个 Windows 计划任务，每周一上午 7:00 自动执行周刊生成脚本

.USAGE
    .\scripts\setup-cron.ps1
    .\scripts\setup-cron.ps1 -Uninstall   # 移除定时任务
#>

param(
    [switch]$Uninstall
)

$TaskName = "AI-Weekly-AutoGenerate"
$ProjectRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$PythonScript = Join-Path $ProjectRoot "scripts\generate_weekly.py"
$LogFile = Join-Path $ProjectRoot "scripts\weekly-cron.log"

# 查找 Python 路径
$PythonPath = (Get-Command python -ErrorAction SilentlyContinue).Source
if (-not $PythonPath) {
    $PythonPath = (Get-Command python3 -ErrorAction SilentlyContinue).Source
}
if (-not $PythonPath) {
    Write-Error "未找到 Python，请确保已安装并加入 PATH"
    exit 1
}

if ($Uninstall) {
    Write-Host "正在移除定时任务: $TaskName"
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false -ErrorAction SilentlyContinue
    Write-Host "定时任务已移除"
    exit 0
}

# 检查是否已存在
$existing = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
if ($existing) {
    Write-Host "定时任务已存在，正在更新..."
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
}

# 构建执行脚本内容
# 使用单引号 here-string 避免变量展开，再用 -replace 替换占位符
$ScriptContent = @'
# AI Weekly 自动生成 - {{DATE}}
Set-Location "{{PROJECT_ROOT}}"

# 加载环境变量
if (Test-Path "{{PROJECT_ROOT}}\scripts\.env") {
    Get-Content "{{PROJECT_ROOT}}\scripts\.env" | ForEach-Object {
        if ($_ -match '^\s*([^#][^=]+)=(.*)$') {
            [System.Environment]::SetEnvironmentVariable($matches[1], $matches[2], 'Process')
        }
    }
}

# 生成周刊
Write-Host "[$((Get-Date).ToString('yyyy-MM-dd HH:mm:ss'))] 开始生成周刊..."
& "{{PYTHON_PATH}}" "{{PYTHON_SCRIPT}}" 2>&1 | Tee-Object -FilePath "{{LOG_FILE}}" -Append

Write-Host "[$((Get-Date).ToString('yyyy-MM-dd HH:mm:ss'))] 周刊生成完成"
'@

$ScriptContent = $ScriptContent -replace '\{\{DATE\}\}', (Get-Date -Format 'yyyy-MM-dd')
$ScriptContent = $ScriptContent -replace '\{\{PROJECT_ROOT\}\}', $ProjectRoot
$ScriptContent = $ScriptContent -replace '\{\{PYTHON_PATH\}\}', $PythonPath
$ScriptContent = $ScriptContent -replace '\{\{PYTHON_SCRIPT\}\}', $PythonScript
$ScriptContent = $ScriptContent -replace '\{\{LOG_FILE\}\}', $LogFile

$ScriptPath = Join-Path $ProjectRoot "scripts\run-weekly.ps1"
$ScriptContent | Out-File -FilePath $ScriptPath -Encoding UTF8
# 移除 UTF-8 BOM，避免 PowerShell 5 解析中文出错
$bytes = [System.IO.File]::ReadAllBytes($ScriptPath)
if ($bytes.Length -ge 3 -and $bytes[0] -eq 0xEF -and $bytes[1] -eq 0xBB -and $bytes[2] -eq 0xBF) {
    [System.IO.File]::WriteAllBytes($ScriptPath, $bytes[3..($bytes.Length - 1)])
}

# 创建计划任务
$Action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$ScriptPath`""
$Trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Monday -At 7:00AM
$Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -RestartCount 3 -RestartInterval (New-TimeSpan -Minutes 5)

Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger -Settings $Settings -Description "每周一上午7:00自动生成AI Weekly周刊" -Force

Write-Host ""
Write-Host "=== 定时任务设置完成 ==="
Write-Host "任务名称: $TaskName"
Write-Host "执行时间: 每周一 07:00"
Write-Host "执行脚本: $ScriptPath"
Write-Host "日志文件: $LogFile"
Write-Host ""
Write-Host "管理命令:"
Write-Host "  查看任务: Get-ScheduledTask -TaskName '$TaskName'"
Write-Host "  手动运行: Start-ScheduledTask -TaskName '$TaskName'"
Write-Host "  移除任务: .\scripts\setup-cron.ps1 -Uninstall"
