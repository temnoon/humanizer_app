#!/usr/bin/env python3
"""
Humanizer API - Main Launcher & Status Dashboard

Centralized launcher for the complete Humanizer API ecosystem with 
status monitoring and service management.
"""

import os
import sys
import time
import json
import asyncio
import argparse
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

import httpx
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.live import Live
from rich.layout import Layout
from rich.text import Text

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

try:
    from config import get_config
    CONFIG_AVAILABLE = True
except ImportError:
    CONFIG_AVAILABLE = False

console = Console()

class HumanizerAPIManager:
    """Main manager for the Humanizer API ecosystem"""
    
    def __init__(self):
        self.config = get_config() if CONFIG_AVAILABLE else None
        self.services = {
            "archive_api": {
                "name": "Archive API",
                "port": self.config.api.archive_api_port if self.config else 7200,
                "script": "src/archive_api.py",
                "description": "Universal content ingestion and semantic search",
                "icon": "📚"
            },
            "lpe_api": {
                "name": "LPE API", 
                "port": self.config.api.lpe_api_port if self.config else 7201,
                "script": "src/lpe_api.py",
                "description": "Multi-engine content transformation",
                "icon": "🧠"
            }
        }
        
        self.http_client = httpx.AsyncClient(timeout=5.0)
    
    async def check_service_health(self, service_name: str) -> Dict:
        """Check health of a specific service"""
        service = self.services[service_name]
        port = service["port"]
        
        try:
            response = await self.http_client.get(f"http://localhost:{port}/health")
            if response.status_code == 200:
                health_data = response.json()
                return {
                    "status": "healthy",
                    "response_time": response.elapsed.total_seconds() * 1000,
                    "details": health_data
                }
            else:
                return {
                    "status": "unhealthy",
                    "error": f"HTTP {response.status_code}"
                }
        except Exception as e:
            return {
                "status": "offline",
                "error": str(e)
            }
    
    async def get_service_stats(self, service_name: str) -> Dict:
        """Get statistics from a service"""
        service = self.services[service_name]
        port = service["port"]
        
        try:
            response = await self.http_client.get(f"http://localhost:{port}/stats")
            if response.status_code == 200:
                return response.json()
            else:
                return {}
        except Exception:
            return {}
    
    def create_status_table(self, health_data: Dict) -> Table:
        """Create a status table for services"""
        table = Table(title="🌐 Humanizer API Services")
        
        table.add_column("Service", style="cyan", no_wrap=True)
        table.add_column("Status", style="bold")
        table.add_column("Port", justify="center")
        table.add_column("Response", justify="right")
        table.add_column("Description", style="dim")
        
        for service_name, service in self.services.items():
            health = health_data.get(service_name, {"status": "unknown"})
            
            # Status styling
            if health["status"] == "healthy":
                status = "[green]●[/green] Healthy"
                response_time = f"{health.get('response_time', 0):.0f}ms"
            elif health["status"] == "unhealthy":
                status = "[yellow]●[/yellow] Unhealthy"
                response_time = health.get('error', 'Unknown')
            else:
                status = "[red]●[/red] Offline"
                response_time = health.get('error', 'Connection failed')
            
            table.add_row(
                f"{service['icon']} {service['name']}",
                status,
                str(service['port']),
                response_time,
                service['description']
            )
        
        return table
    
    def create_stats_panel(self, stats_data: Dict) -> Panel:
        """Create a statistics panel"""
        content = []
        
        for service_name, stats in stats_data.items():
            if stats:
                service = self.services[service_name]
                content.append(f"{service['icon']} {service['name']}:")
                
                if service_name == "archive_api":
                    content.append(f"  • Total Items: {stats.get('total_items', 0)}")
                    content.append(f"  • Sources: {len(stats.get('sources', {}))}")
                    content.append(f"  • Content Types: {len(stats.get('content_types', {}))}")
                elif service_name == "lpe_api":
                    content.append(f"  • Total Sessions: {stats.get('total_sessions', 0)}")
                    content.append(f"  • Total Operations: {stats.get('total_operations', 0)}")
                    content.append(f"  • Engines: {stats.get('available_engines', 0)}")
                
                content.append("")
        
        return Panel(
            "\n".join(content) if content else "No statistics available",
            title="📊 Service Statistics",
            border_style="blue"
        )
    
    async def status_dashboard(self):
        """Display real-time status dashboard"""
        console.print(Panel.fit(
            "🚀 Humanizer API Ecosystem Dashboard\n"
            "Real-time monitoring of all services",
            style="bold green"
        ))
        
        def create_layout():
            layout = Layout()
            layout.split_column(
                Layout(name="header", size=3),
                Layout(name="main"),
                Layout(name="footer", size=3)
            )
            layout["main"].split_row(
                Layout(name="services"),
                Layout(name="stats")
            )
            return layout
        
        layout = create_layout()
        
        with Live(layout, refresh_per_second=2, screen=True):
            while True:
                # Update header
                layout["header"].update(Panel(
                    f"[bold]Humanizer API Dashboard[/bold] - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                    style="blue"
                ))
                
                # Check service health
                health_data = {}
                stats_data = {}
                
                for service_name in self.services:
                    health_data[service_name] = await self.check_service_health(service_name)
                    if health_data[service_name]["status"] == "healthy":
                        stats_data[service_name] = await self.get_service_stats(service_name)
                
                # Update main content
                layout["services"].update(self.create_status_table(health_data))
                layout["stats"].update(self.create_stats_panel(stats_data))
                
                # Update footer
                healthy_count = sum(1 for h in health_data.values() if h["status"] == "healthy")
                total_services = len(self.services)
                
                footer_text = f"Services: {healthy_count}/{total_services} healthy | "
                footer_text += "Press Ctrl+C to exit | "
                footer_text += f"Config: {'✅' if CONFIG_AVAILABLE else '❌'}"
                
                layout["footer"].update(Panel(
                    footer_text,
                    style="dim"
                ))
                
                await asyncio.sleep(2)
    
    def start_service(self, service_name: str) -> bool:
        """Start a specific service"""
        if service_name not in self.services:
            console.print(f"❌ Unknown service: {service_name}")
            return False
        
        service = self.services[service_name]
        console.print(f"🚀 Starting {service['name']}...")
        
        try:
            # Start the service
            cmd = [sys.executable, service['script']]
            subprocess.Popen(cmd, cwd=Path.cwd())
            
            console.print(f"✅ {service['name']} started on port {service['port']}")
            return True
            
        except Exception as e:
            console.print(f"❌ Failed to start {service['name']}: {e}")
            return False
    
    def show_quick_status(self):
        """Show a quick status check"""
        console.print("🔍 Checking Humanizer API services...")
        
        async def check_all():
            health_data = {}
            for service_name in self.services:
                health_data[service_name] = await self.check_service_health(service_name)
            
            table = self.create_status_table(health_data)
            console.print(table)
            
            # Show quick stats
            console.print("\n📊 Quick Stats:")
            for service_name in self.services:
                if health_data[service_name]["status"] == "healthy":
                    stats = await self.get_service_stats(service_name)
                    service = self.services[service_name]
                    if stats:
                        console.print(f"  {service['icon']} {service['name']}: {list(stats.keys())[:3]}")
            
            # Show useful URLs
            console.print("\n🔗 Useful URLs:")
            for service_name, service in self.services.items():
                if health_data[service_name]["status"] == "healthy":
                    console.print(f"  {service['icon']} {service['name']}: http://localhost:{service['port']}/docs")
        
        asyncio.run(check_all())

