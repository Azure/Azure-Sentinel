Gem::Specification.new do |s|
  s.name = 'microsoft-sentinel-logstash-output-plugin'
  s.version = "1.0.1"
  s.authors = ["Microsoft Sentinel"]
  s.email   = 'AzureSentinel@microsoft.com'
  s.summary = %q{The plugin was renamed to microsoft-sentinel-log-analytics-logstash-output-plugin. microsoft-sentinel-logstash-output-plugin will no longer be maintained.}
  s.description = s.summary
  s.homepage = "https://github.com/Azure/Azure-Sentinel"
  s.licenses = ["MIT"]

  # Special flag to let us know this is actually a logstash plugin
  s.metadata = { "logstash_plugin" => "true", "logstash_group" => "output" }

end
