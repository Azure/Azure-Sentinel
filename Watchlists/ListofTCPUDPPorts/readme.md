# TCP and UDP Ports and Descriptions
Author: Nathan Swift

This watchlist is meant to create a table of offical and unoffical tcp and udp port information. This watchlist can be used to provide context to other network based logs that do not contain port description or application service information running on port. Another use case could be potential use of Ingest Time Transformation rules to enrich port information.

A powershell Script is also included for reference on converting a .csv file into a single string for rawcontent needed in Rest API Call, LogicApp Action, or ARM Template to insert data int watchlist.

https://en.wikipedia.org/wiki/List_of_TCP_and_UDP_port_numbers

    _GetWatchlist('listoftcpudpports')
    // highest count was 16 OR , AltDescriptions
    | parse Description with * " OR " AltDescription1 " OR " AltDescription2  " OR " AltDescription3  " OR " AltDescription4  " OR " AltDescription5
    // 9 entries had very long port ranges, were inserted with -- between the ranges, future could be KQL to parse through ranges and convert string to int 
    //| where Port has "–-"

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FWatchlists%2FListofTCPUDPPorts%2Fazuredeploy.json)