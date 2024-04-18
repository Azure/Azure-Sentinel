# Known issue
If the raw data is in the below format
"Dec 27 17:14:23 vhkdlp1356 (squid-1): 1703668463.841    880 10.22.76.254 TCP_MISS/200 22853 CONNECT clsa.symphony.com:443 - HIER_DIRECT/18.138.195.23 -
"
## Squid proxy parser.

If raw data is in the above format [Squid proxy Parser](https://github.com/Azure/Azure-Sentinel\Solutions\SquidProxy\Parsers\SquidProxyv1.txt) .