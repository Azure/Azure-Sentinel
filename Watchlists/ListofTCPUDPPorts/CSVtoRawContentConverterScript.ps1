# Created On: 4/13/2022 11:31 PM
# Created By: Nathan Swift
# This script is as is and not supported by Microsoft 
# Microsoft does not assume any risk of data loss
# Use it at your own risk
################################################################################

<#  Possible Futures:
 
1. recreate the script with aprameters and a function
2. build a way to auto generate the Headers dynamically into the entry string

#>


# Update This ! # Put your own path to create the rawcontent output file
$rawcontentpath = "C:\Users\username\Downloads\rawcontent.txt"

# Outputfile for vm inventory
$outputFile = $rawcontentpath


# Update This ! #  Put your own csv file path to import into PS
$filePath = "C:\Users\username\Downloads\ListofTCPandUDPportnumbers.csv"

# import csv file into a PS table for rawcontent conversion
$csvData = Import-Csv -Path $filepath

# Update This ! # manually set your headers into the file here be sure to keep \r\n at end of last column header
$headerstring = "Port,TCP,UDP,SCTP,DCCP,Description\r\n"

#Set and apply 1st line of csv headers
$headerstring | Out-File $outputFile -Append -NoNewline

## Future section for auto generating the $entrystring with headers automatically rather than static assignment
<# $headers = $headerstring.Split(',')
$counter = 0

do {

    $header

} while ($counter -le $headers.count )
#>

# conversion of each entry into a rawcontent string to be appended 
foreach ($entry in $csvData){
    
    # Update This ! # Be sure to update the .headers according to your needs
    # example: "Port,TCP,UDP,SCTP,DCCP,Description\r\n"
    $entrystring = $entry.Port + "," + $entry.TCP + "," + $entry.UDP + "," + $entry.SCTP + "," + $entry.DCCP + "," + $entry.Description + "\r\n"
    
    #Set and apply next entry line from csv
    $entrystring | Out-File $outputFile -Append -NoNewline

}