"""
CLI API for HAW Command Execution
=================================

API to execute HAW CLI commands from the React interface with proper
subprocess handling, timeout management, and output streaming.
"""

import os
import subprocess
import logging
import asyncio
from datetime import datetime
from typing import Dict, Any, Optional, List
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

class CLICommandRequest(BaseModel):
    """Request model for CLI command execution."""
    command: str = Field(..., description="The command to execute")
    working_directory: Optional[str] = Field(
        default="/Users/tem/humanizer-lighthouse", 
        description="Working directory for command execution"
    )
    timeout: Optional[int] = Field(
        default=300, 
        description="Timeout in seconds (default: 5 minutes)"
    )
    capture_output: bool = Field(
        default=True, 
        description="Whether to capture command output"
    )

class CLICommandResponse(BaseModel):
    """Response model for CLI command execution."""
    command: str
    output: str
    error: str
    return_code: int
    execution_time_ms: int
    timestamp: str
    working_directory: str

class CLIBatchRequest(BaseModel):
    """Request model for batch command execution."""
    commands: List[str] = Field(..., description="List of commands to execute")
    working_directory: Optional[str] = Field(
        default="/Users/tem/humanizer-lighthouse", 
        description="Working directory for command execution"
    )
    timeout_per_command: Optional[int] = Field(
        default=300, 
        description="Timeout per command in seconds"
    )
    continue_on_error: bool = Field(
        default=True, 
        description="Whether to continue if a command fails"
    )

class CLIBatchResponse(BaseModel):
    """Response model for batch command execution."""
    commands: List[CLICommandResponse]
    total_execution_time_ms: int
    successful_commands: int
    failed_commands: int
    timestamp: str

# Router for CLI endpoints
cli_router = APIRouter(prefix="/api/cli", tags=["cli"])

class CLICommandExecutor:
    """
    Handles execution of CLI commands with proper security and error handling.
    """
    
    def __init__(self):
        self.base_directory = "/Users/tem/humanizer-lighthouse"
        self.allowed_commands = {
            "haw": True,
            "./haw": True,
            "python": True,
            "pip": True,
            "ls": True,
            "pwd": True,
            "cd": True,
            "which": True,
            "ps": True,
            "lsof": True,
            "git": True,
            "npm": True,
            "curl": True,
            "echo": True,
            "cat": True,
            "head": True,
            "tail": True,
            "grep": True,
            "find": True,
            "wc": True
        }
    
    def is_command_allowed(self, command: str) -> bool:
        """
        Check if a command is allowed to be executed.
        """
        # Split command to get the base command
        parts = command.strip().split()
        if not parts:
            return False
        
        base_cmd = parts[0]
        
        # Check if base command is in allowed list
        if base_cmd in self.allowed_commands:
            return True
        
        # Special handling for HAW commands
        if base_cmd == "haw" or command.startswith("./haw"):
            return True
        
        # Allow python scripts in the project directory
        if base_cmd == "python" and len(parts) > 1:
            script_path = parts[1]
            if not script_path.startswith("/") and not script_path.startswith(".."):
                return True
        
        return False
    
    def sanitize_working_directory(self, working_dir: str) -> str:
        """
        Ensure working directory is safe and within allowed bounds.
        """
        # Resolve to absolute path
        abs_path = os.path.abspath(working_dir)
        
        # Must be within the humanizer-lighthouse directory or subdirectory
        if not abs_path.startswith(self.base_directory):
            logger.warning(f"Working directory {abs_path} not allowed, using base directory")
            return self.base_directory
        
        # Must exist
        if not os.path.exists(abs_path):
            logger.warning(f"Working directory {abs_path} does not exist, using base directory")
            return self.base_directory
        
        return abs_path
    
    async def execute_command(self, request: CLICommandRequest) -> CLICommandResponse:
        """
        Execute a single command with proper error handling and timeout.
        """
        start_time = datetime.now()
        
        # Validate command
        if not self.is_command_allowed(request.command):
            raise HTTPException(
                status_code=403, 
                detail=f"Command not allowed: {request.command.split()[0] if request.command.split() else 'empty'}"
            )
        
        # Sanitize working directory
        working_dir = self.sanitize_working_directory(request.working_directory)
        
        logger.info(f"Executing command: {request.command} in {working_dir}")
        
        try:
            # Execute command
            process = subprocess.run(
                request.command,
                shell=True,
                cwd=working_dir,
                capture_output=request.capture_output,
                text=True,
                timeout=request.timeout,
                env=dict(os.environ, **{
                    "PYTHONPATH": f"{working_dir}:{os.environ.get('PYTHONPATH', '')}",
                    "PATH": f"{working_dir}:{os.environ.get('PATH', '')}"
                })
            )
            
            output = process.stdout or ""
            error = process.stderr or ""
            return_code = process.returncode
            
        except subprocess.TimeoutExpired:
            output = ""
            error = f"Command timed out after {request.timeout} seconds"
            return_code = 124  # Standard timeout exit code
            logger.warning(f"Command timed out: {request.command}")
            
        except subprocess.CalledProcessError as e:
            output = e.stdout or ""
            error = e.stderr or str(e)
            return_code = e.returncode
            logger.warning(f"Command failed with exit code {return_code}: {request.command}")
            
        except Exception as e:
            output = ""
            error = f"Execution error: {str(e)}"
            return_code = 1
            logger.error(f"Command execution failed: {request.command} - {e}")
        
        end_time = datetime.now()
        execution_time_ms = int((end_time - start_time).total_seconds() * 1000)
        
        return CLICommandResponse(
            command=request.command,
            output=output,
            error=error,
            return_code=return_code,
            execution_time_ms=execution_time_ms,
            timestamp=start_time.isoformat(),
            working_directory=working_dir
        )
    
    async def execute_batch(self, request: CLIBatchRequest) -> CLIBatchResponse:
        """
        Execute multiple commands in sequence.
        """
        start_time = datetime.now()
        results = []
        successful = 0
        failed = 0
        
        for command in request.commands:
            try:
                cmd_request = CLICommandRequest(
                    command=command,
                    working_directory=request.working_directory,
                    timeout=request.timeout_per_command
                )
                
                result = await self.execute_command(cmd_request)
                results.append(result)
                
                if result.return_code == 0:
                    successful += 1
                else:
                    failed += 1
                    if not request.continue_on_error:
                        logger.info(f"Stopping batch execution due to failed command: {command}")
                        break
                        
            except Exception as e:
                logger.error(f"Failed to execute command in batch: {command} - {e}")
                failed += 1
                if not request.continue_on_error:
                    break
        
        end_time = datetime.now()
        total_time_ms = int((end_time - start_time).total_seconds() * 1000)
        
        return CLIBatchResponse(
            commands=results,
            total_execution_time_ms=total_time_ms,
            successful_commands=successful,
            failed_commands=failed,
            timestamp=start_time.isoformat()
        )

