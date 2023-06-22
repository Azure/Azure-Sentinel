# encoding: utf-8
require "logstash/outputs/base"
require "logstash/namespace"

class LogStash::Outputs::MicrosoftSentinelOutputLegacy < LogStash::Outputs::Base

  config_name "microsoft-sentinel-logstash-output-plugin"
  
  concurrency :shared

  config :client_app_Id, :validate => :string
  config :client_app_secret, :validate => :string
  config :tenant_id, :validate => :string
  config :data_collection_endpoint, :validate => :string
  config :dcr_immutable_id, :validate => :string
  config :dcr_stream_name, :validate => :string
  config :key_names, :validate => :array, :default => []
  config :plugin_flush_interval, :validate => :number, :default => 5
  config :decrease_factor, :validate => :number, :default => 100
  config :amount_resizing, :validate => :boolean, :default => true
  config :max_items, :validate => :number, :default => 2000
  config :proxy, :validate => :string, :default => ''
  config :retransmission_time, :validate => :number, :default => 10
  config :compress_data, :validate => :boolean, :default => false
  config :create_sample_file, :validate => :boolean, :default => false
  config :sample_file_path, :validate => :string  

  def register
    raise("The plugin was renamed to microsoft-sentinel-log-analytics-logstash-output-plugin. microsoft-sentinel-logstash-output-plugin will no longer be maintained.")
  end 