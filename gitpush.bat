echo off
set year=%date:~10,4%
set month=%date:~4,2%
set day=%date:~7,2%

echo  %year%.%month%.%day%.%1
git status
pause
REM all of the files, set commit and tag values
git add .
git commit -m “%1”
git push https://github.com/charliewp/Guestbook.git master