if [ "$EUID" -ne 0 ]
  then echo "Please run as root"
  exit
fi


# Grab basic python deps
apt-get update
apt-get install -y python-dev git python-pip dtach

# Install SSL lib to remove pip warnings
apt-get install -y libffi-dev libssl-dev

# Install docker PGP key
apt-key adv --keyserver hkp://p80.pool.sks-keyservers.net:80 --recv-keys 58118E89F3A912897C070ADBF76221572C52609D
echo 'deb https://apt.dockerproject.org/repo ubuntu-trusty main' | sudo tee -a /etc/apt/sources.list

# Install docker
apt-get update
apt-get install -y docker-engine
usermod -a -G docker ubuntu

shutdown 0
