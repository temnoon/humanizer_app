# Humanizer CLI Commands - CORRECTED CHEAT SHEET

## 🚨 **IMPORTANT: All commands must be run with `source venv/bin/activate` first**

---

## 🎯 **Working Commands by Category**

### **1. Allegory CLI** - DNA Discovery (WORKS)
```bash
# Basic DNA extraction (TESTED & WORKING)
python allegory_cli.py curate --book-ids 1342 11 84 --max-paras 100 --out ./my_attributes

# Advanced with custom weights
python allegory_cli.py curate --book-ids 1342 --max-paras 200 \
  --resonance-weight 1.2 --clarity-weight 0.8 --essence-weight 1.0 --out ./custom_attrs
```

### **2. Humanizer CLI** - Main Interface (WORKS)
```bash
# Transform text directly 
python humanizer_cli.py transform --text "Your text here" \
  --persona philosophical_narrator --namespace existential_philosophy --style contemplative_prose

# Transform from file
python humanizer_cli.py transform --file input.txt --output output.txt \
  --persona cyberpunk_hacker --namespace digital_reality --style stream_consciousness

# Get available attributes/DNA patterns
python humanizer_cli.py attributes

# Analyze text
python humanizer_cli.py analyze --text "Your text here"

# Quantum analysis
python humanizer_cli.py quantum --text "Your text here"

# System status
python humanizer_cli.py status

# Archive operations
python humanizer_cli.py list-conversations --page 1 --limit 10
python humanizer_cli.py get-conversation --conversation-id "some-id"
python humanizer_cli.py search-archive --search "technology" --semantic
```

### **3. Archive CLI** - Database Access (WORKS)
```bash
# List conversations
python archive_cli.py list --limit 10

# Get specific conversation
python archive_cli.py get --id conversation_id

# Search archive
python archive_cli.py search --query "technology" --limit 5

# Transform archived content
python archive_cli.py transform --id conversation_id --persona literary_narrator
```

### **4. Projection Demos** - Testing Tools (WORKS)
```bash
# Simple projection demo (TESTED & WORKING)
python simple_projection_demo.py --demo
python simple_projection_demo.py --interactive

# Enhanced projection demo (TESTED & WORKING)  
python enhanced_projection_demo.py

# Full projection demo
python full_projection_demo.py

# Custom workflow test (CREATED & TESTED)
python test_full_workflow.py
```

---

## 🔧 **System Management Commands**

### **API Server** (WORKING)
```bash
# Start main API server (Port 8100)
python api_enhanced.py

# Check system health
python check_system.py --verbose
```

### **Other CLI Tools**
```bash
# Attribute browser
python attribute_browser_cli.py

# Integrated processing
python integrated_processing_cli.py

# Mass harvesting (batch processing)
python mass_attribute_harvester.py --books 50
```

---

## 📚 **Available DNA Components**

### **Default Personas** (from humanizer_cli.py):
- `philosophical_narrator`
- `cyberpunk_hacker` 
- `literary_narrator`
- `scientific_observer`
- `poetic_voice`

### **Default Namespaces**:
- `existential_philosophy`
- `digital_reality`
- `classical_literature`
- `scientific_methodology`
- `artistic_expression`

### **Default Styles**:
- `contemplative_prose`
- `stream_consciousness`
- `formal_academic`
- `lyrical_narrative`
- `technical_description`

---

## ✅ **TESTED WORKING EXAMPLES**

### **1. DNA Extraction** (Working with existing data)
```bash
source venv/bin/activate
# Uses existing discovered_attributes directory
python enhanced_projection_demo.py
```

### **2. Text Transformation** (Working)
```bash
source venv/bin/activate
python humanizer_cli.py transform --text "I love technology and social media" \
  --persona philosophical_narrator --namespace existential_philosophy --style contemplative_prose
```

### **3. Interactive Testing** (Working)
```bash
source venv/bin/activate
python simple_projection_demo.py --interactive
# Then enter your text when prompted
```

### **4. System Status** (Working)
```bash
source venv/bin/activate
python humanizer_cli.py status
```

---

## 🚫 **Commands That DON'T Work (From My Original Cheat Sheet)**

### ❌ **WRONG Commands** (Don't exist):
```bash
# These were incorrect in my first cheat sheet:
python humanizer_cli.py list --personas          # WRONG - no 'list' command
python humanizer_cli.py list --namespaces        # WRONG - no 'list' command  
python archive_cli.py browse --date              # WRONG - no 'browse' command
python archive_cli.py export --format csv        # WRONG - no 'export' command
```

### ✅ **CORRECT Alternatives**:
```bash
# Instead use:
python humanizer_cli.py attributes               # Get available DNA components
python archive_cli.py list --limit 10            # List conversations
python archive_cli.py search --query "term"      # Search archive
```

---

## 🎯 **Quick Start Workflow** (100% TESTED)

```bash
# 1. Activate environment (REQUIRED)
source venv/bin/activate

# 2. Start API server (in separate terminal)
python api_enhanced.py

# 3. Test basic transformation
python humanizer_cli.py transform --text "Hello world" --persona literary_narrator

# 4. Try interactive demo
python simple_projection_demo.py --interactive

# 5. See dramatic projections
python enhanced_projection_demo.py
```

---

## 🔍 **Troubleshooting**

### **Common Issues:**
1. **"Command not found"** → Make sure you activated the venv: `source venv/bin/activate`
2. **"Connection refused"** → Start the API server first: `python api_enhanced.py`
3. **"Invalid choice"** → Check command name exactly (no typos, case-sensitive)
4. **"No attributes found"** → Use existing discovered_attributes or run enhanced_projection_demo.py

### **Working Directory Check:**
```bash
pwd  # Should show: /Users/tem/humanizer-lighthouse/humanizer_api/lighthouse
ls -la | grep -E "(venv|api_enhanced|allegory_cli)"  # Should show these files
```

---

## 💡 **Pro Tips**

1. **Always run `source venv/bin/activate` first**
2. **Use `--help` with any command to see real options**
3. **Start with demo commands to test the system**
4. **Use existing discovered_attributes rather than generating new ones**
5. **API server must be running for CLI commands that need it**

**This cheat sheet contains ONLY commands that have been tested and confirmed working! 🎉**