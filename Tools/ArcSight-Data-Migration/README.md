# lacat script for AcrSight Logger Archives Migration

This utility can be used to export CEF records ( available in dat format) from ArcSight Logger archive. The output can be exported to specified output file in the JSON format. When the file is not specified, the output is printed over stdout (by default).


- Method to run this script

    $META=ArcSight_Metadata_1_504403158265500976.csv.gz

    $ERRLOG=Err_1_504403158265500976.log

    $JSONOUT=Out_1_504403158265500976.json.gz
    
    $DATIN=ArcSight_Data_1_0504403158265500976.dat

    ./lacat-opt.py -j $DATIN $META  2> $ERRLOG | gzip -c > $JSONOUT
