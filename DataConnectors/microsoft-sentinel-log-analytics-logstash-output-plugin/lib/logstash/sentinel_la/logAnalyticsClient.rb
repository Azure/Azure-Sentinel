# encoding: utf-8
require "logstash/sentinel_la/version"
require 'rest-client'
require 'json'
require 'openssl'
require 'base64'
require 'time'
require 'rbconfig'

module LogStash; module Outputs; class MicrosoftSentinelOutputInternal
class LogAnalyticsClient

require "logstash/sentinel_la/logstashLoganalyticsConfiguration"
require "logstash/sentinel_la/logAnalyticsAadTokenProvider"
require "logstash/sentinel_la/logAnalyticsMiTokenProvider"
require "logstash/sentinel_la/logAnalyticsArcTokenProvider"

  def azcmagent_running? # AZure Connected Machine AGENT is running outside of Azure and onboarded into Azure Arc
    system('azcmagent > /dev/null', [:out, :err] => IO::NULL)
  end # def azcmagent_running?

  def initialize(logstashLoganalyticsConfiguration)
    @logstashLoganalyticsConfiguration = logstashLoganalyticsConfiguration
    @logger = @logstashLoganalyticsConfiguration.logger

    la_api_version = "2023-01-01"
    @uri = sprintf("%s/dataCollectionRules/%s/streams/%s?api-version=%s",@logstashLoganalyticsConfiguration.data_collection_endpoint, @logstashLoganalyticsConfiguration.dcr_immutable_id, logstashLoganalyticsConfiguration.dcr_stream_name, la_api_version)

    if @logstashLoganalyticsConfiguration.managed_identity
      if azcmagent_running?
        @logger.info("Machine is Azure Arc-enabled server. Retrieving bearer token via azcmagent...")
        @aadTokenProvider=LogAnalyticsArcTokenProvider::new(logstashLoganalyticsConfiguration)
      else
        @logger.info("Using Managed Identity configuration. Retrieving bearer token for Managed Identity...")
        @aadTokenProvider=LogAnalyticsMiTokenProvider::new(logstashLoganalyticsConfiguration)
      end
    else
      @aadTokenProvider=LogAnalyticsAadTokenProvider::new(logstashLoganalyticsConfiguration)
    end

    @userAgent = getUserAgent()
  end # def initialize

  # Post the given json to Azure Loganalytics
  def post_data(body)
    raise ConfigError, 'no json_records' if body.empty?

    # Create REST request header
    headers = get_header()

    # Post REST request
    return RestClient::Request.execute(method: :post, url: @uri, payload: body, headers: headers,
                                        proxy: @logstashLoganalyticsConfiguration.proxy_endpoint, timeout: 240)
  end # def post_data

  # Static function to return if the response is OK or else
  def self.is_successfully_posted(response)
    return (response.code >= 200 && response.code < 300 ) ? true : false
  end # def self.is_successfully_posted

  private

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
