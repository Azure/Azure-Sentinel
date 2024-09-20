# encoding: utf-8
class LogstashLoganalyticsOutputConfiguration
    def initialize(workspace_id, workspace_key, custom_log_table_name, logger)
        @workspace_id = workspace_id
        @workspace_key = workspace_key
        @custom_log_table_name = custom_log_table_name
        @logger = logger

        # Delay between each resending of a message
        @RETRANSMISSION_DELAY = 2
        @MIN_MESSAGE_AMOUNT = 100
        # Maximum of 30 MB per post to Log Analytics Data Collector API. 
        # This is a size limit for a single post. 
        # If the data from a single post that exceeds 30 MB, you should split it.
        @loganalytics_api_data_limit = 30 * 1000 * 1000

        # Taking 4K safety buffer
        @MAX_SIZE_BYTES = @loganalytics_api_data_limit - 10000
    end

    def validate_configuration()
        if @retransmission_time < 0
            raise ArgumentError, "Setting retransmission_time which sets the time spent for resending each failed messages must be positive integer. [retransmission_time=#{@retransmission_time}]." 
        
        elsif @max_items < @MIN_MESSAGE_AMOUNT
            raise ArgumentError, "Setting max_items to value must be greater then #{@MIN_MESSAGE_AMOUNT}."

        elsif @workspace_id.empty? or @workspace_key.empty? or @custom_log_table_name.empty? 
            raise ArgumentError, "Malformed configuration , the following arguments can not be null or empty.[workspace_id=#{@workspace_id} , workspace_key=#{@workspace_key} , custom_log_table_name=#{@custom_log_table_name}]"

        elsif not @custom_log_table_name.match(/^[[:alpha:][:digit:]_]+$/)
            raise ArgumentError, 'custom_log_table_name must be only alpha characters, numbers and underscore.'

        elsif @custom_log_table_name.length > 100
            raise ArgumentError, 'custom_log_table_name must not exceed 100 characters.'

        elsif custom_log_table_name.empty?
            raise ArgumentError, 'custom_log_table_name should not be empty.' 
            
        elsif @key_names.length > 500
            raise ArgumentError, 'Azure Loganalytics limits the amount of columns to 500 in each table.' 
        end

        @logger.info("Azure Loganalytics configuration was found valid.")
        
        # If all validation pass then configuration is valid 
        return  true
    end # def validate_configuration

    def azure_resource_id
        @azure_resource_id
    end

    def RETRANSMISSION_DELAY
        @RETRANSMISSION_DELAY
    end

    def MAX_SIZE_BYTES
        @MAX_SIZE_BYTES
    end

    def amount_resizing
        @amount_resizing
    end

    def retransmission_time
        @retransmission_time
    end

    def proxy
        @proxy
    end

    def logger
        @logger
    end

    def decrease_factor
        @decrease_factor
    end

    def workspace_id
        @workspace_id
    end

    def workspace_key
        @workspace_key
    end

    def custom_log_table_name
        @custom_log_table_name
    end

    def endpoint
        @endpoint
    end

    def time_generated_field
        @time_generated_field
    end

    def key_names
        @key_names
    end

    def max_items
        @max_items
    end

    def plugin_flush_interval
        @plugin_flush_interval
    end

    def MIN_MESSAGE_AMOUNT
        @MIN_MESSAGE_AMOUNT
    end
    
    def max_items=(new_max_items)
        @max_items = new_max_items
    end

    def endpoint=(new_endpoint)
        @endpoint = new_endpoint
    end

    def time_generated_field=(new_time_generated_field)
        @time_generated_field = new_time_generated_field
    end

    def key_names=(new_key_names)
        @key_names = new_key_names
    end

    def plugin_flush_interval=(new_plugin_flush_interval)
        @plugin_flush_interval = new_plugin_flush_interval
    end
    
    def decrease_factor=(new_decrease_factor)
        @decrease_factor = new_decrease_factor
    end

    def amount_resizing=(new_amount_resizing)
        @amount_resizing = new_amount_resizing
    end

    def max_items=(new_max_items)
        @max_items = new_max_items
    end
    
    def azure_resource_id=(new_azure_resource_id)
        @azure_resource_id = new_azure_resource_id
    end
    
    def proxy=(new_proxy)
        @proxy = new_proxy
    end

    def retransmission_time=(new_retransmission_time)
        @retransmission_time = new_retransmission_time
    end
end