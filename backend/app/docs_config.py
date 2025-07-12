"""
Documentation Configuration for Hive API

This module configures advanced OpenAPI documentation features,
custom CSS styling, and additional documentation endpoints.
"""

from fastapi.openapi.utils import get_openapi
from typing import Dict, Any


def custom_openapi_schema(app) -> Dict[str, Any]:
    """
    Generate custom OpenAPI schema with enhanced metadata.
    
    Args:
        app: FastAPI application instance
        
    Returns:
        Dict containing the custom OpenAPI schema
    """
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
        servers=app.servers
    )
    
    # Add custom extensions
    openapi_schema["info"]["x-logo"] = {
        "url": "https://hive.home.deepblack.cloud/static/hive-logo.png",
        "altText": "Hive Logo"
    }
    
    # Add contact information
    openapi_schema["info"]["contact"] = {
        "name": "Hive Development Team",
        "url": "https://hive.home.deepblack.cloud/contact",
        "email": "hive-support@deepblack.cloud"
    }
    
    # Add authentication schemes
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "JWT authentication token"
        },
        "ApiKeyAuth": {
            "type": "apiKey",
            "in": "header", 
            "name": "X-API-Key",
            "description": "API key for service-to-service authentication"
        }
    }
    
    # Add security requirements globally
    openapi_schema["security"] = [
        {"BearerAuth": []},
        {"ApiKeyAuth": []}
    ]
    
    # Add external documentation links
    openapi_schema["externalDocs"] = {
        "description": "Hive Documentation Portal",
        "url": "https://hive.home.deepblack.cloud/docs"
    }
    
    # Enhance tag descriptions
    if "tags" not in openapi_schema:
        openapi_schema["tags"] = []
    
    # Add comprehensive tag metadata
    tag_metadata = [
        {
            "name": "health",
            "description": "System health monitoring and status endpoints",
            "externalDocs": {
                "description": "Health Check Guide",
                "url": "https://hive.home.deepblack.cloud/docs/health-monitoring"
            }
        },
        {
            "name": "authentication", 
            "description": "User authentication and authorization operations",
            "externalDocs": {
                "description": "Authentication Guide",
                "url": "https://hive.home.deepblack.cloud/docs/authentication"
            }
        },
        {
            "name": "agents",
            "description": "Ollama agent management and registration",
            "externalDocs": {
                "description": "Agent Management Guide", 
                "url": "https://hive.home.deepblack.cloud/docs/agent-management"
            }
        },
        {
            "name": "cli-agents",
            "description": "CLI-based agent management (Google Gemini, etc.)",
            "externalDocs": {
                "description": "CLI Agent Guide",
                "url": "https://hive.home.deepblack.cloud/docs/cli-agents"
            }
        },
        {
            "name": "tasks",
            "description": "Task creation, management, and execution",
            "externalDocs": {
                "description": "Task Management Guide",
                "url": "https://hive.home.deepblack.cloud/docs/task-management"
            }
        },
        {
            "name": "workflows",
            "description": "Multi-agent workflow orchestration", 
            "externalDocs": {
                "description": "Workflow Guide",
                "url": "https://hive.home.deepblack.cloud/docs/workflows"
            }
        }
    ]
    
    openapi_schema["tags"] = tag_metadata
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema


# Custom CSS for Swagger UI
SWAGGER_UI_CSS = """
/* Hive Custom Swagger UI Styling */
.swagger-ui .topbar {
    background-color: #1a1a2e;
    border-bottom: 2px solid #16213e;
}

.swagger-ui .topbar .download-url-wrapper {
    display: none;
}

.swagger-ui .info {
    margin: 50px 0;
}

.swagger-ui .info .title {
    color: #16213e;
    font-family: 'Arial', sans-serif;
}

.swagger-ui .scheme-container {
    background: #fafafa;
    border: 1px solid #e3e3e3;
    border-radius: 4px;
    margin: 0 0 20px 0;
    padding: 30px 0;
}

.swagger-ui .opblock.opblock-get .opblock-summary-method {
    background: #61affe;
}

.swagger-ui .opblock.opblock-post .opblock-summary-method {
    background: #49cc90;
}

.swagger-ui .opblock.opblock-put .opblock-summary-method {
    background: #fca130;
}

.swagger-ui .opblock.opblock-delete .opblock-summary-method {
    background: #f93e3e;
}

/* Custom header styling */
.swagger-ui .info .title small {
    background: #89bf04;
    color: white;
    padding: 2px 8px;
    border-radius: 4px;
    font-size: 12px;
    margin-left: 10px;
}

/* Response schema styling */
.swagger-ui .model-box {
    background: #f7f7f7;
    border: 1px solid #e3e3e3;
    border-radius: 4px;
}

.swagger-ui .model .model-title {
    color: #3b4151;
    font-size: 16px;
    font-weight: 600;
}

/* Error response styling */
.swagger-ui .response .response-col_status {
    font-weight: 700;
}

.swagger-ui .response .response-col_status.response-undocumented {
    color: #999;
}

/* Tag section styling */
.swagger-ui .opblock-tag {
    border-bottom: 2px solid #e3e3e3;
    color: #3b4151;
    font-family: 'Arial', sans-serif;
    font-size: 24px;
    margin: 0 0 20px 0;
    padding: 20px 0 5px 0;
}

.swagger-ui .opblock-tag small {
    color: #999;
    font-size: 14px;
    font-weight: normal;
}

/* Parameter styling */
.swagger-ui .parameter__name {
    color: #3b4151;
    font-weight: 600;
}

.swagger-ui .parameter__type {
    color: #999;
    font-size: 12px;
    font-weight: 400;
}

.swagger-ui .parameter__in {
    color: #888;
    font-size: 12px;
    font-style: italic;
}
"""

# Custom JavaScript for enhanced functionality
SWAGGER_UI_JS = """
// Custom Swagger UI enhancements
window.onload = function() {
    // Add custom behaviors here
    console.log('Hive API Documentation loaded');
    
    // Add version badge
    const title = document.querySelector('.info .title');
    if (title && !title.querySelector('.version-badge')) {
        const versionBadge = document.createElement('small');
        versionBadge.className = 'version-badge';
        versionBadge.textContent = 'v1.1.0';
        title.appendChild(versionBadge);
    }
};
"""