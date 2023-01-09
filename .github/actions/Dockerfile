
FROM mcr.microsoft.com/powershell:latest

ARG SolutionName

ARG mainTemplateChanged
ENV mainTemplateChanged ${mainTemplateChanged}

ARG createUiChanged
ENV createUiChanged ${createUiChanged}

ARG hasPlaybooksChanged
ENV playbooksChanged ${hasPlaybooksChanged}

ARG playbookFilesList
ENV playbookFilesList ${playbookFilesList}

ARG isDataConnectorFolderNameWithSpace
ENV isDataConnectorFolderNameWithSpace ${isDataConnectorFolderNameWithSpace}

ARG dataConnectorFileNames
ENV dataConnectorFileNames ${dataConnectorFileNames}

ARG hasDataConnectorFileChanged
ENV hasDataConnectorFileChanged ${hasDataConnectorFileChanged}

ENV sname ${SolutionName}
ENV sname1 $SolutionName
RUN echo "playbooksChanged ${playbooksChanged}"
RUN echo "mainTemplateChanged ${mainTemplateChanged}"
RUN echo "createUiChanged ${createUiChanged}"

RUN echo "isDataConnectorFolderNameWithSpace ${isDataConnectorFolderNameWithSpace}"
RUN echo "dataConnectorFileNames ${dataConnectorFileNames}"
RUN echo "hasDataConnectorFileChanged ${hasDataConnectorFileChanged}"

LABEL version="v1.0"

WORKDIR ./Solutions/$SolutionName

COPY ./Solutions/$SolutionName dist
COPY ./.github/actions/entrypoint.ps1 dist

LABEL "com.github.actions.name"="ARM TTK"
LABEL "com.github.actions.description"="Checks template with the ARM TTK"

LABEL version="0.0.1"
LABEL maintainer="Microsoft" 

# Install Git
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y git

# Clone ARM-TTK Repo
RUN git clone https://github.com/Azure/arm-ttk.git /dist/armttk

SHELL ["pwsh"]
RUN .\dist\entrypoint.ps1

