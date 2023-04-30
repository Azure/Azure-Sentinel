# encoding: utf-8
require 'rest-client'
module LogStash; module Outputs; class MicrosoftSentinelOutputInternal
    class Utils
        def self.post_data_optional_proxy(url, body, headers, proxy)
            response = nil
            if proxy.nil?
                if ENV['http_proxy'].nil?
                    response = RestClient::Request.execute(method: :post, url: url, payload: body, headers: headers, proxy: nil)
                else 
                    response = RestClient::Request.execute(method: :post, url: url, payload: body, headers: headers, proxy: ENV['http_proxy'])
                end
            elsif proxy.empty?
                response = RestClient::Request.execute(method: :post, url: url, payload: body, headers: headers, proxy: nil)
            else
                response = RestClient::Request.execute(method: :post, url: url, payload: body, headers: headers, proxy: proxy)
            end
            return response
        end
    end
end ;end ;end 