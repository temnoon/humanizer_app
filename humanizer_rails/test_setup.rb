# Test script to verify Rails setup
# Run with: ruby test_setup.rb

puts "🧪 Testing Humanizer Rails Setup"
puts "================================"

# Test 1: Check if we can load Rails
begin
  require_relative 'config/environment'
  puts "✅ Rails environment loaded successfully"
rescue => e
  puts "❌ Failed to load Rails environment: #{e.message}"
  exit 1
end

# Test 2: Check database connection
begin
  ActiveRecord::Base.connection.execute("SELECT 1")
  puts "✅ Database connection working"
rescue => e
  puts "❌ Database connection failed: #{e.message}"
  puts "   Try running: bundle exec rails db:create db:migrate"
end

# Test 3: Check models can be loaded
begin
  LlmTask
  Writebook
  WritebookSection
  puts "✅ All models loaded successfully"
rescue => e
  puts "❌ Model loading failed: #{e.message}"
end

# Test 4: Check ArchiveClient
begin
  require_relative 'app/services/archive_client'
  puts "✅ ArchiveClient service loaded"
rescue => e
  puts "❌ ArchiveClient failed to load: #{e.message}"
end

# Test 5: Create sample records
begin
  # Create a test LLM task
  task = LlmTask.create!(
    task_type: 'test',
    model_name: 'test-model',
    prompt: 'Test prompt',
    result_status: 'completed',
    output: 'Test output'
  )
  
  # Create a test writebook
  book = Writebook.create!(
    title: 'Test Book',
    version: '1.0',
    author: 'Test Author'
  )
  
  # Create a test section
  section = book.writebook_sections.create!(
    title: 'Test Section',
    content: 'Test content'
  )
  
  puts "✅ Sample records created successfully"
  puts "   - LLM Task ID: #{task.id}"
  puts "   - Writebook ID: #{book.id}"
  puts "   - Section ID: #{section.id}"
  
  # Clean up
  task.destroy
  book.destroy
  
rescue => e
  puts "❌ Failed to create sample records: #{e.message}"
end

puts ""
puts "🎉 Setup verification complete!"
puts "📋 To start the server: bundle exec rails server -p 3001"
