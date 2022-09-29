FROM ubuntu 
LABEL version="v1.0"
ENV builddir='Solutions'
RUN mkdir \${builddir}
RUN apt-get update
RUN apt-get install -y wget apt-transport-https software-properties-common
RUN wget -q https://packages.microsoft.com/config/ubuntu/20.04/packages-microsoft-prod.deb
RUN dpkg -i packages-microsoft-prod.deb
RUN apt-get update
RUN add-apt-repository universe
RUN apt-get install -y powershell

LABEL "com.github.actions.name"="ARM TTK"
LABEL "com.github.actions.description"="Checks template with the ARM TTK"

LABEL version="0.0.1"
LABEL maintainer="Wesley Haakman" 

# Install Git
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y git

# Clone ARM-TTK Repo
RUN git clone https://github.com/Azure/arm-ttk.git
RUN git clone https://github.com/whaakman/armttk-github-action-demo.git /temp

#exec(ls "/home/runner/work/packagingrepo/packagingrepo/Solutions/Alibaba Cloud/Package/." > /dev/null 2>&1 && echo 0 || echo 1)
# Copy the Entrypoint file from the current directory (the one the Dockerfile is located in)
COPY entrypoint.ps1 /entrypoint.ps1
RUN echo "hello there"
RUN ls -la /home/runner/work/packagingrepo/packagingrepo/*
#docker cp "/home/runner/work/packagingrepo/packagingrepo/Solutions/Alibaba Cloud/Package/." container_id:/${builddir}
#COPY ${} /mainTemplate.json

# Start using the Entrypoint file.
ENTRYPOINT [ "pwsh", "/entrypoint.ps1" ]