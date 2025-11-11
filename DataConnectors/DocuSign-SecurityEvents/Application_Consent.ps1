param(
    [Parameter(Mandatory=$true)]$DocuSignEnvironment,
    [Parameter(Mandatory=$true)]$IntegrationKey
)

If ($DocuSignEnvironment.ToLower() -eq "developer") {
    $jwtHost = "account-d"    
} 
Else {
    $jwtHost = "account"
   
}

$scopes = "signature%20impersonation"
$PORT = '8080'
$IP = 'localhost'
$state = [Convert]::ToString($(Get-Random -Maximum 1000000000), 16)
$authorizationEndpoint = "https://$jwtHost.docusign.com/oauth"
$redirectUri = "http://${IP}:${PORT}/authorization-code/callback"
$redirectUriEscaped = [Uri]::EscapeDataString($redirectURI)
$authorizationURL = "$authorizationEndpoint/auth?scope=$scopes&redirect_uri=$redirectUriEscaped&client_id=$IntegrationKey&state=$state&response_type=code"

Write-Output "The authorization URL is: $authorizationURL"
Write-Output ""

# Request the authorization code
# Use Http Server
$http = New-Object System.Net.HttpListener

# Hostname and port to listen on
$http.Prefixes.Add($redirectURI + "/")

# Start the Http Server
$http.Start()

if ($http.IsListening) {
    Write-Output "Open the following URL in a browser to continue:" $authorizationURL
    Start-Process $authorizationURL
}

while ($http.IsListening) {
    $context = $http.GetContext()

    if ($context.Request.HttpMethod -eq 'GET' -and $context.Request.Url.LocalPath -match '/authorization-code/callback') {
        # write-host "Check context"
        # write-host "$($context.Request.UserHostAddress)  =>  $($context.Request.Url)" -f 'mag'
        [string]$html = '
          <html lang="en">
          <head>
            <meta charset="utf-8">
            <title></title>
          </head>
          <body>
          Ok. You may close this tab and return to the shell. This window closes automatically in five seconds.
          <script type="text/javascript">
            setTimeout(
            function ( )
            {
              self.close();
            }, 5000 );
            </script>
          </body>
          </html>
          '
        # Respond to the request
        $buffer = [System.Text.Encoding]::UTF8.GetBytes($html) # Convert HTML to bytes
        $context.Response.ContentLength64 = $buffer.Length
        $context.Response.OutputStream.Write($buffer, 0, $buffer.Length) # Stream HTML to browser
        $context.Response.OutputStream.Close() # Close the response

        Start-Sleep 10
        $http.Stop()
    }
}