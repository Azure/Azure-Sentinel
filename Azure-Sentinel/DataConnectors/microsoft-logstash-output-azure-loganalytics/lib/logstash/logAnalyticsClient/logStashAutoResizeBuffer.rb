# encoding: utf-8
require "stud/buffer"
require "logstash/logAnalyticsClient/logAnalyticsClient"
require "stud/buffer"
require "logstash/logAnalyticsClient/logstashLoganalyticsConfiguration"

# LogStashAutoResizeBuffer class setting a resizable buffer which is flushed periodically
# The buffer resize itself according to Azure Loganalytics  and configuration limitations
class LogStashAutoResizeBuffer
    include Stud::Buffer

    def initialize(logstashLoganalyticsConfiguration)
        @logstashLoganalyticsConfiguration = logstashLoganalyticsConfiguration
        @logger = @logstashLoganalyticsConfiguration.logger
        @client=LogAnalyticsClient::new(logstashLoganalyticsConfiguration)
        buffer_initialize(
          :max_items => logstashLoganalyticsConfiguration.max_items,
          :max_interval => logstashLoganalyticsConfiguration.plugin_flush_interval,
          :logger => @logstashLoganalyticsConfiguration.logger
        )
    end # initialize

    # Public methods
    public

    # Adding an event document into the buffer
    def add_event_document(event_document)
        buffer_receive(event_document)
    end # def add_event_document

    # Flushing all buffer content to Azure Loganalytics.
    # Called from Stud::Buffer#buffer_flush when there are events to flush
    def flush (documents, close=false)
        # Skip in case there are no candidate documents to deliver
        if documents.length < 1
            @logger.warn("No documents in batch for log type #{@logstashLoganalyticsConfiguration.custom_log_table_name}. Skipping")
            return
        end

        # We send Json in the REST request 
        documents_json = documents.to_json
        # Setting resizing to true will cause changing the max size
        if @logstashLoganalyticsConfiguration.amount_resizing == true
            # Resizing the amount of messages according to size of message received and amount of messages
            change_message_limit_size(documents.length, documents_json.bytesize)
        end
        send_message_to_loganalytics(documents_json, documents.length)
    end # def flush

    # Private methods 
    private 

    # Send documents_json to Azure Loganalytics  
    def send_message_to_loganalytics(documents_json, amount_of_documents)
        begin
            @logger.debug("Posting log batch (log count: #{amount_of_documents}) as log type #{@logstashLoganalyticsConfiguration.custom_log_table_name} to DataCollector API.")
            response = @client.post_data(documents_json)
            if is_successfully_posted(response)
                @logger.info("Successfully posted #{amount_of_documents} logs into custom log analytics table[#{@logstashLoganalyticsConfiguration.custom_log_table_name}].")
            else
                @logger.error("DataCollector API request failure: error code: #{response.code}, data=>" + (documents.to_json).to_s)
                resend_message(documents_json, amount_of_documents, @logstashLoganalyticsConfiguration.retransmission_time)
            end
            rescue Exception => ex
                @logger.error("Exception in posting data to Azure Loganalytics.\n[Exception: '#{ex}]'")
                @logger.trace("Exception in posting data to Azure Loganalytics.[amount_of_documents=#{amount_of_documents} documents=#{documents_json}]")
                resend_message(documents_json, amount_of_documents, @logstashLoganalyticsConfiguration.retransmission_time)
            end
    end # end send_message_to_loganalytics

    # If sending the message toAzure Loganalytics fails we would like to retry to send it again.
    # We would like to do it until we reached to the duration 
    def resend_message(documents_json, amount_of_documents, remaining_duration)
        if remaining_duration > 0
            @logger.info("Resending #{amount_of_documents} documents as log type #{@logstashLoganalyticsConfiguration.custom_log_table_name} to DataCollector API in #{@logstashLoganalyticsConfiguration.RETRANSMISSION_DELAY} seconds.")
            sleep @logstashLoganalyticsConfiguration.RETRANSMISSION_DELAY
            begin
                response = @client.post_data(documents_json)
                if is_successfully_posted(response)
                    @logger.info("Successfully sent #{amount_of_documents} logs into custom log analytics table[#{@logstashLoganalyticsConfiguration.custom_log_table_name}] after resending.")
                else
                    @logger.debug("Resending #{amount_of_documents} documents failed, will try to resend for #{(remaining_duration - @logstashLoganalyticsConfiguration.RETRANSMISSION_DELAY)}")
                    resend_message(documents_json, amount_of_documents, (remaining_duration - @logstashLoganalyticsConfiguration.RETRANSMISSION_DELAY))
                end
            rescue Exception => ex
                @logger.debug("Resending #{amount_of_documents} documents failed, will try to resend for #{(remaining_duration - @logstashLoganalyticsConfiguration.RETRANSMISSION_DELAY)}")
                resend_message(documents_json, amount_of_documents, (remaining_duration - @logstashLoganalyticsConfiguration.RETRANSMISSION_DELAY))
            end
        else 
            @logger.error("Could not resend #{amount_of_documents} documents, message is dropped.")
            @logger.trace("Documents (#{amount_of_documents}) dropped. [documents_json=#{documents_json}]")
        end
    end # def resend_message

    # We would like to change the amount of messages in the buffer (change_max_size)
    # We change the amount according to the Azure Loganalytics limitation and the amount of messages inserted to the buffer
    # in one sending window.
    # Meaning that if we reached the max amount we would like to increase it.
    # Else we would like to decrease it(to reduce latency for messages)
    def change_message_limit_size(amount_of_documents, documents_byte_size)
        new_buffer_size = @logstashLoganalyticsConfiguration.max_items
        average_document_size = documents_byte_size / amount_of_documents
        # If window is full we need to increase it 
        # "amount_of_documents" can be greater since buffer is not synchronized meaning 
        # that flush can occur after limit was reached.
        if  amount_of_documents >= @logstashLoganalyticsConfiguration.max_items
            # if doubling the size wouldn't exceed the API limit
            if ((2 * @logstashLoganalyticsConfiguration.max_items) * average_document_size) < @logstashLoganalyticsConfiguration.MAX_SIZE_BYTES
                new_buffer_size = 2 * @logstashLoganalyticsConfiguration.max_items
            else
                new_buffer_size = (@logstashLoganalyticsConfiguration.MAX_SIZE_BYTES / average_document_size) -1000
            end

        # We would like to decrease the window but not more then the MIN_MESSAGE_AMOUNT
        # We are trying to decrease it slowly to be able to send as much messages as we can in one window 
        elsif amount_of_documents < @logstashLoganalyticsConfiguration.max_items and  @logstashLoganalyticsConfiguration.max_items != [(@logstashLoganalyticsConfiguration.max_items - @logstashLoganalyticsConfiguration.decrease_factor) ,@logstashLoganalyticsConfiguration.MIN_MESSAGE_AMOUNT].max
            new_buffer_size = [(@logstashLoganalyticsConfiguration.max_items - @logstashLoganalyticsConfiguration.decrease_factor) ,@logstashLoganalyticsConfiguration.MIN_MESSAGE_AMOUNT].max
        end

        change_buffer_size(new_buffer_size)
    end # def change_message_limit_size

    # Receiving new_size as the new max buffer size.
    # Changing both the buffer, the configuration and logging as necessary
    def change_buffer_size(new_size)
        # Change buffer size only if it's needed(new size)
        if @buffer_config[:max_items] != new_size
            old_buffer_size = @buffer_config[:max_items]
            @buffer_config[:max_items] = new_size
            @logstashLoganalyticsConfiguration.max_items = new_size
            @logger.info("Changing buffer size.[configuration='#{old_buffer_size}' , new_size='#{new_size}']")
        else
            @logger.info("Buffer size wasn't changed.[configuration='#{old_buffer_size}' , new_size='#{new_size}']")
        end
    end # def change_buffer_size

    # Function to return if the response is OK or else
    def is_successfully_posted(response)
        return (response.code == 200) ? true : false
      end # def is_successfully_posted

end # LogStashAutoResizeBuffer