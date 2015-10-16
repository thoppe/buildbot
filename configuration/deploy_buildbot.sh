
if [ ! -d "buildbot" ]; then
    git clone "https://github.com/tulsa/buildbot.git"
fi

sudo -H pip -q install pip -U
cd buildbot
sudo -H pip -q install -r requirements.txt
