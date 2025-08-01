# Narrative DNA Commander - CLI Dashboard System

A comprehensive "Windows Commander" style terminal interface for managing narrative DNA attributes, essences, batch jobs, and system monitoring.

## 🎯 System Overview

The Narrative DNA Commander provides a complete toolkit for:
- **Narrative DNA extraction** from Project Gutenberg books
- **Text transformation** using extracted DNA attributes
- **Batch job management** with queue system
- **Real-time monitoring** and log viewing
- **Quantum narrative analysis** and comparison

## 🏗️ Architecture

```
┌─────────────────────┐    ┌─────────────────────┐    ┌─────────────────────┐
│   CLI Dashboard     │    │   Background Jobs   │    │   API Integration   │
│ narrative_dna_      │    │   job_daemon.sh     │    │  Enhanced Lighthouse│
│ commander.sh        │    │   dna_tools.sh      │    │   api_enhanced.py   │
└─────────────────────┘    └─────────────────────┘    └─────────────────────┘
         │                            │                           │
         ├─ Two-pane interface        ├─ Job queue system         ├─ DNA extraction
         ├─ Real-time navigation      ├─ Background processing    ├─ Text transformation
         ├─ Keyboard shortcuts        ├─ Log management           └─ Quantum analysis
         └─ Status monitoring         └─ Result tracking
```

## 🚀 Quick Start

### 1. Launch the System
```bash
cd /Users/tem/humanizer-lighthouse/scripts
./launcher.sh setup    # First-time setup
./launcher.sh status   # Check system status
```

### 2. Extract DNA Attributes
```bash
./launcher.sh extract                    # Extract from default books
./launcher.sh extract 1342 11 84 174     # Extract from specific books
```

### 3. Launch Commander Interface
```bash
./launcher.sh commander
```

### 4. Transform Text
```bash
./launcher.sh transform 'persona|namespace|style' 'Text to transform'
```

## 📋 Available Scripts

### 🎛️ launcher.sh - Central Control Hub
Main entry point for the entire system:

```bash
./launcher.sh setup           # Complete system setup
./launcher.sh start           # Start API and daemon
./launcher.sh stop            # Stop all services
./launcher.sh status          # System status overview
./launcher.sh commander       # Launch CLI dashboard
./launcher.sh extract [books] # Quick DNA extraction
./launcher.sh transform DNA TEXT # Quick text transformation
./launcher.sh attributes      # List available DNA
```

### 🖥️ narrative_dna_commander.sh - Interactive Dashboard
Windows Commander style interface with:

- **Two-pane layout** - Left (attributes/essences/results) / Right (jobs/logs/monitor)
- **Keyboard navigation** - Tab to switch panels, arrow keys to navigate
- **Real-time updates** - Live job status and system monitoring
- **Function key commands** - F1-F11 for various actions

**Key Features:**
- Browse and manage DNA attributes
- Monitor batch job lifecycles
- View real-time logs
- System resource monitoring
- Interactive job management

### 🔧 dna_tools.sh - Batch Processing Engine
Command-line utilities for DNA operations:

```bash
./dna_tools.sh list [format]        # List attributes (table/json/list/count)
./dna_tools.sh extract [book_ids]   # Extract DNA from books
./dna_tools.sh transform DNA TEXT   # Transform text using DNA
./dna_tools.sh process [job_file]   # Process specific job
./dna_tools.sh status               # Job queue status
./dna_tools.sh cleanup [days]       # Clean old files
```

### 🤖 job_daemon.sh - Background Processor
Daemon for automatic job processing:

```bash
./job_daemon.sh start      # Start background daemon
./job_daemon.sh stop       # Stop daemon
./job_daemon.sh status     # Show daemon status
./job_daemon.sh logs [n]   # Show recent activity
./job_daemon.sh tail       # Follow logs in real-time
./job_daemon.sh cleanup    # Clean old logs
```

## 🎮 Commander Interface Guide

