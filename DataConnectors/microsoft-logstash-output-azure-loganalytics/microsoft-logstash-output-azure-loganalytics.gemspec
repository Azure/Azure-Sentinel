Gem::Specification.new do |s|
  s.name = 'microsoft-logstash-output-azure-loganalytics'
  s.version    =  File.read("VERSION").strip
  s.authors = ["Ron Marsiano", "Haim Rubinstein"]
  s.email = "romarsia@outlook.com"
  s.summary = %q{Azure Sentinel provides a new output plugin for Logstash. Using this output plugin, you will be able to send any log you want using Logstash to the Azure Sentinel/Log Analytics workspace}
  s.description = s.summary
  s.homepage = "https://github.com/Azure/Azure-Sentinel"
  s.licenses = ["MIT"]
  s.require_paths = ["lib"]

  # Files
  s.files = Dir['lib/**/*','spec/**/*','vendor/**/*','*.gemspec','*.md','CONTRIBUTORS','Gemfile','LICENSE','NOTICE.TXT', 'VERSION']
   # Tests
  s.test_files = s.files.grep(%r{^(test|spec|features)/})

  # Special flag to let us know this is actually a logstash plugin
  s.metadata = { "logstash_plugin" => "true", "logstash_group" => "output" }

  # Gem dependencies
  s.add_runtime_dependency "rest-client", ">= 1.8.0"
  s.add_runtime_dependency "logstash-core-plugin-api", ">= 1.60", "<= 2.99"
  s.add_runtime_dependency "logstash-codec-plain"
  s.add_development_dependency "logstash-devutils"
end
