# If the repo hasn't been cloned, do so now
if [ ! -d "buildbot" ]; then
    git clone "https://github.com/tulsa/buildbot.git"
fi

# Upgrade pip
sudo -H pip -q install pip -U

# Install the requirements
cd buildbot
sudo -H pip -q install -r requirements.txt

# Start a test instance (this downloads the docker images needed)
fab start

# Stop the test image
fab stop
