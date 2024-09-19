#!/bin/bash

# Update and install dependencies
sudo apt-get update
sudo apt-get install -y git python3 python3-venv python3-dev libssl-dev libffi-dev build-essential

#Backup the current SSH configuration file
sudo cp /etc/ssh/sshd_config /etc/ssh/sshd_config.bak
#Change the SSH port to 22222
sudo sed -i 's/^#Port 22/Port 22222/' /etc/ssh/sshd_config
#Restart the SSH service to apply changes
sudo systemctl restart ssh.service
echo "SSH port changed to 22222 and SSH service restarted."

# Create a cowrie user without a password
sudo useradd -m -s /bin/bash -c "Cowrie" -p "" cowrie

# Switch to the cowrie user and set up the environment
sudo -u cowrie bash << EOF
cd /home/cowrie
git clone https://github.com/cowrie/cowrie.git
cd cowrie
python3 -m venv cowrie-env
source cowrie-env/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
cp etc/cowrie.cfg.dist etc/cowrie.cfg
cp etc/userdb.example etc/userdb.txt
bin/cowrie start
EOF

# Create the systemd service file for cowrie
#cat <<EOF | sudo tee /etc/systemd/system/cowrie.service
#[Unit]
#Description=Cowrie Service
#After=network.target

#[Service]
#Type=simple
#User=cowrie
#ExecStart=/home/cowrie/cowrie/cowrie-env/bin/python /home/cowrie/cowrie/bin/cowrie start
#Restart=on-failure

#[Install]
#WantedBy=multi-user.target
#EOF

# Reload systemd to recognize the new service
#sudo systemctl daemon-reload

# Enable the service to start on boot
#sudo systemctl enable cowrie.service

# Start the service
#sudo systemctl start cowrie.service



# Update iptables to redirect port 22 to 2222 and 23 to 2223
sudo iptables -t nat -A PREROUTING -p tcp --dport 22 -j REDIRECT --to-port 2222
sudo iptables -t nat -A PREROUTING -p tcp --dport 23 -j REDIRECT --to-port 2223

# Exit the script
exit 0

# Check the status of the service
#sudo systemctl status cowrie.service
