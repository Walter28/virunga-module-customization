# -*- coding: utf-8 -*- 
{
    "name":"Av Project",
    "summary":"Alliance Virunga Project App",
    "version":"17.0.1.0.0",
    'description': "Alliance Virunga Project App",
    'author': "Virunga Foundation",
    "license":"OPL-1",
    "depends": [
        "project",  # Base project management
        "hr",       # For department integration
    ],
    "application":False,
    "data": [
        # Security
        'security/project_project_security.xml',
        'security/ir.model.access.csv',
        
        # Views
        'views/project_project_views.xml',
        
        # Data
        
    ],
    "installable": True
}
