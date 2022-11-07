# encoding: utf-8

require "logstash/sentinel/logAnalyticsClient"
require "logstash/sentinel/logstashLoganalyticsConfiguration"

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
            # 429 (too many requests) are retried forever 
            # All other http errors are retried for total every of @logstashLoganalyticsConfiguration.RETRANSMISSION_DELAY until @logstashLoganalyticsConfiguration.retransmission_time seconds passed
            begin
                @logger.debug(transmission_verb(is_retry) + " log batch (amount of documents: #{amount_of_documents}) to DCR stream #{@logstashLoganalyticsConfiguration.dcr_stream_name} to #{api_name}.")
                response = @client.post_data(call_payload)
                
                if LogAnalyticsClient.is_successfully_posted(response)
                    @logger.info("Successfully posted #{amount_of_documents} logs into log analytics DCR stream [#{@logstashLoganalyticsConfiguration.dcr_stream_name}].")
                    return
                else
                    @logger.error("#{api_name} request failed. Error code: #{response.code} #{try_get_info_from_error_response(response)}")
                    @logger.trace("Rest client response ['#{response}']")
                end

            rescue RestClient::ExceptionWithResponse => ewr
                response = ewr.response
                @logger.error("Exception when posting data to #{api_name}. #{try_get_info_from_error_response(ewr.response)} [Exception: '#{ewr}, amount of documents=#{amount_of_documents}]'")
                @logger.trace("Exception in posting data to #{api_name}. Rest client response ['#{ewr.response}']. [amount_of_documents=#{amount_of_documents} request payload=#{call_payload}]")

                if ewr.http_code.to_f == 400
                    @logger.info("Not trying to resend since exception http code is #{ewr.http_code}")
                    return                
                elsif ewr.http_code.to_f == 429
                    # thrutteling detected, backoff before resending
                    parsed_retry_after = response.headers.include?(:retry_after) ? response.headers[:retry_after].to_i : 0
                    seconds_to_sleep = parsed_retry_after > 0 ? parsed_retry_after : 30

                    #force another retry even if the next iteration of the loop will be after the retransmission_timeout
                    force_retry = true
                end
            rescue Exception => ex
                @logger.error("Exception in posting data to #{api_name}. [Exception: '#{ex}]'")
                @logger.trace("Exception in posting data to #{api_name}.[amount_of_documents=#{amount_of_documents} request payload=#{call_payload}]")       
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

    # Try to get the values of the x-ms-error-code and x-ms-request-id headers and decorate it for printing
    def try_get_info_from_error_response(response)
        output = ""
        if response.headers.include?(:x_ms_error_code)
            output += " [ms-error-code header: #{response.headers[:x_ms_error_code]}]"
        end
        if response.headers.include?(:x_ms_request_id)
            output += " [x-ms-request-id header: #{response.headers[:x_ms_request_id]}]"
        end
        return output
    end

end
end;end;end;
