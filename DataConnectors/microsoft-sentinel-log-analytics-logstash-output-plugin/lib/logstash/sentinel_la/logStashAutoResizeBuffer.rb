# encoding: utf-8

require "logstash/sentinel_la/logstashLoganalyticsConfiguration"
require "logstash/sentinel_la/customSizeBasedBuffer"
require "logstash/sentinel_la/logStashEventsBatcher"

# LogStashAutoResizeBuffer class setting a resizable buffer which is flushed periodically
# The buffer resize itself according to Azure Loganalytics  and configuration limitations
# This buffer will increase and decrease size according to the amount of messages inserted.
# If the buffer reached the max amount of messages the amount will be increased until the limit
module LogStash; module Outputs; class MicrosoftSentinelOutputInternal
class LogStashAutoResizeBuffer < LogStashEventsBatcher
    include CustomSizeBasedBuffer

    def initialize(logstashLoganalyticsConfiguration)
        buffer_initialize(
          :max_items => logstashLoganalyticsConfiguration.max_items,
          :max_interval => logstashLoganalyticsConfiguration.plugin_flush_interval,
          :logger => logstashLoganalyticsConfiguration.logger,
          #todo: There is a small discrepancy between the total size of the documents and the message body 
          :flush_each => logstashLoganalyticsConfiguration.MAX_SIZE_BYTES - 2000
        )
        super
    end # initialize

    # Public methods
    public

    # Adding an event document into the buffer
    def batch_event(event_document)        
        buffer_receive(event_document)
    end # def batch_event

    # Flushing all buffer content to Azure Loganalytics.
    # Called from Stud::Buffer#buffer_flush when there are events to flush
    def flush (documents, close=false)
        # Skip in case there are no candidate documents to deliver
        if documents.length < 1
            @logger.warn("No documents in batch for log type #{@logstashLoganalyticsConfiguration.dcr_stream_name}. Skipping")
            return
        end

        # We send Json in the REST request 
        documents_json = documents.to_json
        documents_byte_size = documents_json.bytesize
        if (documents_byte_size <= @logstashLoganalyticsConfiguration.MAX_SIZE_BYTES)
        # Setting resizing to true will cause changing the max size
            if @logstashLoganalyticsConfiguration.amount_resizing == true
                # Resizing the amount of messages according to size of message received and amount of messages
                    change_message_limit_size(documents.length, documents_byte_size)
            end
            send_message_to_loganalytics(documents_json, documents.length)
        else
            warn_documents_size_over_limitation(documents, documents_byte_size)
            split_documents_lists = split_document_list_to_sublists_by_max_size(documents, documents_byte_size)
            @logger.trace("Number of documents: #{documents.length}, Number of split lists to send separately: #{split_documents_lists.length}");
            send_split_documents_list_to_loganalytics(split_documents_lists)
        end
    end # def flush

    def close
        buffer_flush(:final => true)
    end

    # Private methods 
    private 

    def warn_documents_size_over_limitation(documents, documents_byte_size)
        average_document_size = documents_byte_size / documents.length
        recommended_max_items = (@buffer_config[:flush_each] / average_document_size).floor
        
        if @logstashLoganalyticsConfiguration.amount_resizing == true
            change_buffer_size(recommended_max_items)
        else 
            @logger.info("Warning: The size of the batch to post (#{documents_byte_size} bytes) is higher than the maximum allowed to post (#{@logstashLoganalyticsConfiguration.MAX_SIZE_BYTES}).")
        end

    end
    # This will convert our documents list into a list of sublists. Each sublist size will be lower than the max allowed size, and will be posted separately, in order to avoid the endpoint failing the request due to size limitation..
    def split_document_list_to_sublists_by_max_size(all_documents, documents_byte_size)
        number_of_sublists = (documents_byte_size.to_f / @logstashLoganalyticsConfiguration.MAX_SIZE_BYTES.to_f).ceil # If max size is 1MB and actual size is 2.5MB - this will return 3.
        split_documents_lists = all_documents.each_slice((all_documents.size/number_of_sublists.to_f).round).to_a
        final_documents_lists = Array.new

        for documents_sublist in split_documents_lists do
            documents_sublist_byte_size = documents_sublist.to_json.bytesize

            if (documents_sublist_byte_size >= @logstashLoganalyticsConfiguration.MAX_SIZE_BYTES)
                if (documents_sublist.length > 1)
                    final_documents_lists.concat(split_document_list_to_sublists_by_max_size(documents_sublist, documents_sublist_byte_size))
                else
                    @logger.error("Received document above the max allowed size - dropping the document [document size: #{current_document_size}, max allowed size: #{@logstashLoganalyticsConfiguration.MAX_SIZE_BYTES}")
                end
            else
                final_documents_lists.push(documents_sublist)
            end
        end

        return final_documents_lists
    end

    def send_split_documents_list_to_loganalytics(split_documents_lists)
        for documents in split_documents_lists do
            send_message_to_loganalytics(documents.to_json, documents.length)
        end
    end
   
    # We would like to change the amount of messages in the buffer (change_max_size)
    # We change the amount according to the Azure Loganalytics limitation and the amount of messages inserted to the buffer
    # in one sending window.
    # Meaning that if we reached the max amount we would like to increase it.
    # Else we would like to decrease it(to reduce latency for messages)
    def change_message_limit_size(amount_of_documents, documents_byte_size)
        current_buffer_size = @buffer_config[:max_items]
        new_buffer_size = current_buffer_size 
        average_document_size = documents_byte_size / amount_of_documents

        # If window is full we need to increase it 
        # "amount_of_documents" can be greater since buffer is not synchronized meaning 
        # that flush can occur after limit was reached.
        if  amount_of_documents >= current_buffer_size
            # if doubling the size wouldn't exceed the API limit
            if ((2 * current_buffer_size) * average_document_size) < @buffer_config[:flush_each]
                new_buffer_size = 2 * current_buffer_size
            # If doubling the size will exceed the API limit, change it to be as close as possible to the API limit (minus 4kb just to be safe) - but don't cause it to decrease
            else
                average_documents_in_4kb = (average_document_size / 4000).ceil
                potential_new_buffer_size = (@buffer_config[:flush_each] / average_document_size) -average_documents_in_4kb
                if potential_new_buffer_size > new_buffer_size
                    new_buffer_size = potential_new_buffer_size
                end
            end

        # We would like to decrease the window but not more then the MIN_MESSAGE_AMOUNT
        # We are trying to decrease it slowly to be able to send as much messages as we can in one window 
        elsif amount_of_documents < current_buffer_size and  current_buffer_size != [(current_buffer_size - @logstashLoganalyticsConfiguration.decrease_factor) ,@logstashLoganalyticsConfiguration.MIN_MESSAGE_AMOUNT].max
            new_buffer_size = [(current_buffer_size - @logstashLoganalyticsConfiguration.decrease_factor) ,@logstashLoganalyticsConfiguration.MIN_MESSAGE_AMOUNT].max
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
            @logger.trace("Changing buffer size.[configuration='#{old_buffer_size}' , new_size='#{new_size}']")
        else
            @logger.trace("Buffer size wasn't changed.[configuration='#{old_buffer_size}' , new_size='#{new_size}']")
        end
    end # def change_buffer_size

end # LogStashAutoResizeBuffer
end ;end ;end 