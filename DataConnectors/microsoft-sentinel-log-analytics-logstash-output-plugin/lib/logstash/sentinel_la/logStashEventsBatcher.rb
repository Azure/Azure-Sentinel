# encoding: utf-8

require "logstash/sentinel_la/logAnalyticsClient"
require "logstash/sentinel_la/logstashLoganalyticsConfiguration"
require "excon"
# LogStashAutoResizeBuffer class setting a resizable buffer which is flushed periodically
# The buffer resize itself according to Azure Loganalytics  and configuration limitations
module LogStash; module Outputs; class MicrosoftSentinelOutputInternal
class LogStashEventsBatcher
    
    def initialize(logstashLoganalyticsConfiguration)
        @logstashLoganalyticsConfiguration = logstashLoganalyticsConfiguration
        @logger = @logstashLoganalyticsConfiguration.logger
        @client = LogAnalyticsClient::new(logstashLoganalyticsConfiguration)
    end # initialize

    public
    def batch_event_document(event_document)
        # todo: ensure the json serialization only occurs once. 
        current_document_size = event_document.to_json.bytesize
        if (current_document_size >= @logstashLoganalyticsConfiguration.MAX_SIZE_BYTES - 1000)
            @logger.error("Received document above the max allowed size - dropping the document [document size: #{current_document_size}, max allowed size: #{@buffer_config[:flush_each]}")
        else
            batch_event(event_document)
        end
    end # def add_event_document

    protected
    def close
        raise "Method close not implemented"
    end

    def batch_event(event_document)
        raise "Method batch_event not implemented"
    end
   
    def send_message_to_loganalytics(call_payload, amount_of_documents)

        retransmission_timeout = Time.now.to_i + @logstashLoganalyticsConfiguration.retransmission_time
        api_name = "Logs Ingestion API"
        is_retry = false
        force_retry = false

        while Time.now.to_i < retransmission_timeout || force_retry
            seconds_to_sleep = @logstashLoganalyticsConfiguration.RETRANSMISSION_DELAY
            force_retry = false
            # Retry logic:
            # 400 bad request or general exceptions are dropped
            # 408 reqeust timeout and client timeout (open/read) will retry the current message
            # 429 (too many requests) are retried forever 
            # All other http errors are retried for total every of @logstashLoganalyticsConfiguration.RETRANSMISSION_DELAY until @logstashLoganalyticsConfiguration.retransmission_time seconds passed
            begin
                @logger.debug(transmission_verb(is_retry) + " log batch (amount of documents: #{amount_of_documents}) to DCR stream #{@logstashLoganalyticsConfiguration.dcr_stream_name} to #{api_name}.")
                response = @client.post_data(call_payload)
                
                if LogAnalyticsClient.is_successfully_posted(response)
                    request_id = get_request_id_from_response(response)
                    @logger.info("Successfully posted #{amount_of_documents} logs into log analytics DCR stream [#{@logstashLoganalyticsConfiguration.dcr_stream_name}] x-ms-request-id [#{request_id}].")
                    return
                else
                    @logger.trace("Rest client response ['#{response}']")
                    @logger.error("#{api_name} request failed. Error code: #{response.pree} #{try_get_info_from_error_response(response)}")
                end
                rescue Excon::Error::HTTPStatus => ewr
                    response = ewr.response
                    @logger.trace("Exception in posting data to #{api_name}. Rest client response ['#{response}']. [amount_of_documents=#{amount_of_documents} request payload=#{call_payload}]")
                    @logger.error("Exception when posting data to #{api_name}. [Exception: '#{ewr.class}'] #{try_get_info_from_error_response(ewr.response)} [amount of documents=#{amount_of_documents}]'")

                    if ewr.class ==  Excon::Error::BadRequest
                        @logger.info("Not trying to resend since exception http code is 400")
                        return                
                    elsif ewr.class ==  Excon::Error::RequestTimeout
                        force_retry = true
                    elsif ewr.class ==  Excon::Error::TooManyRequests
                        # throttling detected, backoff before resending
                        parsed_retry_after = response.data[:headers].include?('Retry-After') ? response.data[:headers]['Retry-After'].to_i : 0
                        seconds_to_sleep = parsed_retry_after > 0 ? parsed_retry_after : 30

                        #force another retry even if the next iteration of the loop will be after the retransmission_timeout
                        force_retry = true
                    end               
                rescue Excon::Error::Socket => ex
                    @logger.trace("Exception: '#{ex.class.name}]#{ex} in posting data to #{api_name}. [amount_of_documents=#{amount_of_documents}]'")
                    force_retry = true
                rescue Excon::Error::Timeout => ex
                    @logger.trace("Exception: '#{ex.class.name}]#{ex} in posting data to #{api_name}. [amount_of_documents=#{amount_of_documents}]'")
                    force_retry = true
                rescue Exception => ex
                    @logger.trace("Exception in posting data to #{api_name}.[amount_of_documents=#{amount_of_documents} request payload=#{call_payload}]")       
                    @logger.error("Exception in posting data to #{api_name}. [Exception: '[#{ex.class.name}]#{ex}, amount of documents=#{amount_of_documents}]'")
            end
            is_retry = true
            @logger.info("Retrying transmission to #{api_name} in #{seconds_to_sleep} seconds.")

            sleep seconds_to_sleep
        end

        @logger.error("Could not resend #{amount_of_documents} documents, message is dropped after retransmission_time exceeded.")
        @logger.trace("Documents (#{amount_of_documents}) dropped. [call_payload=#{call_payload}]")
    end # end send_message_to_loganalytics
    
    private
    def transmission_verb(is_retry)
        if is_retry
            "Resending"
        else
            "Posting"
        end
    end

    def get_request_id_from_response(response)
        output =""
        begin
            if !response.nil? && response.data[:headers].include?("x-ms-request-id")
                output += response.data[:headers]["x-ms-request-id"]
            end
        rescue Exception => ex
            @logger.debug("Error while getting reqeust id from success response headers: #{ex.display}")
        end
       return output
    end

    # Try to get the values of the x-ms-error-code and x-ms-request-id headers and content of body, decorate it for printing
    def try_get_info_from_error_response(response)
        begin
            output = ""
            if !response.nil?                
                if response.data[:headers].include?("x-ms-error-code")
                    output += " [ms-error-code header: #{response.data[:headers]["x-ms-error-code"]}]"
            end
            if response.data[:headers].include?("x-ms-request-id")
                output += " [x-ms-request-id header: #{response.data[:headers]["x-ms-request-id"]}]"
            end
            output += " [response body: #{response.data[:body]}]"            
        end        
            return output
        rescue Exception => ex
            @logger.debug("Error while getting reqeust id from headers: #{ex.display}")
            return " [response content: #{response.to_s}]"
        end
    end

end
end;end;end;
