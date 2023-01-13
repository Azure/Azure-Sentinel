# Download and un-pack latest arm-ttk
# This is the same way the certification team automation works, from the aka.ms URL

$root="$PSScriptRoot/.."
$tmp="$root/tmp"
New-Item -Path $tmp -ItemType Directory -Force

# Download arm-ttk and unpack it
$ttkZip="$tmp/AzTemplateToolKit.zip"

# we download the latest arm-ttk, DARSy uses the same steps
# the arm-ttk is hosted on the public github here: https://github.com/Azure/arm-ttk
Invoke-WebRequest -Uri "https://aka.ms/arm-ttk-latest" -OutFile $ttkZip -Verbose
Expand-Archive -Path $ttkZip -DestinationPath $tmp -Force

# try and import the module to see it works
if(!$(Get-Command Test-AzTemplate -ErrorAction SilentlyContinue)){
    Import-Module "$tmp/arm-ttk/arm-ttk.psd1"
}