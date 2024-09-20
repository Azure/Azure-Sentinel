# encoding: utf-8
require "logstash/logAnalyticsClient/logstashLoganalyticsConfiguration"
require 'rest-client'
require 'json'
require 'openssl'
require 'base64'
require 'time'

class LogAnalyticsClient
  API_VERSION = '2016-04-01'.freeze

  def initialize (logstashLoganalyticsConfiguration)
    @logstashLoganalyticsConfiguration = logstashLoganalyticsConfiguration
    set_proxy(@logstashLoganalyticsConfiguration.proxy)
    @uri = sprintf("https://%s.%s/api/logs?api-version=%s", @logstashLoganalyticsConfiguration.workspace_id, @logstashLoganalyticsConfiguration.endpoint, API_VERSION)
  end # def initialize


  # Post the given json to Azure Loganalytics
  def post_data(body)
    raise ConfigError, 'no json_records' if body.empty?
    # Create REST request header
    header = get_header(body.bytesize)
    # Post REST request 
    response = RestClient.post(@uri, body, header)

    return response
  end # def post_data

  private 

  # Create a header for the given length 
  def get_header(body_bytesize_length)
    # We would like each request to be sent with the current time
    date = rfc1123date()

    return {
      'Content-Type' => 'application/json',
      'Authorization' => signature(date, body_bytesize_length),
      'Log-Type' => @logstashLoganalyticsConfiguration.custom_log_table_name,
      'x-ms-date' => date,
      'time-generated-field' =>  @logstashLoganalyticsConfiguration.time_generated_field,
      'x-ms-AzureResourceId' => @logstashLoganalyticsConfiguration.azure_resource_id
    }
  end # def get_header

  # Setting proxy for the REST client.
  # This option is not used in the output plugin and will be used 
  #  
  def set_proxy(proxy='')
    RestClient.proxy = proxy.empty? ? ENV['http_proxy'] : proxy
  end # def set_proxy

  # Return the current data 
  def rfc1123date()
    current_time = Time.now
    
    return current_time.httpdate()
  end # def rfc1123date

  def signature(date, body_bytesize_length)
    sigs = sprintf("POST\n%d\napplication/json\nx-ms-date:%s\n/api/logs", body_bytesize_length, date)
    utf8_sigs = sigs.encode('utf-8')
    decoded_shared_key = Base64.decode64(@logstashLoganalyticsConfiguration.workspace_key)
    hmac_sha256_sigs = OpenSSL::HMAC.digest(OpenSSL::Digest.new('sha256'), decoded_shared_key, utf8_sigs)
    encoded_hash = Base64.encode64(hmac_sha256_sigs)
    authorization = sprintf("SharedKey %s:%s", @logstashLoganalyticsConfiguration.workspace_id, encoded_hash)
    
    return authorization
  end # def signature

end # end of class