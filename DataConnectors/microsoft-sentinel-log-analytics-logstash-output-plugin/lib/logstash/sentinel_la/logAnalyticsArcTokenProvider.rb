# encoding: utf-8
require "logstash/sentinel_la/logstashLoganalyticsConfiguration"
require 'rest-client'
require 'json'
require 'openssl'
require 'base64'
require 'time'

module LogStash; module Outputs; class MicrosoftSentinelOutputInternal
class LogAnalyticsArcTokenProvider
  def initialize (logstashLoganalyticsConfiguration)
    scope = CGI.escape("#{logstashLoganalyticsConfiguration.get_monitor_endpoint}")
    @token_request_uri = sprintf("http://127.0.0.1:40342/metadata/identity/oauth2/token?api-version=2019-11-01&resource=%s", scope)
    # https://learn.microsoft.com/en-us/azure/azure-arc/servers/managed-identity-authentication
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

  # Find the path to the authentication token
  def get_challange_token_path()
    # Create REST request header
    headers = get_header1()
    begin
      response = RestClient::Request.execute(
        method: :get,
        url: @token_request_uri,
        headers: headers
      )
    rescue RestClient::ExceptionWithResponse => e
      response = e.response
    end

    # Path to .KEY file is stripped from response
    www_authenticate = response.headers[:www_authenticate]
    path = www_authenticate.split(' ')[1].gsub('realm=', '')
    return path
  end # def get_challange_token_path

  # With path to .KEY file we can retrieve Bearer token
  def get_challange_token()
    path = get_challange_token_path()
    # Check if the file is readable
    if ::File.readable?(path)
      # Read the content of the key file
      key_content = ::File.read(path)
      return key_content
    else
      # User must be a member of the himds group to be able to retrieve contents of .KEY file
      @logger.error("The file at #{path} is not readable by the current user. Please run the script as root.")
    end
  end # def get_challange_token

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
    @logger.info("Azure Arc Managed Identity token expired - refreshing token.")

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
        @logger.error("Exception while authenticating with Azure Arc Connected Machine API ['#{ewr.response}']")
      rescue Exception => ex
        @logger.trace("Exception while authenticating with Azure Arc Connected Machine API ['#{ex}']")
      end
      @logger.error("Error while authenticating with Azure Arc Connected Machine ('#{@token_request_uri}'), retrying in 10 seconds.")
      sleep 10
    end
  end # def post_token_request

  # Create a header
  def get_header()
    return {
      'Metadata' => 'true',
      'Authorization' => "Basic #{get_challange_token()}"
    }
  end # def get_header

  # Create a header
  def get_header1()
    return {
      'Metadata' => 'true',
    }
  end # def get_header1

end # end of class
end ;end ;end
