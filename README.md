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
rm ~/.cache/matplotlib/fontlist-v330.json  
rm -rf /home/featurize/.cache/matplotlib 

cd ..  
cd ..  
sudo cp /home/ubuntu/TopicTimeline/SimHei.ttf /usr/share/fonts/  

## Git
git config --global user.email "you@example.com"  
git config --global user.name "Your Name"  

## S3 access
Create an IAM with _AmazonS3FullAccess_ strategy.  
Assign this IAM role to your EC2 instance.  