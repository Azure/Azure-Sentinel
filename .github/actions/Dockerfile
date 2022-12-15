
FROM mcr.microsoft.com/powershell:latest

ARG SolutionName
# ARG SolutionName1
# ENV snamea ${SolutionName1}

ARG mainTemplateOrCreateUiDefinitionTemplateChanged
ENV mainTemplateOrCreateUiDefinitionTemplateChanged ${mainTemplateOrCreateUiDefinitionTemplateChanged}

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
RUN echo "mainCreateUIExist ${mainTemplateOrCreateUiDefinitionTemplateChanged}"

RUN echo "isDataConnectorFolderNameWithSpace ${isDataConnectorFolderNameWithSpace}"
RUN echo "dataConnectorFileNames ${dataConnectorFileNames}"
RUN echo "hasDataConnectorFileChanged ${hasDataConnectorFileChanged}"

LABEL version="v1.0"
RUN ls ./

WORKDIR ./Solutions/$SolutionName

COPY ./Solutions/$SolutionName dist
COPY ./.github/actions/entrypoint1.ps1 dist
RUN ls dist/*

LABEL "com.github.actions.name"="ARM TTK"
LABEL "com.github.actions.description"="Checks template with the ARM TTK"

LABEL version="0.0.1"
LABEL maintainer="Amol" 

# Install Git
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y git

# Clone ARM-TTK Repo
RUN git clone https://github.com/Azure/arm-ttk.git /dist/armttk
RUN ls /dist/armttk/
RUN ls /dist


SHELL ["pwsh"]
RUN .\dist\entrypoint.ps1

