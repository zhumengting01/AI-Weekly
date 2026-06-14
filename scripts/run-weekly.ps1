# AI Weekly 自动生成
Set-Location "D:\ai-weekly\astro-brook"

# 加载环境变量
if (Test-Path "D:\ai-weekly\astro-brook\scripts\.env") {
    Get-Content "D:\ai-weekly\astro-brook\scripts\.env" | ForEach-Object {
        if ($_ -match '^\s*([^#][^=]+)=(.*)$') {
            [System.Environment]::SetEnvironmentVariable($matches[1], $matches[2], 'Process')
        }
    }
}

# 生成周刊
Write-Host "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] 开始生成周刊..."
& "D:\Program Files\Python\python.exe" "D:\ai-weekly\astro-brook\scripts\generate_weekly.py" 2>&1 | Tee-Object -FilePath "D:\ai-weekly\astro-brook\scripts\weekly-cron.log" -Append

Write-Host "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] 周刊生成完成"
