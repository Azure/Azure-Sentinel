cd /home/devuser
DOCKER_LINK=$1
SEEK_TIMESTAMP=$9
DATA_DIR="/home/devuser/docker_persistent_volume"
mkdir /home/devuser/docker_persistent_volume
mkdir /home/devuser/docker_persistent_volume/sentinel
echo "Hostname=$2" > "$DATA_DIR/netskope_config.env"
echo "Token=$3" >> "$DATA_DIR/netskope_config.env"
echo "WorkspaceKey=$4" >> "$DATA_DIR/sentinel_config.env"
echo "WorkspaceId=$5" >> "$DATA_DIR/sentinel_config.env"
echo "BackoffRetryCount=$6" > "$DATA_DIR/general_config.env"
echo "BackoffSleepTime=$7" >> "$DATA_DIR/general_config.env"
echo "IdleTimeout=$8" >> "$DATA_DIR/general_config.env"
echo "SeekTimestamp=$SEEK_TIMESTAMP" >> "$DATA_DIR/seek_timestamp.env"
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo docker pull $DOCKER_LINK
sudo docker run -d -v $(pwd)/docker_persistent_volume:/app $DOCKER_LINK