# Hot Topic timeline generator

## link EC2 with VScode
C:/Users/username/.ssh/ <-- save your-ec2-key.pem

C:/Users/username/.ssh/config :
Host aws-ec2
    HostName <your-ec2-ip-address>
    User ubuntu
    IdentityFile ~/.ssh/your-ec2-key.pem

## config your aws-ec2
sudo apt-get update
sudo apt-get install sysbench
sudo apt install python3-pip

## config your project in linux
cd TopicTimeline
pip3 install -r requirements.txt

## install font
sudo apt-get install -y fonts-dejavu
sudo apt-get install -y ttf-mscorefonts-installer
sudo fc-cache -f -v

## Git
git config --global user.email "you@example.com"
git config --global user.name "Your Name"
