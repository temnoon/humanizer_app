#!/bin/bash
#
# Unified Platform Startup Script
# One-command startup with dependency checking and initialization
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
COMPOSE_FILE="docker-compose.yml"
ENV_FILE=".env"
API_URL="http://localhost:8100"
TIMEOUT=60

echo -e "${BLUE}🚀 Starting Unified Humanizer Platform${NC}"
echo "=================================================="

# Check if Docker is running
check_docker() {
    echo -e "${BLUE}📋 Checking Docker...${NC}"
    if ! docker info > /dev/null 2>&1; then
        echo -e "${RED}❌ Docker is not running. Please start Docker first.${NC}"
        exit 1
    fi
    echo -e "${GREEN}✅ Docker is running${NC}"
}

# Check environment file
check_environment() {
    echo -e "${BLUE}📋 Checking environment configuration...${NC}"
    
    if [ ! -f "$ENV_FILE" ]; then
        echo -e "${YELLOW}⚠️  .env file not found. Creating from template...${NC}"
        cp .env.example .env
        echo -e "${YELLOW}📝 Please edit .env file with your API keys and configuration${NC}"
        echo "   Required settings:"
        echo "   - DATABASE_URL"
        echo "   - REDIS_URL" 
        echo "   - SECRET_KEY"
        echo "   - JWT_SECRET_KEY"
        echo "   - At least one LLM provider API key"
        echo ""
        read -p "Press Enter after configuring .env file..."
    fi
    
    echo -e "${GREEN}✅ Environment file found${NC}"
}

# Start services
start_services() {
    echo -e "${BLUE}🏗️  Starting services...${NC}"
    
    # Stop any existing containers
    echo "🛑 Stopping existing containers..."
    docker-compose down > /dev/null 2>&1 || true
    
    # Start in background
    echo "🚀 Starting unified platform..."
    docker-compose up -d
    
    echo -e "${GREEN}✅ Services started${NC}"
}

# Wait for services to be healthy
wait_for_services() {
    echo -e "${BLUE}⏳ Waiting for services to be ready...${NC}"
    
    # Function to check service health
    check_service() {
        local service=$1
        local url=$2
        local max_attempts=$3
        local attempt=1
        
        echo "  Checking $service..."
        
        while [ $attempt -le $max_attempts ]; do
            if curl -s "$url" > /dev/null 2>&1; then
                echo -e "  ${GREEN}✅ $service is ready${NC}"
                return 0
            fi
            
            echo "    Attempt $attempt/$max_attempts - waiting..."
            sleep 2
            attempt=$((attempt + 1))
        done
        
        echo -e "  ${RED}❌ $service failed to start${NC}"
        return 1
    }
    
    # Check services
    check_service "PostgreSQL" "http://localhost:5432" 15 || {
        echo -e "${RED}❌ Database failed to start${NC}"
        docker-compose logs db
        exit 1
    }
    
    check_service "Redis" "http://localhost:6379" 10 || {
        echo -e "${RED}❌ Redis failed to start${NC}"
        docker-compose logs redis
        exit 1
    }
    
    check_service "ChromaDB" "http://localhost:8001/api/v1/heartbeat" 15 || {
        echo -e "${RED}❌ ChromaDB failed to start${NC}"
        docker-compose logs chromadb
        exit 1
    }
    
    check_service "Unified API" "$API_URL/health" 30 || {
        echo -e "${RED}❌ API failed to start${NC}"
        docker-compose logs api
        exit 1
    }
    
    echo -e "${GREEN}✅ All services are ready!${NC}"
}

# Run initial setup
initial_setup() {
    echo -e "${BLUE}⚙️  Running initial setup...${NC}"
    
    # Run database migrations
    echo "📊 Running database migrations..."
    docker-compose exec -T api alembic upgrade head || {
        echo -e "${YELLOW}⚠️  Migration failed - database might need initialization${NC}"
    }
    
    # Test API endpoints
    echo "🧪 Testing API endpoints..."
    if curl -s "$API_URL/health" | grep -q "healthy"; then
        echo -e "${GREEN}✅ API health check passed${NC}"
    else
        echo -e "${YELLOW}⚠️  API health check failed${NC}"
    fi
    
    echo -e "${GREEN}✅ Initial setup completed${NC}"
}

# Show status and information
show_status() {
    echo ""
    echo "=================================================="
    echo -e "${GREEN}🎉 Unified Platform Started Successfully!${NC}"
    echo "=================================================="
    echo ""
    echo "📡 Services:"
    echo "  • Unified API:      $API_URL"
    echo "  • API Documentation: $API_URL/docs"
    echo "  • Health Check:     $API_URL/health"
    echo "  • Database:         localhost:5432"
    echo "  • Redis Cache:      localhost:6379"
    echo "  • Vector DB:        localhost:8001"
    echo ""
    echo "🧪 Quick Tests:"
    echo "  • Health:    curl $API_URL/health"
    echo "  • API Docs:  open $API_URL/docs"
    echo "  • Run Tests: python test_api.py"
    echo ""
    echo "📋 Management:"
    echo "  • View Logs:   docker-compose logs -f api"
    echo "  • Stop:        docker-compose down"
    echo "  • Restart:     docker-compose restart"
    echo ""
    echo "🔧 Debugging:"
    echo "  • Container Status: docker-compose ps"
    echo "  • Service Logs:     docker-compose logs [service]"
    echo "  • Enter Container:  docker-compose exec api bash"
    echo ""
}

# Run migration if requested
run_migration() {
    echo -e "${BLUE}📊 Running data migration from existing services...${NC}"
    
    if [ -f "migrations/migrate_from_existing.py" ]; then
        python migrations/migrate_from_existing.py
        echo -e "${GREEN}✅ Migration completed${NC}"
    else
        echo -e "${YELLOW}⚠️  Migration script not found${NC}"
    fi
}

# Main execution
main() {
    # Parse command line arguments
    MIGRATE=false
    FORCE=false
    
    for arg in "$@"; do
        case $arg in
            --migrate)
                MIGRATE=true
                shift
                ;;
            --force)
                FORCE=true
                shift
                ;;
            --help)
                echo "Usage: $0 [options]"
                echo ""
                echo "Options:"
                echo "  --migrate    Run data migration from existing services"
                echo "  --force      Force restart even if services are running"
                echo "  --help       Show this help message"
                echo ""
                exit 0
                ;;
        esac
    done
    
    # Check if already running (unless force)
    if [ "$FORCE" = false ] && curl -s "$API_URL/health" > /dev/null 2>&1; then
        echo -e "${YELLOW}⚠️  Platform appears to be already running${NC}"
        echo "Use --force to restart anyway"
        show_status
        exit 0
    fi
    
    # Run startup sequence
    check_docker
    check_environment
    start_services
    wait_for_services
    initial_setup
    
    # Run migration if requested
    if [ "$MIGRATE" = true ]; then
        run_migration
    fi
    
    # Show final status
    show_status
    
    echo -e "${GREEN}Ready for production! 🚀${NC}"
}

# Run main function
main "$@"