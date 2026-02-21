Project Name: Auralite

Objective:
Build an AI-powered environmental monitoring application that detects potential illegal mining activity using multi-modal environmental indicators.

Problem Context:
Illegal mining causes vegetation loss, abnormal night-time industrial activity, and heavy machinery noise. Traditional satellite-only monitoring is reactive and slow. The goal is to create a predictive anomaly detection system.

Core Idea:
Combine three environmental signals:
1. NDVI vegetation decline
2. Nightlight intensity increase
3. Acoustic anomaly score (simulated for prototype)

System Architecture:

1. Data Layer:
- Input dataset (CSV format) with columns:
  Region_Name
  Latitude
  Longitude
  NDVI_Drop_Percentage
  Nightlight_Increase_Percentage
  Acoustic_Anomaly_Score

2. Feature Engineering:
- Normalize all input features between 0 and 1
- Create composite Mining_Risk_Score using weighted formula:
  Mining_Risk_Score = 
      (0.4 * NDVI_Drop_Percentage) +
      (0.3 * Nightlight_Increase_Percentage) +
      (0.3 * Acoustic_Anomaly_Score)

3. AI Model:
- Use Anomaly Detection (Isolation Forest preferred)
OR
- Use classification model with output classes:
    Low Risk
    Medium Risk
    High Risk

4. Business Logic Rules:
- If NDVI drop > 0.4 AND Nightlight increase > 0.5 → High Risk
- If Mining_Risk_Score > 0.7 → High Risk
- If Mining_Risk_Score between 0.4–0.7 → Medium Risk
- Else → Low Risk

5. Application Pages:

Page 1 – Dashboard Overview
- Display summary metrics:
    Total Regions
    High Risk Regions
    Average Risk Score

Page 2 – Region Analysis
- Select region
- Show:
    NDVI trend
    Nightlight trend
    Acoustic anomaly value
    Mining Risk Score
    Risk Classification

Page 3 – Risk Map
- Plot Latitude and Longitude
- Color-code regions:
    Red → High Risk
    Orange → Medium Risk
    Green → Low Risk

6. Output:
- Geo-tagged risk dashboard
- Exportable report (optional)
- Visual anomaly explanation

Prototype Notes:
- Acoustic data will be simulated.
- Satellite values will be pre-processed before upload.
- Focus on anomaly detection logic and explainability.

Sustainability Goal:
Enable early detection of illegal mining to prevent ecological degradation and support environmental governance.

Constraints:
- Use structured tabular dataset
- Keep model lightweight and interpretable
- Ensure hackathon-ready feasibility

Model Preference:
Use Isolation Forest for unsupervised anomaly detection.
Output anomaly score scaled between 0–1.
Explain model output using feature contribution.