# Global executor instance
cli_executor = CLICommandExecutor()

@cli_router.post("/execute", response_model=CLICommandResponse)
async def execute_cli_command(request: CLICommandRequest):
    """
    Execute a single CLI command.
    
    Supports HAW commands and other whitelisted system commands.
    Includes timeout handling and proper error reporting.
    """
    return await cli_executor.execute_command(request)

@cli_router.post("/batch", response_model=CLIBatchResponse)
async def execute_cli_batch(request: CLIBatchRequest):
    """
    Execute multiple CLI commands in sequence.
    
    Useful for running complex workflows that require multiple steps.
    Can continue on errors or stop at first failure.
    """
    return await cli_executor.execute_batch(request)

@cli_router.get("/allowed-commands")
async def get_allowed_commands():
    """
    Get list of allowed command prefixes for security reference.
    """
    return {
        "allowed_commands": list(cli_executor.allowed_commands.keys()),
        "base_directory": cli_executor.base_directory,
        "security_note": "Only whitelisted commands are allowed for security"
    }

@cli_router.get("/working-directory")
async def get_working_directory():
    """
    Get current working directory information.
    """
    return {
        "base_directory": cli_executor.base_directory,
        "current_directory": os.getcwd(),
        "exists": os.path.exists(cli_executor.base_directory),
        "is_git_repo": os.path.exists(os.path.join(cli_executor.base_directory, ".git"))
    }

@cli_router.get("/haw-help")
async def get_haw_help():
    """
    Get HAW command help information for quick reference.
    """
    return {
        "system_commands": [
            {"command": "haw status", "description": "Complete system health check"},
            {"command": "haw processes", "description": "Show active humanizer processes"},
            {"command": "haw logs", "description": "View recent log activity"},
            {"command": "haw setup", "description": "Setup/repair Python environment"}
        ],
        "content_discovery": [
            {"command": "haw browse-notebooks list", "description": "List all conversations"},
            {"command": "haw browse-notebooks browse", "description": "Interactive browsing"},
            {"command": "haw browse-notebooks analyze 123", "description": "Analyze specific conversation"},
            {"command": "haw browse-writing summary", "description": "Writing pattern summary"},
            {"command": "haw browse-wordclouds search consciousness", "description": "Search word clouds"}
        ],
        "book_generation": [
            {"command": "haw curate-book analyze", "description": "Quick thematic analysis"},
            {"command": "haw explore-themes", "description": "System capabilities overview"},
            {"command": "haw advanced-books --analyze-only", "description": "Preview book generation"},
            {"command": "haw advanced-books --min-quality 0.4 --max-books 3", "description": "Generate high-quality books"},
            {"command": "haw universal-books --source-type notebooks", "description": "Universal book generator"},
            {"command": "haw book-editor", "description": "AI editorial assistant"},
            {"command": "haw book-pipeline --quality-threshold 0.3", "description": "Full automated pipeline"}
        ],
        "content_extraction": [
            {"command": "haw extract-writing extract --limit 1000", "description": "Extract writing patterns"}
        ]
    }

# Function to add CLI routes to the main FastAPI app
def add_cli_routes(app):
    """Add CLI routes to the FastAPI application."""
    app.include_router(cli_router)