# encoding: utf-8
module LogStash; module Outputs; class MicrosoftSentinelOutputInternal
class LogstashLoganalyticsOutputConfiguration
    def initialize(client_app_Id, client_app_secret, tenant_id, data_collection_endpoint, dcr_immutable_id, dcr_stream_name, compress_data, create_sample_file, sample_file_path, logger, managed_identity)
		@client_app_Id = client_app_Id
        @client_app_secret = client_app_secret
        @tenant_id = tenant_id
        @data_collection_endpoint = data_collection_endpoint
        @dcr_immutable_id = dcr_immutable_id
        @dcr_stream_name = dcr_stream_name
        @logger = logger
        @compress_data = compress_data
        @create_sample_file = create_sample_file
        @sample_file_path = sample_file_path
        @managed_identity = managed_identity

	# Delay between each resending of a message
        @RETRANSMISSION_DELAY = 2
        @MIN_MESSAGE_AMOUNT = 100
        # Maximum of 1 MB per post to Log Analytics Data Collector API V2.
        # This is a size limit for a single post.
        # If the data from a single post that exceeds 1 MB, you should split it.
        @loganalytics_api_data_limit = 1 * 1024 * 1024

        # Taking 4K safety buffer
        @MAX_SIZE_BYTES = @loganalytics_api_data_limit - 10000

        @azure_clouds = {
            "AzureCloud" => {"aad" => "https://login.microsoftonline.com", "monitor" => "https://monitor.azure.com"},
            "AzureChinaCloud" => {"aad" => "https://login.chinacloudapi.cn", "monitor" => "https://monitor.azure.cn"},
            "AzureUSGovernment" => {"aad" => "https://login.microsoftonline.us", "monitor" => "https://monitor.azure.us"}
        }.freeze
    end

	def validate_configuration()
        if @create_sample_file
        begin
            if @sample_file_path.nil?
                print_missing_parameter_message_and_raise("sample_file_path")
            end
            if @sample_file_path.strip == ""
                raise ArgumentError, "The setting sample_file_path cannot be empty"
            end
            begin
                file = java.io.File.new(@sample_file_path)
                if !file.exists
                    raise "Path not exists"
                end
                rescue Exception
                    raise ArgumentError, "The path #{@sample_file_path} does not exist."
                end
            end
        else
            if @managed_identity
                required_configs = { "data_collection_endpoint" => @data_collection_endpoint,
                                    "dcr_immutable_id" => @dcr_immutable_id,
                                    "dcr_stream_name" => @dcr_stream_name }
            else
                required_configs = { "client_app_Id" => @client_app_Id,
                                    "client_app_secret" => @client_app_secret,
                                    "tenant_id" => @tenant_id,
                                    "data_collection_endpoint" => @data_collection_endpoint,
                                    "dcr_immutable_id" => @dcr_immutable_id,
                                    "dcr_stream_name" => @dcr_stream_name }
            end
        required_configs.each { |name, conf|
            if conf.nil?
                print_missing_parameter_message_and_raise(name)
            end
            if conf.empty?
                raise ArgumentError, "Malformed configuration , the following arguments can not be null or empty.[client_app_Id, client_app_secret, tenant_id, data_collection_endpoint, dcr_immutable_id, dcr_stream_name]"
            end
        }

        if @retransmission_time < 0
            raise ArgumentError, "retransmission_time must be a positive integer."
        end
        if @max_items < @MIN_MESSAGE_AMOUNT
            raise ArgumentError, "Setting max_items to value must be greater then #{@MIN_MESSAGE_AMOUNT}."
        end
        if @key_names.length > 500
            raise ArgumentError, 'There are over 500 key names listed to be included in the events sent to Azure Loganalytics, which exceeds the limit of columns that can be define in each table in log analytics.'
        end
        if !@azure_clouds.key?(@azure_cloud)
            raise ArgumentError, "The specified Azure cloud #{@azure_cloud} is not supported. Supported clouds are: #{@azure_clouds.keys.join(", ")}."
        end
    end
        @logger.info("Azure Loganalytics configuration was found valid.")
        # If all validation pass then configuration is valid
        return  true
    end # def validate_configuration


    def print_missing_parameter_message_and_raise(param_name)
        @logger.error("Missing a required setting for the microsoft-sentinel-log-analytics-logstash-output-plugin output plugin:
    output {
        microsoft-sentinel-log-analytics-logstash-output-plugin {
            #{param_name} => # SETTING MISSING
            ...
        }
    }
")
        raise ArgumentError, "The setting #{param_name} is required."
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

    def proxy_aad
        @proxy_aad
    end

    def proxy_endpoint
        @proxy_endpoint
    end

    def logger
        @logger
    end

    def decrease_factor
        @decrease_factor
    end

    def managed_identity
        @managed_identity
    end

    def client_app_Id
        @client_app_Id
    end

    def client_app_secret
        @client_app_secret
    end

    def tenant_id
        @tenant_id
    end

    def data_collection_endpoint
        @data_collection_endpoint
    end

    def dcr_immutable_id
        @dcr_immutable_id
    end

    def dcr_stream_name
        @dcr_stream_name
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

    def proxy_aad=(new_proxy_aad)
        @proxy_aad = new_proxy_aad
    end

    def proxy_endpoint=(new_proxy_endpoint)
        @proxy_endpoint = new_proxy_endpoint
    end

    def retransmission_time=(new_retransmission_time)
        @retransmission_time = new_retransmission_time
    end

    def compress_data
        @compress_data
    end

    def compress_data=(new_compress_data)
        @compress_data = new_compress_data
    end

    def create_sample_file
        @create_sample_file
    end

    def create_sample_file=(new_create_sample_file)
        @create_sample_file = new_create_sample_file
    end

    def sample_file_path
        @sample_file_path
    end

    def sample_file_path=(new_sample_file_path)
        @sample_file_path = new_sample_file_path
    end

    def azure_cloud
        @azure_cloud
    end

    def azure_cloud=(new_azure_cloud)
        @azure_cloud = new_azure_cloud
    end

    def get_aad_endpoint
        @azure_clouds[@azure_cloud]["aad"]
    end

    def get_monitor_endpoint
        @azure_clouds[@azure_cloud]["monitor"]
    end

end
end ;end ;end
