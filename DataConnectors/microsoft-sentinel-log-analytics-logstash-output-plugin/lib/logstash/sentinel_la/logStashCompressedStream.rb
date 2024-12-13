# encoding: utf-8

require "logstash/sentinel_la/logstashLoganalyticsConfiguration"
require "logstash/sentinel_la/customSizeBasedBuffer"
require "logstash/sentinel_la/logStashEventsBatcher"
require 'zlib'

module LogStash; module Outputs; class MicrosoftSentinelOutputInternal
    class LogStashCompressedStream < LogStashEventsBatcher
        include CustomSizeBasedBuffer
        #This is a basic memory based buffer with size and time bounds
        #Events are compressed when entering the buffer.
        def initialize(logstashLoganalyticsConfiguration)
            @compression_buffer = StringIO.new
            @deflater = Zlib::Deflate.new
            
            @compression_stream_state = {
                :events_in_compression_buffer => 0,
                :original_events_size => 0,
                :last_flush => Time.now.to_i,
                # guarding the flush
                :flush_mutex => Mutex.new,
                # guarding the stream
                :insert_mutex => Mutex.new               
            }

            buffer_initialize(
                :max_items => logstashLoganalyticsConfiguration.max_items,
                :max_interval => logstashLoganalyticsConfiguration.plugin_flush_interval,
                :logger => logstashLoganalyticsConfiguration.logger,
                :flush_each => logstashLoganalyticsConfiguration.MAX_SIZE_BYTES - 1000
              )
            super
        end # initialize
  
        public
        # Adding an event document into the buffer
        def batch_event(event_document)        
            buffer_receive(event_document)
        end # def batch_event

        def flush (documents, close=false)
            @compression_stream_state[:insert_mutex].synchronize do
                documents.each do |document|
                    add_event_to_compression_buffer(document)
                end
            end
        end

        def close
            buffer_flush(:final => true)
            flush_compression_buffer(:final => true)
        end

        protected        
        def get_time_since_last_flush
          Time.now.to_i - @compression_stream_state[:last_flush]
        end

        # This override is to pickup on forced flushes, for example when timer is firing
        def buffer_flush(options={})
            super
            if options[:force]
                @compression_stream_state[:insert_mutex].synchronize do
                    flush_compression_buffer(:force => true)
                end
            end
        end

        # Adding an event document into the compressed stream
        private
        def add_event_to_compression_buffer(event_document)
            event_json = event_document.to_json
               
            # Ensure that adding the current event to the stream will not exceed the maximum size allowed. 
            # If so, first flush and clear the current stream and then add the current record to the new stream instance.
            if event_json.bytesize + @deflater.total_out > @buffer_config[:flush_each]
                flush_compression_buffer
            end

            buffer_empty? ? write_string_to_compression_buffer("[") :
                            write_string_to_compression_buffer(",")
            
            write_string_to_compression_buffer(event_json)
            @compression_stream_state[:events_in_compression_buffer] += 1
            @compression_stream_state[:original_events_size] += event_json.bytesize        
        end
        
        def write_string_to_compression_buffer(string_to_compress)
            @compression_buffer << @deflater.deflate(string_to_compress, Zlib::SYNC_FLUSH)
        end

        def buffer_empty?
            @compression_stream_state[:events_in_compression_buffer] == 0
        end

        def flush_compression_buffer(options={})
            # logstash service is shutting down, flush all pending logs
            final = options[:final] 
            # Force is passed when the timer fires - ensure the stream will flush every x seconds
            force = options[:force]

            # there might be more than one thread trying to flush concurrently 
            if final
                # final flush will wait for lock, so we are sure to flush out all buffered events
                @compression_stream_state[:flush_mutex].lock
            elsif ! @compression_stream_state[:flush_mutex].try_lock # failed to get lock, another flush already in progress
                return 
            end
            
            begin
                time_since_last_flush = get_time_since_last_flush

                if buffer_empty? || 
                    (get_time_since_last_flush < @buffer_config[:max_interval] && force && (!final))
                    @logger.trace("flushing aborted. buffer_empty? #{buffer_empty?} time_since_last_flush #{time_since_last_flush} force #{force} final #{final}")
                    return
                end

                write_string_to_compression_buffer("]")
                @compression_buffer.flush
                outgoing_data = @compression_buffer.string
                
                number_outgoing_events = @compression_stream_state[:events_in_compression_buffer]
                @logger.trace("about to send [#{@compression_stream_state[:events_in_compression_buffer]}] events. Compressed data byte size [#{outgoing_data.bytesize}] Original data byte size [#{@compression_stream_state[:original_events_size]}].")

                reset_compression_stream
                
                send_message_to_loganalytics(outgoing_data, number_outgoing_events)
            ensure
                @compression_stream_state[:flush_mutex].unlock
            end
        end

        def reset_compression_stream                            
            @deflater.reset
            @compression_buffer.reopen("")
            @compression_stream_state[:events_in_compression_buffer] = 0
            @compression_stream_state[:original_events_size] = 0
            @compression_stream_state[:last_flush] = Time.now.to_i
        end        

    end
end;end;end;