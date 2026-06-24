require 'sinatra'
require 'sqlite3'
require 'open-uri'
require 'erb'

# CWE-89: SQL Injection
get '/user' do
  id = params[:id]
  db = SQLite3::Database.new("database.db")
  results = db.execute("SELECT * FROM users WHERE id = '" + id + "'")
  results.to_s
end

# CWE-78: OS Command Injection
get '/ping' do
  host = params[:host]
  output = `ping -c 4 #{host}`
  output
end

# CWE-79: Reflected Cross-Site Scripting (XSS)
get '/greet' do
  name = params[:name]
  "<h1>Hello, #{name}!</h1>"
end

# CWE-918: Server-Side Request Forgery (SSRF)
get '/fetch' do
  url = params[:url]
  content = URI.open(url).read
  content
end

# CWE-22: Path Traversal
get '/file' do
  filename = params[:filename]
  File.read(filename)
end

# CWE-798: Hardcoded credentials
DB_PASSWORD = "SuperSecret123!"
API_TOKEN = "ghp_abc123def456ghi789"

get '/connect' do
  uri = URI("https://api.example.com/data")
  req = Net::HTTP::Get.new(uri)
  req["Authorization"] = "Bearer " + API_TOKEN
  Net::HTTP.start(uri.hostname, uri.port, use_ssl: true) do |http|
    response = http.request(req)
    response.body
  end
end

# CWE-502: Unsafe deserialization
get '/load' do
  data = params[:data]
  obj = Marshal.load(Base64.decode64(data))
  obj.to_s
end

# CWE-327: Weak cryptographic algorithm
get '/hash' do
  require 'digest'
  data = params[:data]
  Digest::MD5.hexdigest(data)
end