### Navigation
- **TAB** - Switch between left and right panels
- **↑/↓ or j/k** - Navigate within panel
- **ENTER** - Select item
- **/** - Filter/search items
- **ESC** - Clear filter

### Panel Modes

#### Left Panel
- **F6** - Attributes mode (view DNA combinations)
- **F7** - Essences mode (view essence files)
- **F8** - Results mode (view generated files)

#### Right Panel
- **F9** - Jobs mode (manage batch jobs)
- **F10** - Logs mode (view job logs)
- **F11** - Monitor mode (system status)

### Actions
- **F1** - Show help
- **F2** - Extract DNA / Run job
- **F3** - Transform text / View details
- **F4** - Delete selected item
- **F5** - Refresh view
- **Q** - Quit

## 📁 Directory Structure

```
scripts/
├── launcher.sh                   # Main entry point
├── narrative_dna_commander.sh    # CLI dashboard
├── dna_tools.sh                  # Batch processing tools
├── job_daemon.sh                 # Background daemon
├── results/                      # Generated content
│   ├── attributes.json           # Extracted DNA attributes
│   ├── *_result.txt             # Transformation results
│   └── *.md                     # Analysis reports
├── logs/                         # System logs
│   ├── daemon.log               # Daemon activity
│   ├── commander.log            # Dashboard activity
│   └── *.log                    # Job-specific logs
└── queue/                        # Job queue
    └── *.job                    # Pending job files
```

## 🧬 DNA Format

Narrative DNA consists of three components:
```
persona|namespace|style
```

### Examples from Extracted Attributes:
- `philosophical_seafarer|maritime_existentialism|epic_philosophical_prose` (Moby Dick)
- `tragic_chorus|renaissance_tragedy|elizabethan_dramatic_verse` (Romeo & Juliet)
- `gothic_documenter|victorian_gothic_horror|gothic_realism` (Dracula)
- `cosmic_wanderer|philosophical_science_fiction|contemplative_prose` (Foundation)

## ⚙️ Configuration

### Environment Variables
```bash
# API Configuration
API_URL="http://localhost:8100"

# Directory Structure
RESULTS_DIR="./results"
LOGS_DIR="./logs"
QUEUE_DIR="./queue"

# Daemon Settings
POLL_INTERVAL=5
MAX_CONCURRENT_JOBS=3
```

### Job Queue Format
Jobs are JSON files in the queue directory:
```json
{
    "id": "extract_1234567890",
    "type": "dna_extraction",
    "created": "2025-07-28T12:34:56",
    "status": "pending",
    "books": [1342, 11, 84]
}
```

## 🔍 System Monitoring

### Real-time Status
- API server health check
- Background daemon status
- Job queue statistics
- Disk usage monitoring
- Active job tracking

### Logging System
- Centralized logging with timestamps
- Separate logs for each component
- Automatic log rotation
- Real-time log following

## 🚨 Troubleshooting

### Common Issues

1. **API Not Starting**
   ```bash
   cd ../humanizer_api/lighthouse
   source venv/bin/activate
   python api_enhanced.py
   ```

2. **Jobs Not Processing**
   ```bash
   ./job_daemon.sh restart
   ./job_daemon.sh logs
   ```

3. **No DNA Attributes Found**
   ```bash
   ./launcher.sh extract
   ./dna_tools.sh list
   ```

4. **Permission Errors**
   ```bash
   chmod +x *.sh
   ```

### Log Locations
- **Daemon logs**: `logs/daemon.log`
- **API logs**: `logs/api.log`
- **Job logs**: `logs/*.log`
- **Commander logs**: `logs/commander.log`

## 🎯 Advanced Usage

### Batch DNA Extraction
```bash
# Extract from multiple book sets
./dna_tools.sh extract 1342 11 84        # Classic literature
./dna_tools.sh extract 174 2701 345      # Science fiction
./dna_tools.sh extract 1661 76           # Adventure novels
```

### Automated Transformation Pipeline
```bash
# Queue multiple transformations
echo "Text 1" | ./dna_tools.sh transform 'persona1|namespace1|style1' -
echo "Text 2" | ./dna_tools.sh transform 'persona2|namespace2|style2' -
./job_daemon.sh status  # Monitor progress
```

### Quantum Analysis Integration
The system integrates with the quantum narrative analysis framework:
```bash
# Generate quantum analysis report
./launcher.sh tools process quantum_analysis_job.json
```

## 🔮 Future Enhancements

Planned features for future versions:
- **Neural network DNA prediction**
- **Collaborative filtering for DNA discovery**
- **Web interface integration**
- **Advanced visualization tools**
- **Multi-language support**
- **Cloud deployment options**

## 📖 Related Documentation

- [Quantum Narrative Theory](./quantum_analysis_report.md)
- [Gilgamesh Case Study](./gilgamesh_enhanced_20250728_004343/)
- [API Documentation](../humanizer_api/lighthouse/README.md)
- [Project Overview](../CLAUDE.md)

---

*Generated by Narrative DNA Commander System*  
*Quantum Narrative Theory in Practice*  
*Version 1.0.0 - 2025-07-28*