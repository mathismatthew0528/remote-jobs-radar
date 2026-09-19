@echo off
cd /d "D:\remote_jobs_crawler"
git remote remove origin >nul 2>&1
git remote add origin https://github.com/mathismatthew0528/remote-jobs-radar.git
echo ============================================================
echo  Pushing to GitHub: https://github.com/mathismatthew0528/remote-jobs-radar
echo ============================================================
git push -u origin main
echo ============================================================
pause