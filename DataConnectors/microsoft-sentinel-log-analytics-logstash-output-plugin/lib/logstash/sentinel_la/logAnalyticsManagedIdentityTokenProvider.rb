# encoding: utf-8
require "logstash/sentinel_la/logstashLoganalyticsConfiguration"
require 'rest-client'
require 'json'
require 'time'
require 'uri'
require 'cgi'

module LogStash; module Outputs; class MicrosoftSentinelOutputInternal
class LogAnalyticsManagedIdentityTokenProvider
  def initialize(logstashLoganalyticsConfiguration)
    @logger = logstashLoganalyticsConfiguration.logger
    @config = logstashLoganalyticsConfiguration

    # Token caching with thread safety
    @token_state = {
      :access_token => nil,
      :expiry_time => nil,
      :token_details_mutex => Mutex.new,
    }

    # Detect authentication mode at initialization
    if workload_identity_available?
      @auth_mode = :workload_identity
      setup_workload_identity()
    else
      @auth_mode = :imds
      setup_imds()
    end

    @logger.info("Managed Identity provider initialized - mode: #{@auth_mode}")
  end

  # Public interface - matches AadTokenProvider
  public

  def get_aad_token_bearer()
    @token_state[:token_details_mutex].synchronize do
      if is_saved_token_need_refresh?
        refresh_saved_token()
      end
      return @token_state[:access_token]
    end
  end

  private

  def is_saved_token_need_refresh?
    @token_state[:access_token].nil? ||
    @token_state[:expiry_time].nil? ||
    @token_state[:expiry_time] <= Time.now
  end

  def refresh_saved_token()
    @logger.info("Managed Identity token expired - refreshing via #{@auth_mode}")

    token_response = request_token()
    @token_state[:access_token] = token_response["access_token"]
    @token_state[:expiry_time] = get_token_expiry_time(token_response["expires_in"].to_i)
  end

  def get_token_expiry_time(expires_in_seconds)
    if expires_in_seconds.nil? || expires_in_seconds <= 0
      Time.now + (60 * 60 * 24)  # 24-hour fallback
    else
      Time.now + expires_in_seconds - 1  # 1-second safety buffer
    end
  end

  # Detection: check for AKS workload identity environment variables
  def workload_identity_available?
    client_id = ENV['AZURE_CLIENT_ID']
    tenant_id = ENV['AZURE_TENANT_ID']
    token_file = ENV['AZURE_FEDERATED_TOKEN_FILE']

    return false if client_id.nil? || client_id.empty?
    return false if tenant_id.nil? || tenant_id.empty?
    return false if token_file.nil? || token_file.empty?

    if ::File.readable?(token_file)
      @logger.debug("Workload identity token file found: #{token_file}")
      true
    else
      @logger.debug("Workload identity token file not readable: #{token_file}")
      false
    end
  end

  # Setup for OIDC/Workload Identity
  def setup_workload_identity()
    @client_id = ENV['AZURE_CLIENT_ID']
    @tenant_id = ENV['AZURE_TENANT_ID']
    @token_file_path = ENV['AZURE_FEDERATED_TOKEN_FILE']
    # Use AZURE_AUTHORITY_HOST if set (AKS sets this), otherwise use cloud-appropriate endpoint
    # Strip trailing slash to avoid double-slash in endpoint URL
    @authority_host = (ENV['AZURE_AUTHORITY_HOST'] || @config.get_aad_endpoint).chomp('/')

    @scope = "#{@config.get_monitor_endpoint}/.default"
    @token_endpoint = "#{@authority_host}/#{@tenant_id}/oauth2/v2.0/token"

    @logger.info("Workload Identity configured - client_id: #{@client_id}, endpoint: #{@token_endpoint}")
  end

  # Setup for IMDS (VM Managed Identity)
  def setup_imds()
    resource = CGI.escape(@config.get_monitor_endpoint)
    @token_endpoint = "http://169.254.169.254/metadata/identity/oauth2/token" \
                      "?api-version=2018-02-01&resource=#{resource}"

    # Support user-assigned managed identity via object_id
    object_id = @config.managed_identity_object_id
    if object_id && !object_id.empty?
      @token_endpoint += "&object_id=#{CGI.escape(object_id)}"
      @logger.info("IMDS configured with user-assigned identity: #{object_id}")
    else
      @logger.info("IMDS configured with system-assigned identity")
    end
  end

  # Dispatch to appropriate token request method
  def request_token()
    case @auth_mode
    when :workload_identity
      request_workload_identity_token()
    when :imds
      request_imds_token()
    end
  end

  # OIDC token exchange for AKS Workload Identity
  def request_workload_identity_token()
    # Read fresh OIDC token from mounted file (Kubernetes rotates this)
    federated_token = ::File.read(@token_file_path).strip

    payload = {
      'grant_type' => 'client_credentials',
      'client_id' => @client_id,
      'client_assertion_type' => 'urn:ietf:params:oauth:client-assertion-type:jwt-bearer',
      'client_assertion' => federated_token,
      'scope' => @scope
    }

    headers = { 'Content-Type' => 'application/x-www-form-urlencoded' }

    post_with_retry(@token_endpoint, URI.encode_www_form(payload), headers, :post)
  end

  # IMDS token request for VM Managed Identity
  def request_imds_token()
    headers = { 'Metadata' => 'true' }

    post_with_retry(@token_endpoint, nil, headers, :get)
  end

  # Unified retry logic for both authentication methods
  def post_with_retry(url, payload, headers, method)
    while true
      begin
        response = RestClient::Request.execute(
          method: method,
          url: url,
          payload: payload,
          headers: headers,
          proxy: @config.proxy_aad
        )

        if response.code == 200 || response.code == 201
          return JSON.parse(response.body)
        end
      rescue RestClient::ExceptionWithResponse => e
        @logger.error("Token request failed: #{e.response.code} - #{e.response.body}")
      rescue => e
        @logger.error("Token request exception: #{e.message}")
      end

      @logger.error("Retrying #{@auth_mode} token request in 10 seconds...")
      sleep 10
    end
  end

end
end; end; end
