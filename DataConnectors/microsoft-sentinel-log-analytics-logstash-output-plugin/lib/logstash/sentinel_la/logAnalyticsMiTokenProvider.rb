# encoding: utf-8
require "logstash/sentinel_la/logstashLoganalyticsConfiguration"
require 'rest-client'
require 'json'
require 'openssl'
require 'base64'
require 'time'

module LogStash; module Outputs; class MicrosoftSentinelOutputInternal
class LogAnalyticsMiTokenProvider
  def initialize (logstashLoganalyticsConfiguration)
    scope = CGI.escape("#{logstashLoganalyticsConfiguration.get_monitor_endpoint}")
    @token_request_uri = sprintf("http://169.254.169.254/metadata/identity/oauth2/token?api-version=2018-02-01&resource=%s", scope)
    # https://learn.microsoft.com/en-us/entra/identity/managed-identities-azure-resources/how-to-use-vm-token
    @token_state = {
      :access_token => nil,
      :expiry_time => nil,
      :token_details_mutex => Mutex.new,
    }
    @logger = logstashLoganalyticsConfiguration.logger
    @logstashLoganalyticsConfiguration = logstashLoganalyticsConfiguration
  end # def initialize

  # Public methods
  public

  def get_aad_token_bearer()
    @token_state[:token_details_mutex].synchronize do
      if is_saved_token_need_refresh()
        refresh_saved_token()
      end
      return @token_state[:access_token]
    end
  end # def get_aad_token_bearer

  # Private  methods
  private

  def is_saved_token_need_refresh()
    return @token_state[:access_token].nil? || @token_state[:expiry_time].nil? || @token_state[:expiry_time] <= Time.now
  end # def is_saved_token_need_refresh

  def refresh_saved_token()
    @logger.info("Managed Identity token expired - refreshing token.")

    token_response = post_token_request()
    @token_state[:access_token] = token_response["access_token"]
    @token_state[:expiry_time] = get_token_expiry_time(token_response["expires_in"].to_i)

  end # def refresh_saved_token

  def get_token_expiry_time (expires_in_seconds)
    if (expires_in_seconds.nil? || expires_in_seconds <= 0)
      return Time.now + (60 * 60 * 24) # Refresh anyway in 24 hours
    else
      return Time.now + expires_in_seconds - 1; # Decrease by 1 second to be on the safe side
    end
  end # def get_token_expiry_time

  # Post the given json to Azure Loganalytics
  def post_token_request()
    # Create REST request header
    headers = get_header()
    while true
      begin
        # GET REST request
        response = RestClient::Request.execute(
          method: :get,
          url: @token_request_uri,
          headers: headers,
          proxy: @logstashLoganalyticsConfiguration.proxy_aad
        )

        if (response.code == 200 || response.code == 201)
          return JSON.parse(response.body)
        end
      rescue RestClient::ExceptionWithResponse => ewr
        @logger.error("Exception while authenticating with Microsoft Entra ID API ['#{ewr.response}']")
      rescue Exception => ex
        @logger.trace("Exception while authenticating with Microsoft Entra ID API ['#{ex}']")
      end
      @logger.error("Error while authenticating with Microsoft Entra ID - check if Managed Identity configuration is correct. ('#{@token_request_uri}'), retrying in 10 seconds.")
      sleep 10
    end
  end # def post_token_request

  # Create a header
  def get_header()
    return {
      # 'Content-Type' => 'application/x-www-form-urlencoded',
      'Metadata' => 'true',
    }
  end # def get_header

end # end of class
end ;end ;end
