cd C:\Users\ibgut\Documents\N.I.N.A\GIT_NinaNightly

python embed_video.py

git add .
git commit -m "Automated nightly summary update"
git pull origin main --rebase
git push origin main

pause