"""
GPS coordinates for monitoring points in Aravalli Hills
Based on actual locations mentioned in reports
"""

MONITORING_LOCATIONS = [
    # Rajasthan locations
    {
        'id': 'raj_001',
        'name': 'Sariska Tiger Reserve - Alwar',
        'lat': 27.3217,
        'lon': 76.4378,
        'state': 'Rajasthan',
        'risk_level': 'high',
        'mining_activity': 'active',
        'description': 'Critical tiger habitat, illegal mining reported',
        'camera_installed': True,
        'acoustic_sensor': True,
        'last_incident': '2026-02-20'
    },
    {
        'id': 'raj_002',
        'name': 'Tehla - Alwar District',
        'lat': 27.4217,
        'lon': 76.5378,
        'state': 'Rajasthan',
        'risk_level': 'high',
        'mining_activity': 'active',
        'description': 'Night mining reported, heavy machinery abandoned',
        'camera_installed': True,
        'acoustic_sensor': True,
        'last_incident': '2026-02-22'
    },
    {
        'id': 'raj_003',
        'name': "Bhartrihari's Tapasthali",
        'lat': 27.3517,
        'lon': 76.4678,
        'state': 'Rajasthan',
        'risk_level': 'medium',
        'mining_activity': 'suspicious',
        'description': 'Sacred site threatened by mining',
        'camera_installed': True,
        'acoustic_sensor': False,
        'last_incident': '2026-02-15'
    },
    {
        'id': 'raj_004',
        'name': 'Mount Abu',
        'lat': 24.5925,
        'lon': 72.7083,
        'state': 'Rajasthan',
        'risk_level': 'low',
        'mining_activity': 'none',
        'description': 'Highest peak, protected area',
        'camera_installed': True,
        'acoustic_sensor': True,
        'last_incident': None
    },
    {
        'id': 'raj_005',
        'name': 'Khetri - Jhunjhunu',
        'lat': 27.9833,
        'lon': 75.8000,
        'state': 'Rajasthan',
        'risk_level': 'medium',
        'mining_activity': 'historical',
        'description': 'Copper mining region, now under monitoring',
        'camera_installed': True,
        'acoustic_sensor': False,
        'last_incident': '2026-02-10'
    },
    # Haryana locations
    {
        'id': 'har_001',
        'name': 'Bakrija Hill - Haryana',
        'lat': 28.2833,
        'lon': 76.8167,
        'state': 'Haryana',
        'risk_level': 'high',
        'mining_activity': 'active',
        'description': 'Deep mining scars visible, groundwater exposed',
        'camera_installed': True,
        'acoustic_sensor': True,
        'last_incident': '2026-02-23'
    },
    {
        'id': 'har_002',
        'name': 'Ramalwas Hills',
        'lat': 28.3500,
        'lon': 76.8833,
        'state': 'Haryana',
        'risk_level': 'high',
        'mining_activity': 'active',
        'description': '200-feet deep pits, groundwater depletion',
        'camera_installed': True,
        'acoustic_sensor': True,
        'last_incident': '2026-02-21'
    },
    {
        'id': 'har_003',
        'name': 'Rajawas Village',
        'lat': 28.3833,
        'lon': 76.9167,
        'state': 'Haryana',
        'risk_level': 'high',
        'mining_activity': 'active',
        'description': 'Hilltop stripped bare by mining',
        'camera_installed': True,
        'acoustic_sensor': True,
        'last_incident': '2026-02-22'
    },
    {
        'id': 'har_004',
        'name': 'Gurugram - Sohna Road',
        'lat': 28.2475,
        'lon': 77.0406,
        'state': 'Haryana',
        'risk_level': 'medium',
        'mining_activity': 'suspicious',
        'description': 'Urban fringe, illegal construction mining',
        'camera_installed': True,
        'acoustic_sensor': True,
        'last_incident': '2026-02-19'
    },
    # Delhi-NCR locations
    {
        'id': 'del_001',
        'name': 'Asola Bhatti Wildlife Sanctuary',
        'lat': 28.4567,
        'lon': 77.1833,
        'state': 'Delhi',
        'risk_level': 'medium',
        'mining_activity': 'historical',
        'description': 'Former mining area, now under restoration',
        'camera_installed': True,
        'acoustic_sensor': False,
        'last_incident': '2026-02-05'
    },
    # Additional Rajasthan locations from 100-metre rule concern
    {
        'id': 'raj_006',
        'name': 'Chittorgarh Foothills',
        'lat': 24.8887,
        'lon': 74.6269,
        'state': 'Rajasthan',
        'risk_level': 'critical',
        'mining_activity': 'active',
        'description': 'Below 100m elevation, at risk under new rules',
        'camera_installed': True,
        'acoustic_sensor': True,
        'last_incident': '2026-02-20'
    },
    {
        'id': 'raj_007',
        'name': 'Nagaur - Kuchaman Road',
        'lat': 27.2000,
        'lon': 74.7333,
        'state': 'Rajasthan',
        'risk_level': 'critical',
        'mining_activity': 'active',
        'description': 'Low-elevation hills, water recharge zone',
        'camera_installed': True,
        'acoustic_sensor': True,
        'last_incident': '2026-02-22'
    },
    {
        'id': 'raj_008',
        'name': 'Bundi - Ramgarh',
        'lat': 25.4333,
        'lon': 75.6333,
        'state': 'Rajasthan',
        'risk_level': 'critical',
        'mining_activity': 'suspicious',
        'description': 'Ecologically vital low hills',
        'camera_installed': True,
        'acoustic_sensor': False,
        'last_incident': '2026-02-18'
    },
    {
        'id': 'raj_009',
        'name': 'Kaman - Bharatpur',
        'lat': 27.6500,
        'lon': 77.2667,
        'state': 'Rajasthan',
        'risk_level': 'critical',
        'mining_activity': 'active',
        'description': 'Excluded from definition, under threat',
        'camera_installed': True,
        'acoustic_sensor': True,
        'last_incident': '2026-02-21'
    },
    {
        'id': 'raj_010',
        'name': 'Sawai Madhopur',
        'lat': 26.0167,
        'lon': 76.3500,
        'state': 'Rajasthan',
        'risk_level': 'critical',
        'mining_activity': 'suspicious',
        'description': 'Ranthambhore buffer zone at risk',
        'camera_installed': True,
        'acoustic_sensor': True,
        'last_incident': '2026-02-19'
    }
]

# GPS tracking checkpoints based on NGT directive
GPS_CHECKPOINTS = [
    {'name': 'Gurugram Checkpost', 'lat': 28.4595, 'lon': 77.0266},
    {'name': 'Nuh Border', 'lat': 28.1167, 'lon': 77.0167},
    {'name': 'Faridabad Sector', 'lat': 28.4089, 'lon': 77.3178},
    {'name': 'Alwar Entry', 'lat': 27.5500, 'lon': 76.6167},
    {'name': 'Sariska Gate', 'lat': 27.3217, 'lon': 76.4378}
]

# RFID tag locations
RFID_GATES = [
    {'location': 'Gurugram-Mewat Border', 'lat': 28.2167, 'lon': 77.0167},
    {'location': 'Palwal-Mewat Border', 'lat': 28.1167, 'lon': 77.1667},
    {'location': 'Rajasthan-Haryana Border', 'lat': 27.9500, 'lon': 76.8167}
]
