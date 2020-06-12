# encoding: utf-8
require "logstash/devutils/rspec/spec_helper"
require "logstash/outputs/microsoft-logstash-output-azure-loganalytics"
require "logstash/codecs/plain"
require "logstash/event"

describe LogStash::Outputs::AzureLogAnalytics do

  let(:workspace_id) { '<Workspace ID identifying your workspace>' }
  let(:workspace_key) { '<Primary Key for the Azure log analytics workspace>' }
  let(:custom_log_table_name) { 'ApacheAccessLog' }
  let(:key_names) { ['logid','date','processing_time','remote','user','method','status','agent','eventtime'] }
  let(:time_generated_field) { 'eventtime' }
  let(:amount_resizing) {false}

  # 1 second flush interval
  let(:plugin_flush_interval) {1}

  let(:azure_loganalytics_config) {
    { 
      "workspace_id" => workspace_id, 
      "workspace_key" => workspace_key,
      "custom_log_table_name" => custom_log_table_name,
      "key_names" => key_names,
      "time_generated_field" => time_generated_field,
      "plugin_flush_interval" => plugin_flush_interval,
      "amount_resizing" => amount_resizing
    }
  }

  let(:azure_loganalytics) { LogStash::Outputs::AzureLogAnalytics.new(azure_loganalytics_config) }

  before do
    azure_loganalytics.register
  end 

  describe "#flush" do
    it "Should successfully send the event to Azure Log Analytics" do
      events = []
      log1 = {
        :logid => "5cdad72f-c848-4df0-8aaa-ffe033e75d57",
        :date => "2017-04-22 09:44:32 JST",
        :processing_time => "372",
        :remote => "101.202.74.59",
        :user => "-",
        :method => "GET / HTTP/1.1",
        :status => "304",
        :size => "-",
        :referer => "-",
        :agent => "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.7; rv:27.0) Gecko/20100101 Firefox/27.0",
        :eventtime => "2017-04-22T01:44:32Z"
      }

      log2 = {
        :logid => "7260iswx-8034-4cc3-uirtx-f068dd4cd659",
        :date => "2017-04-22 09:45:14 JST",
        :processing_time => "105",
        :remote => "201.78.74.59",
        :user => "-",
        :method => "GET /manager/html HTTP/1.1",
        :status =>"200",
        :size => "-",
        :referer => "-",
        :agent => "Mozilla/5.0 (Windows NT 5.1; rv:5.0) Gecko/20100101 Firefox/5.0",
        :eventtime => "2017-04-22T01:45:14Z"
      }

      event1 =  LogStash::Event.new(log1) 
      event2 =  LogStash::Event.new(log2) 
      events.push(event1)
      events.push(event2)
      expect {azure_loganalytics.multi_receive(events)}.to_not raise_error
      # Waiting for the data to be sent
      sleep(plugin_flush_interval + 2)
    end
  end

end
