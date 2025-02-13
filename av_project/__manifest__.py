# -*- coding: utf-8 -*- 
{
    "name": "Av Project",
    "summary": "Alliance Virunga Project Management with Department Integration",
    "version": "17.0.1.0.0",
    'description': """
        Alliance Virunga Project Management Application
        
        Key Features:
        * Department and Manager Integration
        * Project Budget Tracking
        * Purchase Order Integration
        * Enhanced Date Management
        * Automated Validations
        
        This module extends Odoo's project management functionality to better suit
        Alliance Virunga's specific needs by adding department management,
        financial tracking, and purchase order integration capabilities.
    """,
    "name": "Av Project",
    "summary": "Alliance Virunga Project Management with Department Integration",
    "version": "17.0.1.0.0",
    'description': """
        Alliance Virunga Project Management Application
        
        Key Features:
        * Department and Manager Integration
        * Project Budget Tracking
        * Purchase Order Integration
        * Enhanced Date Management
        * Automated Validations
        
        This module extends Odoo's project management functionality to better suit
        Alliance Virunga's specific needs by adding department management,
        financial tracking, and purchase order integration capabilities.
    """,
    'author': "Virunga Foundation",
    "license": "OPL-1",
    "license": "OPL-1",
    "depends": [
        "project",  # Base project management
        "purchase", # For purchase order integration
        "hr",       # For department integration
    ],
    "application": False,
    "application": False,
    "data": [
        # Security
        'security/project_security.xml',
        'security/project_security.xml',
        
        # Views
        'views/project_views.xml',
        'views/project_views.xml',
        
        # Data
        
    ],
    "assets": {
        "web.assets_backend": [
            "av_project/static/src/components/*"
        ]
    },
    "installable": True,
    "category": "Project Management",
    "maintainer": "Virunga Foundation",
    "website": "https://virunga.org",
    "assets": {
        "web.assets_backend": [
            "av_project/static/src/components/*"
        ]
    },
    "installable": True,
    "category": "Project Management",
    "maintainer": "Virunga Foundation",
    "website": "https://virunga.org",
}