async def main():
    parser = argparse.ArgumentParser(description="Humanizer API Manager")
    parser.add_argument("command", nargs="?", choices=["status", "dashboard", "start"], 
                       default="status", help="Command to execute")
    parser.add_argument("--service", help="Specific service to start")
    
    args = parser.parse_args()
    
    manager = HumanizerAPIManager()
    
    if args.command == "dashboard":
        try:
            await manager.status_dashboard()
        except KeyboardInterrupt:
            console.print("\n👋 Dashboard stopped")
    
    elif args.command == "start":
        if args.service:
            manager.start_service(args.service)
        else:
            console.print("🚀 Starting all services...")
            for service_name in manager.services:
                manager.start_service(service_name)
                time.sleep(2)  # Stagger startup
    
    else:  # status
        manager.show_quick_status()

if __name__ == "__main__":
    if len(sys.argv) == 1:
        # No arguments - show help and quick status
        console.print(Panel.fit(
            "🌐 Humanizer API Ecosystem Manager\n\n"
            "Commands:\n"
            "  python main.py status     - Quick status check\n"
            "  python main.py dashboard  - Real-time dashboard\n"
            "  python main.py start      - Start all services\n\n"
            "Scripts:\n"
            "  ./setup.sh                - Initial setup\n"
            "  ./start_humanizer_api.sh  - Start ecosystem\n"
            "  ./stop_humanizer_api.sh   - Stop all services",
            title="Help",
            border_style="cyan"
        ))
        
        # Show quick status
        manager = HumanizerAPIManager()
        manager.show_quick_status()
    else:
        asyncio.run(main())
