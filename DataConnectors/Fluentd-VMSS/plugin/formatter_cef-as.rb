#
# Fluentd
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.
#

require 'fluent/plugin/formatter'

module Fluent
  module Plugin
    class CEFFormatter < Formatter
      Plugin.register_formatter('cef-as', self)

      desc 'Field names included in each lines'
      #need to check shortname
      config_param :keys, :array, value_type: :string, default: ["act", "app", "c6a1", "c6a1Label", "c6a2", "c6a2Label", "c6a3", "c6a3Label", "c6a4", "c6a4Label", "cfp1", "cfp1Label", "cfp2", "cfp2Label", "cfp3", "cfp3Label", "cfp4", "cfp4Label", "cn1", "cn1Label", "cn2", "cn2Label", "cn3", "cn3Label", "cnt", "cs1", "cs1Label", "cs2", "cs2Label", "cs3", "cs3Label", "cs4", "cs4Label", "cs5", "cs5Label", "cs6", "cs6Label", "destinationDnsDomain", "destinationServiceName", "destinationTranslatedAddress", "destinationTranslatedPort", "deviceCustomDate1", "deviceCustomDate1Label", "deviceCustomDate2", "deviceCustomDate2Label", "deviceDirection", "deviceDnsDomain", "deviceExternalId", "deviceFacility", "deviceInboundInterface", "deviceNtDomain", "deviceOutboundInterface", "devicePayloadId", "deviceProcessName", "deviceTranslatedAddress", "dhost", "dmac", "dntdom", "dpid", "dpriv", "dproc", "dpt", "dst", "dtz", "duid", "duser", "dvc", "dvchost", "dvcmac", "dvcpid", "end", "externalId", "fileCreateTime", "fileHash", "fileId", "fileModificationTime", "filePath", "filePermission", "fileType", "flexDate1", "flexDate1Label", "flexNumber1", "flexNumber1Label", "flexNumber2", "flexNumber2Label", "flexString1", "flexString1Label", "flexString2", "flexString2Label", "fname", "fsize", "in", "msg", "oldFileCreateTime", "oldFileHash", "oldFileId", "oldFileModificationTime", "oldFileName", "oldFilePath", "oldFilePermission", "oldFileSize", "oldFileType", "out", "outcome", "proto", "reason", "request", "requestClientApplication", "requestContext", "requestCookies", "requestMethod", "rt", "shost", "smac", "sntdom", "sourceDnsDomain", "sourceServiceName", "sourceTranslatedAddress", "sourceTranslatedPort", "spid", "spriv", "sproc", "spt", "src", "start", "suid", "suser", "type", "agentDnsDomain", "agentNtDomain", "agentTranslatedAddress", "agentTranslatedZoneExternalID", "agentTranslatedZoneURI", "agentZoneExternalID", "agentZoneURI", "agt", "ahost", "aid", "amac", "art", "at", "atz", "av", "cat", "customerExternalID", "customerURI", "destinationTranslatedZoneExternalID", "destinationTranslatedZoneURI", "destinationZoneExternalID", "destinationZoneURI", "deviceTranslatedZoneExternalID", "deviceTranslatedZoneURI", "deviceZoneExternalID", "deviceZoneURI", "dlat", "dlong", "eventId", "rawEvent", "slat", "slong", "sourceTranslatedZoneExternalID", "sourceTranslatedZoneURI", "sourceZoneExternalID", "sourceZoneURI"]
      desc 'The delimiter character (or string) of CEF values'
      config_param :delimiter, :string, default: " "
      desc 'The parameter to enable writing to new lines'
      config_param :add_newline, :bool, default: true

      def format(tag, time, record)
        formatted = "CEF:0|" << record['cef_device_vendor'] << "|" << record['cef_device_product'] << "|" << record['cef_device_version'] << "|" << record['cef_device_event_class_id'] << "|" << record['cef_name'] << "|" << record['cef_severity'] << "|"
        @keys.map{|k|
          if record[k].nil?
            #dont add
          else
            formatted << k << "=" << record[k].to_s << @delimiter
          end
        }
        formatted << "\n".freeze if @add_newline
        formatted
      end
    end
  end
end
