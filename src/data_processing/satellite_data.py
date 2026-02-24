import ee
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import rasterio
from rasterio.transform import from_bounds
import geopandas as gpd
from sentinelhub import (
    SentinelHubRequest, BBox, CRS, MimeType,
    DataCollection, SHConfig
)

class EnhancedSatelliteDataCollector:
    def __init__(self, project_area_file=None):
        """
        Initialize satellite data collection for specified area with enhancements
        """
        # Initialize Google Earth Engine
        try:
            ee.Initialize()
        except Exception:
            # In some environments, auth might be needed
            print("Earth Engine not initialized. Run 'earthengine authenticate' if needed.")
        
        # Sentinel Hub configuration
        self.config = SHConfig()
        self.config.sh_client_id = 'YOUR_CLIENT_ID'
        self.config.sh_client_secret = 'YOUR_CLIENT_SECRET'
        
        # Enhancement configurations
        self.cloud_threshold = 0.2
        self.use_data_fusion = True
        
        # Define project area
        if project_area_file:
            self.aoi = gpd.read_file(project_area_file)
        else:
            # Default area
            self.aoi_bounds = [-65.5, -3.5, -64.5, -2.5]  # minx, miny, maxx, maxy
            self.aoi = self._create_bbox(self.aoi_bounds)
        
    def _create_bbox(self, bounds):
        """Create bounding box from bounds"""
        return BBox(bbox=bounds, crs=CRS.WGS84)
    
    def apply_cloud_masking(self, image):
        """Remove cloudy pixels for accurate NDVI (Earth Engine approach)"""
        # Sentinel-2 cloud probability band
        cloud_prob = image.select('MSK_CLDPRB')
        cloud_mask = cloud_prob.lte(self.cloud_threshold * 100)
        return image.updateMask(cloud_mask)

    def collect_ndvi_data(self, start_date, end_date, interval_days=10):
        """
        Collect NDVI data from Sentinel-2 with potential cloud masking
        """
        dates = pd.date_range(start_date, end_date, freq=f'{interval_days}D')
        ndvi_time_series = []
        
        for date in dates:
            date_start = date.strftime('%Y-%m-%d')
            date_end = (date + timedelta(days=interval_days)).strftime('%Y-%m-%d')
            
            # Sentinel-2 request for NDVI with cloud masking logic in evalscript
            evalscript = """
            //VERSION=3
            function setup() {
                return {
                    input: ["B04", "B08", "SCL"],
                    output: { bands: 1, sampleType: "FLOAT32" }
                };
            }
            
            function evaluatePixel(sample) {
                // SCL (Scene Classification Layer) for cloud masking
                // 3: Cloud shadow, 8: Cloud medium probability, 9: Cloud high probability, 10: Cirrus
                if ([3, 8, 9, 10].includes(sample.SCL)) {
                    return [NaN];
                }
                let ndvi = (sample.B08 - sample.B04) / (sample.B08 + sample.B04);
                return [ndvi];
            }
            """
            
            request = SentinelHubRequest(
                evalscript=evalscript,
                input_data=[
                    SentinelHubRequest.input_data(
                        data_collection=DataCollection.SENTINEL2_L2A,
                        time_interval=(date_start, date_end),
                        maxcc=0.3
                    )
                ],
                responses=[
                    SentinelHubRequest.output_response('default', MimeType.TIFF)
                ],
                bbox=self.aoi,
                size=(512, 512),
                config=self.config
            )
            
            try:
                ndvi_data = request.get_data()[0]
                valid_mask = ~np.isnan(ndvi_data)
                if np.any(valid_mask):
                    ndvi_mean = np.mean(ndvi_data[valid_mask])
                    ndvi_time_series.append({
                        'date': date,
                        'ndvi_mean': ndvi_mean,
                        'ndvi_std': np.std(ndvi_data[valid_mask]),
                        'ndvi_min': np.min(ndvi_data[valid_mask]),
                        'ndvi_max': np.max(ndvi_data[valid_mask])
                    })
            except Exception as e:
                print(f"Error collecting data for {date_start}: {e}")
            
        return pd.DataFrame(ndvi_time_series)
    
    def collect_nightlight_data(self, start_date, end_date):
        """
        Collect VIIRS nightlight data using Earth Engine
        """
        viirs = ee.ImageCollection('NOAA/VIIRS/DNB/MONTHLY_V1/VCMSLCFG') \
                  .filterDate(start_date, end_date) \
                  .filterBounds(ee.Geometry.Rectangle(list(self.aoi.bounds)))
        
        nightlight_data = []
        
        def process_image(image):
            date = ee.Date(image.get('system:time_start')).format('YYYY-MM-dd')
            stats = image.reduceRegion(
                reducer=ee.Reducer.mean(),
                geometry=ee.Geometry.Rectangle(list(self.aoi.bounds)),
                scale=500,
                maxPixels=1e9
            )
            return {
                'date': date.getInfo(),
                'avg_radiance': stats.get('avg_radiance').getInfo()
            }
        
        image_list = viirs.toList(viirs.size())
        for i in range(image_list.size().getInfo()):
            image = ee.Image(image_list.get(i))
            nightlight_data.append(process_image(image))
        
        return pd.DataFrame(nightlight_data)

    def calculate_enhanced_ndvi(self):
        """Weighted fusion example (Conceptual for multi-source setup)"""
        # This would require additional setup for Landsat
        pass
