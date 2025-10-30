# encoding: utf-8
require "logstash/sentinel_la/logstashLoganalyticsConfiguration"

module LogStash
  module Outputs
    class MicrosoftSentinelOutputInternal
      class EventsHandler

        def initialize(logstashLogAnalyticsConfiguration)
          @logstashLogAnalyticsConfiguration = logstashLogAnalyticsConfiguration
          @logger = logstashLogAnalyticsConfiguration.logger
          @key_names = logstashLogAnalyticsConfiguration.key_names
          @columns_to_modify = {"@timestamp" => "ls_timestamp", "@version" => "ls_version"}
        end

        def handle_events(events)
          raise "Method handle_events not implemented"
        end

        def close
          raise "Method close not implemented"
        end

        # In case that the user has defined key_names meaning that he would like to a subset of the data,
        # we would like to insert only those keys.
        # If no keys were defined we will send all the data
        def create_event_document(event)
          document = {}
          event_hash = event.to_hash

          @columns_to_modify.each {|original_key, new_key|
            if event_hash.has_key?(original_key)
              event_hash[new_key] = event_hash[original_key]
              event_hash.delete(original_key)
            end
          }

          if @key_names.length > 0
            # Get the intersection of key_names and keys of event_hash
            keys_intersection = @key_names & event_hash.keys
            keys_intersection.each do |key|
              document[key] = event_hash[key]
            end
            if document.keys.length < 1
              @logger.warn("No keys found, message is dropped. Plugin keys: #{@key_names}, Event keys: #{event_hash}. The event message do not match event expected structre. Please edit key_names section in output plugin and try again.")
            end
          else
            document = event_hash
          end

          return document
        end
        # def create_event_document

      end
    end
  end
end
