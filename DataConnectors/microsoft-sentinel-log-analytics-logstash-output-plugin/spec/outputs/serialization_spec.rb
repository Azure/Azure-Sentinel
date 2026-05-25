# encoding: utf-8
require "rspec"
require "json"

$LOAD_PATH.unshift(File.expand_path("../support", __dir__))

require "logstash/sentinel_la/logstashLoganalyticsConfiguration"
require "logstash/sentinel_la/logStashAutoResizeBuffer"

RSpec.describe LogStash::Outputs::MicrosoftSentinelOutputInternal::LogStashAutoResizeBuffer do
  let(:logger) do
    double("logger", warn: nil, trace: nil, info: nil, error: nil, debug: nil)
  end

  let(:config) do
    config = LogStash::Outputs::MicrosoftSentinelOutputInternal::LogstashLoganalyticsOutputConfiguration.new(
      "client_id",
      "client_secret",
      "tenant_id",
      "https://example.ingest.monitor.azure.com",
      "dcr-immutable-id",
      "Custom-Table",
      false,
      false,
      nil,
      logger,
      false,
      nil
    )

    config.key_names = []
    config.plugin_flush_interval = 1
    config.decrease_factor = 100
    config.amount_resizing = false
    config.max_items = 100
    config.retransmission_time = 1
    config.retransmission_delay = 1
    config.azure_cloud = "AzureCloud"

    config
  end

  let(:buffer) { described_class.new(config) }

  it "serializes numeric fields as JSON numbers" do
    payloads = []
    allow(buffer).to receive(:send_message_to_loganalytics) do |payload, _amount|
      payloads << payload
    end

    event_document = {
      "DestinationPort" => 443,
      "SentBytes" => 1296.0,
      "SourcePort" => 57456
    }

    buffer.flush([event_document])

    expect(payloads.length).to eq(1)

    parsed = LogStash::Json.load(payloads.first)
    first = parsed.first

    expect(first["DestinationPort"]).to be_a(Integer)
    expect(first["SentBytes"]).to be_a(Float)
    expect(first["SourcePort"]).to be_a(Integer)
  end
end
