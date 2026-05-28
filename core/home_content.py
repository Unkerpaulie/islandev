"""Static content for the home page sections.

Kept separate from views.py so the view stays small and the icon SVG paths
(verbose by nature) live as data rather than view code. Icon paths are taken
from the Lucide icon set (https://lucide.dev). When swapping to dynamic
content from the database later, the templates won't need to change — the
shape of these dicts is the contract.
"""

_LUCIDE = {
    'lightbulb': '<path d="M9 18h6"/><path d="M10 22h4"/><path d="M15.09 14a5 5 0 1 0-6.18 0c.55.42.96 1 1.09 1.69V17h4v-1.31c.13-.69.54-1.27 1.09-1.69z"/>',
    'clipboard-list': '<rect x="8" y="2" width="8" height="4" rx="1" ry="1"/><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"/><path d="M12 11h4"/><path d="M12 16h4"/><line x1="8" y1="11" x2="8.01" y2="11"/><line x1="8" y1="16" x2="8.01" y2="16"/>',
    'monitor': '<rect x="2" y="3" width="20" height="14" rx="2" ry="2"/><line x1="8" y1="21" x2="16" y2="21"/><line x1="12" y1="17" x2="12" y2="21"/>',
    'bar-chart': '<line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/>',
    'receipt': '<path d="M4 2v20l2-1.5 2 1.5 2-1.5 2 1.5 2-1.5 2 1.5 2-1.5 2 1.5V2l-2 1.5L18 2l-2 1.5L14 2l-2 1.5L10 2 8 3.5 6 2z"/><path d="M8 8h8"/><path d="M8 12h8"/><path d="M8 16h6"/>',
    'database': '<ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"/><path d="M3 12c0 1.66 4 3 9 3s9-1.34 9-3"/>',
    'user-check': '<path d="M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="8.5" cy="7" r="4"/><polyline points="17 11 19 13 23 9"/>',
    'puzzle': '<path d="M19.439 7.85c-.049.322.059.648.289.878l1.568 1.568c.47.47.706 1.087.706 1.704s-.235 1.233-.706 1.704l-1.611 1.611a.98.98 0 0 1-.837.276c-.47-.07-.802-.48-.968-.925a2.501 2.501 0 1 0-3.214 3.214c.446.166.855.497.925.968a.979.979 0 0 1-.276.837l-1.61 1.61a2.402 2.402 0 0 1-1.705.707 2.402 2.402 0 0 1-1.704-.706l-1.568-1.568a1.026 1.026 0 0 0-.877-.29c-.493.074-.84.504-1.02.968a2.5 2.5 0 1 1-3.237-3.237c.464-.18.894-.527.967-1.02a1.026 1.026 0 0 0-.289-.877l-1.568-1.568A2.402 2.402 0 0 1 2 12c0-.617.236-1.234.706-1.704L4.23 8.77c.24-.24.581-.353.917-.303.515.077.877.528 1.073 1.01a2.5 2.5 0 1 0 3.259-3.259c-.482-.196-.933-.558-1.01-1.073-.05-.336.062-.676.303-.917l1.525-1.525A2.402 2.402 0 0 1 12 2c.617 0 1.234.236 1.704.706l1.568 1.568c.23.23.556.338.877.29.493-.074.84-.504 1.02-.968a2.5 2.5 0 1 1 3.237 3.237c-.464.18-.894.527-.967 1.02z"/>',
    'layers': '<polygon points="12 2 2 7 12 12 22 7 12 2"/><polyline points="2 17 12 22 22 17"/><polyline points="2 12 12 17 22 12"/>',
}


