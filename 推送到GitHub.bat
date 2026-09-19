@echo off
chcp 65001 >nul
cd /d "D:\remote_jobs_crawler"
echo ============================================================
echo  准备推送项目到 GitHub: https://github.com/mathismatthew0528/remote-jobs-radar
echo ============================================================
git remote remove origin 2>nul
git remote add origin https://github.com/mathismatthew0528/remote-jobs-radar.git
echo 正在推送到 main 分支...
git push -u origin main
pause