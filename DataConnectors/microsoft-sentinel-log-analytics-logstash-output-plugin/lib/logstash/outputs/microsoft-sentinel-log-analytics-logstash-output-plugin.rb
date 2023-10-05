# encoding: utf-8
require "logstash/outputs/base"
require "logstash/namespace"
require "logstash/sentinel_la/logstashLoganalyticsConfiguration"
require "logstash/sentinel_la/sampleFileCreator"
require "logstash/sentinel_la/logsSender"


class LogStash::Outputs::MicrosoftSentinelOutput < LogStash::Outputs::Base

  config_name "microsoft-sentinel-log-analytics-logstash-output-plugin"
  
  # Stating that the output plugin will run in concurrent mode
  concurrency :shared

  # Your registered app ID
  config :client_app_Id, :validate => :string

  # The registered app's secret, required by Azure Loganalytics REST API
  config :client_app_secret, :validate => :string

  # Your Operations Management Suite Tenant ID
  config :tenant_id, :validate => :string

  # Your data collection rule endpoint
  config :data_collection_endpoint, :validate => :string

  # Your data collection rule ID
  config :dcr_immutable_id, :validate => :string

  # Your dcr data stream name
  config :dcr_stream_name, :validate => :string

  # Subset of keys to send to the Azure Loganalytics workspace
  config :key_names, :validate => :array, :default => []

  # Max number of seconds to wait between flushes. Default 5
  config :plugin_flush_interval, :validate => :number, :default => 5

  # Factor for adding to the amount of messages sent
  config :decrease_factor, :validate => :number, :default => 100

  # This will trigger message amount resizing in a REST request to LA
  config :amount_resizing, :validate => :boolean, :default => true

  # Setting the default amount of messages sent                                                                                                    
  # it this is set with amount_resizing=false --> each message will have max_items
  config :max_items, :validate => :number, :default => 2000

  # Setting default proxy to be used for all communication with azure
  config :proxy, :validate => :string
  
  # Setting proxy_aad to be used for communicating with azure active directory service
  config :proxy_aad, :validate => :string
  
  # Setting proxy to be used for the LogAnalytics endpoint REST client
  config :proxy_endpoint, :validate => :string

  # This will set the amount of time given for retransmitting messages once sending is failed
  config :retransmission_time, :validate => :number, :default => 10

  # Compress the message body before sending to LA
  config :compress_data, :validate => :boolean, :default => false

  # Generate sample file from incoming events
  config :create_sample_file, :validate => :boolean, :default => false

  # Path where to place the sample file created
  config :sample_file_path, :validate => :string

  public
  def register
    @logstash_configuration= build_logstash_configuration()
	
    # Validate configuration correctness 
    @logstash_configuration.validate_configuration()

    @events_handler = @logstash_configuration.create_sample_file ?
                        LogStash::Outputs::MicrosoftSentinelOutputInternal::SampleFileCreator::new(@logstash_configuration) :
                        LogStash::Outputs::MicrosoftSentinelOutputInternal::LogsSender::new(@logstash_configuration)
  end # def register

  def multi_receive(events)
    @events_handler.handle_events(events)
  end # def multi_receive

  def close
    @events_handler.close
  end

  #private 
  private

  # Building the logstash object configuration from the output configuration provided by the user
  # Return LogstashLoganalyticsOutputConfiguration populated with the configuration values
  def build_logstash_configuration()
    logstash_configuration= LogStash::Outputs::MicrosoftSentinelOutputInternal::LogstashLoganalyticsOutputConfiguration::new(@client_app_Id, @client_app_secret, @tenant_id, @data_collection_endpoint, @dcr_immutable_id, @dcr_stream_name, @compress_data, @create_sample_file, @sample_file_path, @logger)
    logstash_configuration.key_names = @key_names
    logstash_configuration.plugin_flush_interval = @plugin_flush_interval
    logstash_configuration.decrease_factor = @decrease_factor
    logstash_configuration.amount_resizing = @amount_resizing
    logstash_configuration.max_items = @max_items
    logstash_configuration.proxy_aad = @proxy_aad || @proxy || ENV['http_proxy']
    logstash_configuration.proxy_endpoint = @proxy_endpoint || @proxy || ENV['http_proxy']
    logstash_configuration.retransmission_time = @retransmission_time
    
    return logstash_configuration
  end # def build_logstash_configuration

end # class LogStash::Outputs::MicrosoftSentinelOutput
