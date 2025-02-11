# -*- coding: utf-8 -*- 
{
    "name": "Av Purchase",
    "summary": "Alliance Virunga Purchase App",
    "version": "17.0.1.0.0",
    'description': """
        Alliance Virunga Purchase Management Application
        
        Key Features:
        * Custom Purchase Workflow
        * CP Team Integration
        * Enhanced Approval Process
        * Department-based Purchase Management
    """,
    'author': "Virunga Foundation",
    "license": "OPL-1",
    "depends": ["av_project","purchase","web","base"],
    "application": False,
    "data": [
        # Security
        'security/security.xml',
        'security/purchase_security.xml',
        'security/ir.model.access.csv',
        
        # Views
        'views/purchase_views.xml',
        
        # Data
        'data/hr_data.xml',
    ],
    "assets": {
        "web.assets_backend": [
            "av_purchase/static/src/components/*"
        ]
    },
    "installable": True,
    "category": "Purchase Management",
    "maintainer": "Virunga Foundation",
    "website": "https://virunga.org",
}
