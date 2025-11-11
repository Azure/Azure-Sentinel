Add-Type -AssemblyName System.Windows.Forms

# Create an OpenFileDialog
$openFileDialog = New-Object System.Windows.Forms.OpenFileDialog
$openFileDialog.Filter = "PEM files (*.pem)|*.pem"
$openFileDialog.Title = "Select a PEM file"

# Show the OpenFileDialog
$dialogResult = $openFileDialog.ShowDialog()

# Check if a file was selected
if ($dialogResult -eq [System.Windows.Forms.DialogResult]::OK) {
    $privateKeyPath = $openFileDialog.FileName

    # Load the private key from the file
    $privateKey = Get-Content -Path $privateKeyPath -Raw

    # Convert to bytes
    $privateKeyBytes = [System.Text.Encoding]::UTF8.GetBytes($privateKey)

    # Encode the key to Base64
    $encodedKey = [Convert]::ToBase64String($privateKeyBytes)

    # Output the encoded key
    Write-Output $encodedKey
} else {
    Write-Output "No file selected."
}
