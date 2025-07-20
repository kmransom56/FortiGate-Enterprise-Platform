# Create FastAPI application with lifespan events
app = FastAPI(
    title="FortiGate Network Monitor Pro API",
    description="Enterprise Device Intelligence Platform with automated security responses",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    lifespan=lifespan
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(devices.router, prefix="/api/v1/devices", tags=["devices"])
app.include_router(scanning.router, prefix="/api/v1/scanning", tags=["scanning"])
app.include_router(vulnerabilities.router, prefix="/api/v1/vulnerabilities", tags=["vulnerabilities"])

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "service": "FortiGate Network Monitor Pro API",
        "version": "1.0.0",
        "status": "active",
        "timestamp": datetime.utcnow().isoformat(),
        "docs": "/api/docs"
    }

@app.get("/api/health")
async def health_check():
    """Health check endpoint for monitoring"""
    global intelligence_engine
    
    engine_status = "healthy" if intelligence_engine and intelligence_engine.is_ready() else "initializing"
    
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "components": {
            "api": "healthy",
            "intelligence_engine": engine_status,
            "database": "healthy"  # Will be updated with actual DB check
        }
    }

def get_intelligence_engine() -> DeviceIntelligenceEngine:
    """Dependency to get the intelligence engine instance"""
    global intelligence_engine
    if not intelligence_engine:
        raise HTTPException(status_code=503, detail="Intelligence engine not ready")
    return intelligence_engine
