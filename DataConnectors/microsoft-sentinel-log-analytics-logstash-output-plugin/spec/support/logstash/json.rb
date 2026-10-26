# encoding: utf-8
require "json"

# Minimal LogStash::Json shim for specs to avoid loading logstash-core.
module LogStash
  module Json
    def self.dump(obj)
      JSON.generate(obj)
    end

    def self.load(json)
      JSON.parse(json)
    end
  end
end