SERVICES = [
    {
        'icon_svg': _LUCIDE['lightbulb'],
        'title': 'Digital Consultation',
        'tagline': 'Clarity before code.',
        'desc': 'Clarity-first discovery sessions that map your business processes and define a practical digital roadmap.',
        'desc_long': 'Before any technology is chosen, we map your business — its processes, pain points, team structure, and goals. The outcome is a clear, prioritized digital roadmap that guides every decision forward.',
        'deliverables': [
            'Process mapping sessions',
            'Digital readiness assessment',
            'Prioritized roadmap document',
            'Technology stack recommendation',
        ],
    },
    {
        'icon_svg': _LUCIDE['clipboard-list'],
        'title': 'SOP Development',
        'tagline': 'Consistency at scale.',
        'desc': 'Document and standardize your operations so your team works consistently and confidently.',
        'desc_long': 'Standard Operating Procedures are the backbone of a scalable business. I work with your team to document, refine, and digitize your operational workflows so everyone knows exactly what to do and when.',
        'deliverables': [
            'Process interviews and documentation',
            'Workflow diagrams',
            'Editable SOP documents',
            'Integration with your systems',
        ],
    },
    {
        'icon_svg': _LUCIDE['monitor'],
        'title': 'Custom Web Applications',
        'tagline': 'Built for your business, not a template.',
        'desc': 'Bespoke dashboard-driven systems built exactly for how your business operates and who uses them.',
        'desc_long': 'Every custom application starts from a deep understanding of how your team works. The result is a dashboard-driven system with data entry, reporting, and access controls designed specifically for your operations.',
        'deliverables': [
            'Role-based dashboards',
            'Custom data entry forms',
            'Internal reporting',
            'User access management',
        ],
    },
    {
        'icon_svg': _LUCIDE['bar-chart'],
        'title': 'Business Intelligence',
        'tagline': 'Turn your data into decisions.',
        'desc': 'KPI dashboards, internal reports, and performance monitors that give you real insight.',
        'desc_long': 'Visibility drives performance. I build internal reporting systems, KPI dashboards, and data visualizations that give managers and owners a real-time view of what is actually happening in their business.',
        'deliverables': [
            'KPI dashboard design',
            'Automated internal reports',
            'Data visualization',
            'Trend analysis tools',
        ],
    },
    {
        'icon_svg': _LUCIDE['receipt'],
        'title': 'Invoice and Estimate Systems',
        'tagline': 'Professional billing, built in.',
        'desc': 'Professional billing instruments integrated into your existing workflow.',
        'desc_long': 'Eliminate manual invoice creation and spreadsheet estimates. I build integrated billing instruments that generate, track, and record all client-facing documents directly within your business system.',
        'deliverables': [
            'Branded invoice generator',
            'Estimate and quote builder',
            'Payment status tracking',
            'Client record management',
        ],
    },
    {
        'icon_svg': _LUCIDE['database'],
        'title': 'Data Architecture',
        'tagline': 'Structure that supports growth.',
        'desc': 'Clean, structured databases and data pipelines designed to grow with your business.',
        'desc_long': 'Many businesses are trapped by their own data because it was never structured properly. I design and build clean relational databases and data pipelines that grow with your business and integrate across your tools.',
        'deliverables': [
            'Database schema design',
            'Data migration support',
            'API integrations',
            'Data validation and cleanup',
        ],
    },
]


REASONS = [
    {
        'icon_svg': _LUCIDE['user-check'],
        'title': 'Built Around Your Team',
        'desc': 'Every system I build is designed around who uses it and how they work — not a generic template.',
    },
    {
        'icon_svg': _LUCIDE['puzzle'],
        'title': 'End-to-End Ownership',
        'desc': 'From scoping and process mapping to development and deployment, I handle the full journey.',
    },
    {
        'icon_svg': _LUCIDE['layers'],
        'title': 'Right-Sized for SMEs',
        'desc': 'Enterprise capability at a scale and cost that makes sense for growing businesses.',
    },
]


FEATURED_PROJECTS = [
    {
        'title': 'TropicTrack POS',
        'type': 'Food and Beverage',
        'desc': 'A full point-of-sale and inventory management system with real-time dashboard reporting for a multi-location restaurant group.',
        'img': 'https://images.unsplash.com/photo-1555396273-367ea4eb4db5?w=700&auto=format&fit=crop',
    },
    {
        'title': 'BuildRight Project Hub',
        'type': 'Construction and Trades',
        'desc': 'Project management dashboard with job costing, subcontractor tracking, and automated progress reporting for a regional contractor.',
        'img': 'https://images.unsplash.com/photo-1504307651254-35680f356dfd?w=700&auto=format&fit=crop',
    },
    {
        'title': 'RetailFlow Inventory',
        'type': 'Retail and Distribution',
        'desc': 'End-to-end inventory and order management platform replacing spreadsheets with a structured, role-based web application.',
        'img': 'https://images.unsplash.com/photo-1441986300917-64674bd600d8?w=700&auto=format&fit=crop',
    },
]
