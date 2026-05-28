"""Hardcoded sample projects used by the portfolio list view as a fallback.

When the database has no published Project rows yet (e.g. fresh install, dev
machine), the portfolio page would otherwise be empty. Rather than ship an
ugly empty state during development, we render this representative data so
the layout can be reviewed. As soon as real projects are added via the admin,
the queryset takes over and this module is no longer touched at request time.
"""

SAMPLE_PROJECTS = [
    {
        'title': 'TropicTrack POS and Inventory',
        'client_type': 'Food and Beverage',
        'tech_stack': ['React', 'Node.js', 'PostgreSQL'],
        'description': (
            'A full point-of-sale and inventory management system for a multi-location '
            'restaurant group. Replaced a patchwork of spreadsheets and a legacy POS with '
            'a single dashboard-driven platform. Staff can process orders, manage stock '
            'levels, and trigger low-inventory alerts. Managers get real-time sales '
            'reporting and daily summary emails.'
        ),
        'highlights': [
            'Multi-location inventory sync',
            'Role-based dashboards for staff, managers, and owners',
            'Automated daily and weekly reports',
            'Custom invoice and receipt generation',
        ],
        'image_urls': [
            'https://images.unsplash.com/photo-1555396273-367ea4eb4db5?w=800&auto=format&fit=crop',
            'https://images.unsplash.com/photo-1414235077428-338989a2e8c0?w=800&auto=format&fit=crop',
            'https://images.unsplash.com/photo-1466978913421-dad2ebd01d17?w=800&auto=format&fit=crop',
        ],
    },
    {
        'title': 'BuildRight Project Hub',
        'client_type': 'Construction and Trades',
        'tech_stack': ['React', 'Express', 'MySQL'],
        'description': (
            'A project management and job costing platform for a regional construction '
            'contractor. Previously operating entirely on spreadsheets and paper, this '
            'system centralizes job creation, subcontractor management, purchase order '
            'tracking, and automated progress reporting. Project managers no longer '
            'manually compile weekly status updates.'
        ),
        'highlights': [
            'Job costing with real-time margin tracking',
            'Subcontractor and purchase order management',
            'Automated weekly progress reports',
            'Document storage per project',
        ],
        'image_urls': [
            'https://images.unsplash.com/photo-1504307651254-35680f356dfd?w=800&auto=format&fit=crop',
            'https://images.unsplash.com/photo-1581094794329-c8112a89af12?w=800&auto=format&fit=crop',
            'https://images.unsplash.com/photo-1503387762-592deb58ef4e?w=800&auto=format&fit=crop',
        ],
    },
    {
        'title': 'RetailFlow Inventory',
        'client_type': 'Retail and Distribution',
        'tech_stack': ['React', 'Node.js', 'MongoDB'],
        'description': (
            'An end-to-end inventory and order management application replacing a complex '
            'multi-sheet spreadsheet system used by a wholesale distributor. The system '
            'handles stock intake, order processing, customer records, and automated '
            'reorder alerts. Admin users control stock, while sales reps see '
            'customer-specific pricing and order history.'
        ),
        'highlights': [
            'Customer-specific pricing tiers',
            'Automated low-stock reorder alerts',
            'Order history and invoice generation',
            'Stock intake and adjustment logs',
        ],
        'image_urls': [
            'https://images.unsplash.com/photo-1441986300917-64674bd600d8?w=800&auto=format&fit=crop',
            'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=800&auto=format&fit=crop',
            'https://images.unsplash.com/photo-1472851294608-062f824d29cc?w=800&auto=format&fit=crop',
        ],
    },
]
