#!/usr/bin/env ruby

# Integration test for Rails + Python API
# Run this after starting both Rails (port 3001) and Python (port 5000) servers

require 'net/http'
require 'json'

puts "🔗 Testing Rails + Python Integration"
puts "===================================="

# Test configuration
RAILS_URL = 'http://localhost:3001'
PYTHON_URL = 'http://localhost:5000'

def test_endpoint(url, description)
  print "🧪 Testing #{description}... "
  
  begin
    uri = URI(url)
    response = Net::HTTP.get_response(uri)
    
    if response.code == '200'
      puts "✅ SUCCESS"
      return true
    else
      puts "❌ FAILED (HTTP #{response.code})"
      return false
    end
  rescue => e
    puts "❌ ERROR: #{e.message}"
    return false
  end
end

def test_post_endpoint(url, data, description)
  print "🧪 Testing #{description}... "
  
  begin
    uri = URI(url)
    http = Net::HTTP.new(uri.host, uri.port)
    request = Net::HTTP::Post.new(uri)
    request['Content-Type'] = 'application/json'
    request.body = data.to_json
    
    response = http.request(request)
    
    if response.code == '200' || response.code == '201'
      puts "✅ SUCCESS"
      return true
    else
      puts "❌ FAILED (HTTP #{response.code})"
      puts "   Response: #{response.body[0..100]}..."
      return false
    end
  rescue => e
    puts "❌ ERROR: #{e.message}"
    return false
  end
end

# Test Rails endpoints
puts "\n📡 Testing Rails API (#{RAILS_URL})"
puts "-" * 40

rails_tests = [
  ["#{RAILS_URL}/llm_tasks", "LLM Tasks listing"],
  ["#{RAILS_URL}/writebooks", "Writebooks listing"],
  ["#{RAILS_URL}/llm_tasks/stats", "LLM Tasks statistics"]
]

rails_success = 0
rails_tests.each do |url, desc|
  rails_success += 1 if test_endpoint(url, desc)
end

# Test Rails POST endpoints
test_llm_task = {
  llm_task: {
    task_type: 'test',
    model_name: 'test-model',
    prompt: 'Integration test prompt',
    result_status: 'completed'
  }
}

test_writebook = {
  writebook: {
    title: 'Integration Test Book',
    version: '1.0',
    author: 'Test Author'
  }
}

rails_success += 1 if test_post_endpoint("#{RAILS_URL}/llm_tasks", test_llm_task, "LLM Task creation")
rails_success += 1 if test_post_endpoint("#{RAILS_URL}/writebooks", test_writebook, "Writebook creation")

# Test Python API
puts "\n🐍 Testing Python API (#{PYTHON_URL})"
puts "-" * 40

python_tests = [
  ["#{PYTHON_URL}/status", "Python API status"]
]

python_success = 0
python_tests.each do |url, desc|
  python_success += 1 if test_endpoint(url, desc)
end

# Test Rails → Python bridge
puts "\n🌉 Testing Rails → Python Bridge"
puts "-" * 40

bridge_test_data = {
  text: "This is a test of the humanization bridge",
  style: "academic"
}

bridge_success = 0
bridge_success += 1 if test_post_endpoint("#{RAILS_URL}/api/v1/archive/humanize", bridge_test_data, "Rails → Python humanize bridge")

# Summary
puts "\n📊 Integration Test Results"
puts "=" * 40
puts "Rails API:        #{rails_success}/#{rails_tests.length + 2} tests passed"
puts "Python API:       #{python_success}/#{python_tests.length} tests passed"
puts "Rails → Python:   #{bridge_success}/1 tests passed"

total_tests = rails_tests.length + 2 + python_tests.length + 1
total_success = rails_success + python_success + bridge_success

puts "\nOverall:          #{total_success}/#{total_tests} tests passed"

if total_success == total_tests
  puts "\n🎉 All integration tests PASSED!"
  puts "   Your Rails and Python APIs are working together correctly."
else
  puts "\n⚠️  Some tests failed. Check that both servers are running:"
  puts "   Rails:  bundle exec rails server -p 3001"
  puts "   Python: (your Python startup command)"
end

puts "\n📋 Next steps:"
puts "1. Point your React frontend to Rails endpoints"
puts "2. Gradually migrate functionality from Python to Rails"
puts "3. Monitor LLM task logging in Rails database"
