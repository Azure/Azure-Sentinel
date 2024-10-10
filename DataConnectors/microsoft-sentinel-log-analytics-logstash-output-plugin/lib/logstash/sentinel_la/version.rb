module LogStash; module Outputs;
class MicrosoftSentinelOutputInternal
  VERSION_INFO = [1, 1, 3].freeze
  VERSION = VERSION_INFO.map(&:to_s).join('.').freeze

  def self.version
    VERSION
  end
end
end;end