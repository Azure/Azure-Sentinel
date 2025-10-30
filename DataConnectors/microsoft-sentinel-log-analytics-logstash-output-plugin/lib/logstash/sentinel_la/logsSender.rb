# encoding: utf-8
require "logstash/sentinel_la/logstashLoganalyticsConfiguration"
require "logstash/sentinel_la/eventsHandler"
require "logstash/sentinel_la/logStashAutoResizeBuffer"
require "logstash/sentinel_la/logStashCompressedStream"

module LogStash; module Outputs; class MicrosoftSentinelOutputInternal
        class LogsSender < EventsHandler

        @thread_batch_map

        def initialize(logstashLogAnalyticsConfiguration)
          @thread_batch_map = Concurrent::Hash.new
          @logstashLogAnalyticsConfiguration = logstashLogAnalyticsConfiguration
          @logger = logstashLogAnalyticsConfiguration.logger
          super
        end

        def handle_events(events)
          t = Thread.current
          
          unless @thread_batch_map.include?(t)
            @thread_batch_map[t] = @logstashLogAnalyticsConfiguration.compress_data ? 
                                      LogStashCompressedStream::new(@logstashLogAnalyticsConfiguration) :
                                      LogStashAutoResizeBuffer::new(@logstashLogAnalyticsConfiguration)
          end

          events.each do |event|
            # creating document from event
            document = create_event_document(event)

            # Skip if document doesn't contain any items
            next if (document.keys).length < 1

            @logger.trace("Adding event document - " + event.to_s)
            @thread_batch_map[t].batch_event_document(document)
          end
        end

        def close
          @thread_batch_map.each { |thread_id, batcher|
            batcher.close
          }
        end

      end
end; end; end;
