# Installation
## Install the dotnet SDK
```
https://dotnet.microsoft.com/download
```

## Build source code
```
dotnet build .\UploadToLogAnalytics.csproj
```
```
bin\Debug\netcoreapp3.1\UploadToLogAnalytics.exe 
```

# Run
```
bin\Debug\netcoreapp3.1\UploadToLogAnalytics.exe [WORKSPACEID] [WORKSPACEID] [TABLENAME] [JSONFILE]
```
Depending on your data size, this may take some time