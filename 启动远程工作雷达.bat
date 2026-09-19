@echo off
chcp 65001 >nul
cd /d "D:\remote_jobs_crawler"
echo ============================================================
echo Starting Remote AI Jobs Radar...
echo ============================================================
python "D:\remote_jobs_crawler\main.py" --daemon
pause