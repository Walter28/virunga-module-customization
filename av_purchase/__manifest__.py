# -*- coding: utf-8 -*- 
{
    "name":"Av Purchase",
    "summary":"Alliance Virunga Purchase App",
    "version":"17.0.1.0.0",
    'description': "Alliance Virunga Purchase App",
    'author': "Virunga Foundation",
    "license":"OPL-1",
    "depends":["base", "purchase"],
    "application":False,
    "data": [
        # Security

        # Views
        
        # Menu views
        'views/av_purchase_menu_views.xml',
        
        # Data
        
    ],

    'assets': {
            'web.assets_backend': [
                'av_purchase/static/src/*',
            ],
        },

    "installable": True
}
