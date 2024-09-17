# encoding: utf-8
require "logstash/sentinel_la/version"
require 'json'
require 'openssl'
require 'base64'
require 'time'
require 'rbconfig'
require 'excon'

module LogStash; module Outputs; class MicrosoftSentinelOutputInternal 
class LogAnalyticsClient

require "logstash/sentinel_la/logstashLoganalyticsConfiguration"
require "logstash/sentinel_la/logAnalyticsAadTokenProvider"


  def initialize(logstashLoganalyticsConfiguration)
    @logstashLoganalyticsConfiguration = logstashLoganalyticsConfiguration
    @logger = @logstashLoganalyticsConfiguration.logger

    la_api_version = "2023-01-01"
    @uri = sprintf("%s/dataCollectionRules/%s/streams/%s?api-version=%s",@logstashLoganalyticsConfiguration.data_collection_endpoint, @logstashLoganalyticsConfiguration.dcr_immutable_id, logstashLoganalyticsConfiguration.dcr_stream_name, la_api_version)
    @aadTokenProvider=LogAnalyticsAadTokenProvider::new(logstashLoganalyticsConfiguration)
    @userAgent = getUserAgent()
    
    # Auto close connection after 60 seconds of inactivity
    @connectionAutoClose = {
      :last_use => Time.now,
      :lock => Mutex.new,
      :max_idel_time => 60,
      :is_closed => true
    }

    @timer = Thread.new do
      loop do
        sleep @connectionAutoClose[:max_idel_time] / 2
        if is_connection_stale?
          @connectionAutoClose[:lock].synchronize do
            if is_connection_stale?
              reset_connection
            end
          end
        end
      end
    end

   
  end # def initialize

  # Post the given json to Azure Loganalytics
  def post_data(body)
    raise ConfigError, 'no json_records' if body.empty?
    response = nil
    
    @connectionAutoClose[:lock].synchronize do 
      #close connection if its stale
      if is_connection_stale?
        reset_connection
      end
      if @connectionAutoClose[:is_closed]
        open_connection
      end
      
      headers = get_header()
      # Post REST request
      response = @connection.request(method: :post, body: body, headers: headers)
      @connectionAutoClose[:is_closed] = false
      @connectionAutoClose[:last_use] = Time.now
    end
    return response

  end # def post_data

  # Static function to return if the response is OK or else
  def self.is_successfully_posted(response)
    return (response.status >= 200 && response.status < 300 ) ? true : false
  end # def self.is_successfully_posted

  private 

  def open_connection
    @connection = Excon.new(@uri, :persistent => true, :proxy => @logstashLoganalyticsConfiguration.proxy_endpoint, 
          expects: [200, 201, 202, 204, 206, 207, 208, 226, 300, 301, 302, 303, 304, 305, 306, 307, 308],
          read_timeout: 240, write_timeout: 240, connect_timeout: 240)
    @logger.trace("Connection to Azure LogAnalytics was opened.");
  end

  def reset_connection
    @connection.reset
    @connectionAutoClose[:is_closed] = true    
    @logger.trace("Connection to Azure LogAnalytics was closed due to inactivity.");
  end

  def is_connection_stale?
    return Time.now - @connectionAutoClose[:last_use] > @connectionAutoClose[:max_idel_time] && !@connectionAutoClose[:is_closed]
  end
  # Create a header for the given length 
  def get_header()
    # Getting an authorization token bearer (if the token is expired, the method will post a request to get a new authorization token)
    token_bearer = @aadTokenProvider.get_aad_token_bearer()

    headers = {
          'Content-Type' => 'application/json',
          'Authorization' => sprintf("Bearer %s", token_bearer),
          'User-Agent' => @userAgent
    }

    if @logstashLoganalyticsConfiguration.compress_data
        headers = headers.merge({
          'Content-Encoding' => 'gzip'
        })
    end

    return headers
  end # def get_header

  def ruby_agent_version()
    case RUBY_ENGINE
        when 'jruby'
            "jruby/#{JRUBY_VERSION} (#{RUBY_VERSION}p#{RUBY_PATCHLEVEL})"
        else
            "#{RUBY_ENGINE}/#{RUBY_VERSION}p#{RUBY_PATCHLEVEL}"
    end
  end

  def architecture()
    "#{RbConfig::CONFIG['host_os']} #{RbConfig::CONFIG['host_cpu']}"
  end

  def getUserAgent()
    "SentinelLogstashPlugin|#{LogStash::Outputs::MicrosoftSentinelOutputInternal::VERSION}|#{architecture}|#{ruby_agent_version}"
  end #getUserAgent

end # end of class
end ;end ;end 