# encoding: utf-8
require "logstash/sentinel_la/logstashLoganalyticsConfiguration"
require "logstash/sentinel_la/eventsHandler"

module LogStash
  module Outputs
    class MicrosoftSentinelOutputInternal
      class SampleFileCreator < EventsHandler

        def initialize(logstashLogAnalyticsConfiguration)
          @events_buffer = Concurrent::Array.new
          @maximum_events_to_sample = 10
          @was_file_written = false
          @writing_mutex = Mutex.new
          super
        end

        def handle_events(events)
          events.each do |event|
            if !@was_file_written
              filtered_event = create_event_document(event)
              @events_buffer.push(filtered_event)
            end
          end
          try_writing_events_to_file
        end

        def close
          try_writing_events_to_file(true)
        end

        def try_writing_events_to_file(force = false)
          if @was_file_written
            return
          end

          @writing_mutex.synchronize do
            #check if file was written during the wait
            if @was_file_written ||
               @events_buffer.length == 0 ||
               (@events_buffer.length <= @maximum_events_to_sample && !force) 
              return
            end

            output_path = @logstashLogAnalyticsConfiguration.sample_file_path
            output_file_name = "sampleFile#{Time.now.to_i}.json"
            file = java.io.File.new(output_path,output_file_name)
            fw = java.io.FileWriter.new(file)
            fw.write(@events_buffer.take(@maximum_events_to_sample).to_json)
            fw.flush
            fw.close

            @was_file_written = true
            @logger.info("Sample file was written in path: #{file.getAbsolutePath}")
          end
        end

      end
    end
  end
end
