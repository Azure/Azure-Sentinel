require File.expand_path('../lib/logstash/sentinel_la/version', __FILE__)

Gem::Specification.new do |s|
  s.name = 'microsoft-sentinel-log-analytics-logstash-output-plugin'
  s.version = LogStash::Outputs::MicrosoftSentinelOutputInternal::VERSION
  s.authors = ["Microsoft Sentinel"]
  s.email   = 'AzureSentinel@microsoft.com'
  s.summary = %q{Microsoft Sentinel provides a new output plugin for Logstash. Use this output plugin to send any log via Logstash to the Microsoft Sentinel/Log Analytics workspace. This is done with the Log Analytics DCR-based API.}
  s.description = s.summary
  s.homepage = "https://github.com/Azure/Azure-Sentinel"
  s.licenses = ["MIT"]
  s.require_paths = ["lib"]

  # Files
  s.files = Dir['lib/**/*','spec/**/*','vendor/**/*','*.gemspec','*.md','CONTRIBUTORS','Gemfile','LICENSE','NOTICE.TXT']
   # Tests
  s.test_files = s.files.grep(%r{^(test|spec|features)/})

  # Special flag to let us know this is actually a logstash plugin
  s.metadata = { "logstash_plugin" => "true", "logstash_group" => "output" }

  # Gem dependencies
  s.add_runtime_dependency "rest-client", ">= 2.1.0"
  s.add_runtime_dependency "logstash-core-plugin-api", ">= 1.60", "<= 2.99"
  s.add_runtime_dependency "logstash-codec-plain"
  s.add_development_dependency "logstash-devutils"
end
