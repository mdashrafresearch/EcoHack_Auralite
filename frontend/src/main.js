import './style.css'
import { createIcons, icons } from 'lucide'
import Chart from 'chart.js/auto'

// Config
const API_URL = 'http://127.0.0.1:5000/api'
let historyChart = null
let regions = []
let selectedRegionId = null

// Initialize Icons
createIcons({ icons })

// Elements
const timeEl = document.getElementById('curr-time')
const regionListEl = document.getElementById('region-list')
const heatmapGridEl = document.getElementById('heatmap-grid')
const refreshBtn = document.getElementById('refresh-btn')
const alertBanner = document.getElementById('risk-alert-banner')

const latInput = document.getElementById('input-lat')
const lngInput = document.getElementById('input-lng')
const analyzeBtn = document.getElementById('analyze-location-btn')

// Update Time
function updateTime() {
  const now = new Date()
  timeEl.textContent = now.toLocaleTimeString()
}
setInterval(updateTime, 1000)
updateTime()

// Leaflet Map Initialization
let map = null
let mapMarker = null

function initMap() {
  // Default to Amazon Basin Area
  map = L.map('map').setView([-3.46, -62.21], 4)

  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
  }).addTo(map)

  map.on('click', onMapClick)
}

function onMapClick(e) {
  const { lat, lng } = e.latlng

  // Update marker
  if (mapMarker) {
    mapMarker.setLatLng(e.latlng)
  } else {
    mapMarker = L.marker(e.latlng).addTo(map)
  }

  // Trigger Analysis
  analyzeMapLocation(lat, lng)
}

// Initial Load
async function init() {
  initMap()
  await fetchRegions()
  renderHeatmap()
  if (regions.length > 0) {
    selectRegion(regions[0].id)
  }
  updateSummary()
}

async function fetchRegions() {
  try {
    const response = await fetch(`${API_URL}/regions`)
    regions = await response.json()
    renderRegionList()
  } catch (error) {
    console.error('Error fetching regions:', error)
  }
}

async function updateSummary() {
  try {
    const response = await fetch(`${API_URL}/risk-summary`)
    const summary = await response.json()

    document.querySelector('#total-sectors .value').textContent = summary.total_regions
    document.querySelector('#high-risk-count .value').textContent = summary.high_risk_count
    document.querySelector('#health-index .value').textContent = `${summary.health_index}%`
    document.querySelector('#avg-threat .value').textContent = summary.average_risk_score.toFixed(2)

    // Add color classes if needed
    const healthEl = document.querySelector('#health-index .value')
    healthEl.className = 'value ' + (summary.health_index > 80 ? 'risk-low' : (summary.health_index > 50 ? 'risk-med' : 'risk-red'))
  } catch (error) {
    console.error('Error fetching summary:', error)
  }
}

function renderRegionList() {
  regionListEl.innerHTML = ''
  regions.forEach(r => {
    const div = document.createElement('div')
    div.className = `region-item ${selectedRegionId === r.id ? 'active' : ''}`
    div.innerHTML = `
            <div class="info">
                <h4>${r.name}</h4>
                <p>${r.area_sqkm} sq km</p>
            </div>
            <span class="mini-badge badge-${r.current_risk_level.toLowerCase()}">${r.current_risk_level}</span>
        `
    div.onclick = () => selectRegion(r.id)
    regionListEl.appendChild(div)
  })
}

async function selectRegion(id) {
  selectedRegionId = id
  alertBanner.classList.add('hidden') // Clear banner on region select
  renderRegionList() // Refresh active state

  try {
    const response = await fetch(`${API_URL}/analyze/${id}`)
    const data = await response.json()
    updateAnalysisView(data)
  } catch (error) {
    console.error('Error analyzing region:', error)
  }
}

async function analyzeLocation() {
  const lat = parseFloat(latInput.value)
  const lng = parseFloat(lngInput.value)

  if (isNaN(lat) || isNaN(lng)) {
    alert('Please enter valid coordinates.')
    return
  }

  analyzeBtn.textContent = 'Scanning...'
  analyzeBtn.disabled = true

  try {
    const response = await fetch(`${API_URL}/analyze-location`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ latitude: lat, longitude: lng })
    })

    const data = await response.json()

    if (response.status === 404) {
      alert(data.message)
      return
    }

    // Mock a response structure suitable for updateAnalysisView or update manually
    updateAnalysisViewWithLocation(data)

    // Handle Alert Banner
    if (data.classification === 'High') {
      alertBanner.classList.remove('hidden')
    } else {
      alertBanner.classList.add('hidden')
    }

    // Highlight in heatmap (pseudo-logic)
    highlightHeatmap()

  } catch (error) {
    console.error('Error analyzing location:', error)
  } finally {
    analyzeBtn.textContent = 'Analyze Coordinates'
    analyzeBtn.disabled = false
  }
}

function updateAnalysisViewWithLocation(data) {
  // Header
  document.getElementById('selected-region-name').textContent = `Custom Analysis: ${data.region_name}`
  document.getElementById('selected-region-location').textContent = `LAT: ${data.latitude} | LNG: ${data.longitude} (${data.distance_km}km from monitor)`

  const badge = document.getElementById('risk-classification')
  badge.textContent = data.classification
  badge.className = `risk-badge badge-${data.classification.toLowerCase()}`

  // Indicators
  updateBadge('badge-ndvi', data.ndvi_drop)
  updateBadge('badge-night', data.nightlight_inc)
  updateBadge('badge-acoustic', data.acoustic_score)

  // AI Stats
  document.getElementById('score-ai').textContent = data.anomaly_score.toFixed(3)
  document.getElementById('score-rule').textContent = data.composite_score.toFixed(3)

  // Confidence (Derived)
  const confidence = (data.anomaly_score > 0.6 && data.composite_score > 0.6) || (data.anomaly_score < 0.4 && data.composite_score < 0.4) ? 'High' : 'Standard'
  const confFill = document.getElementById('conf-fill')
  const confText = document.getElementById('conf-text')
  confText.textContent = `${confidence} CONFIDENCE`
  confFill.style.width = confidence === 'High' ? '100%' : '50%'

  // Contributions
  if (data.feature_contributions) {
    renderContributions(data.feature_contributions)
  }

  // For custom location, we don't have historical trend in the same way, so we just clear or show single point
  if (historyChart) {
    historyChart.data.labels = ['Current']
    historyChart.data.datasets[0].data = [data.final_score]
    historyChart.update()
  }
}

function highlightHeatmap() {
  // Just a visual flash on the heatmap to indicate processing
  const cells = document.querySelectorAll('.heatmap-cell')
  const randomCell = cells[Math.floor(Math.random() * cells.length)]
  randomCell.style.boxShadow = '0 0 20px var(--primary-color)'
  randomCell.style.background = 'var(--primary-color)'
  setTimeout(() => {
    randomCell.style.boxShadow = ''
    randomCell.style.background = ''
  }, 2000)
}

function updateAnalysisView(data) {
  const { region, latest_indicators, risk_analysis, history } = data

  // Header
  document.getElementById('selected-region-name').textContent = region.name
  document.getElementById('selected-region-location').textContent = `LAT: ${region.latitude} | LNG: ${region.longitude}`

  const badge = document.getElementById('risk-classification')
  badge.textContent = risk_analysis.classification
  badge.className = `risk-badge badge-${risk_analysis.classification.toLowerCase()}`

  // Indicators
  updateBadge('badge-ndvi', latest_indicators.ndvi_drop)
  updateBadge('badge-night', latest_indicators.nightlight_inc)
  updateBadge('badge-acoustic', latest_indicators.acoustic_score)

  // AI Stats
  document.getElementById('score-ai').textContent = risk_analysis.ai_score.toFixed(3)
  document.getElementById('score-rule').textContent = risk_analysis.rule_score.toFixed(3)

  // Confidence
  const confFill = document.getElementById('conf-fill')
  const confText = document.getElementById('conf-text')
  confText.textContent = `${risk_analysis.confidence} CONFIDENCE`
  confFill.style.width = risk_analysis.confidence === 'High' ? '100%' : '50%'
  confFill.style.backgroundColor = risk_analysis.confidence === 'High' ? 'var(--primary-color)' : 'var(--text-secondary)'

  // Contributions
  if (risk_analysis.feature_contributions) {
    renderContributions(risk_analysis.feature_contributions)
  }

  // Chart
  renderChart(history)
}

function renderContributions(contributions) {
  const listEl = document.getElementById('contribution-list')
  listEl.innerHTML = ''

  Object.entries(contributions).forEach(([name, value]) => {
    const pct = (value * 100).toFixed(0)
    const div = document.createElement('div')
    div.className = 'driver-item'
    div.innerHTML = `
            <div class="driver-info">
                <span>${name}</span>
                <span>${pct}% Influence</span>
            </div>
            <div class="driver-bar-bg">
                <div class="driver-bar-fill" style="width: ${pct}%"></div>
            </div>
        `
    listEl.appendChild(div)
  })
}

function updateBadge(id, value) {
  const el = document.getElementById(id)
  el.textContent = value.toFixed(2)
  const level = value > 0.75 ? 'high' : (value > 0.45 ? 'med' : 'low')
  el.className = `indicator-badge badge-${level}`
}

function renderChart(history) {
  const ctx = document.getElementById('analysisChart').getContext('2d')
  const labels = history.map(h => new Date(h.timestamp).toLocaleDateString()).reverse()
  const scores = history.map(h => h.final_score).reverse()

  if (historyChart) historyChart.destroy()

  historyChart = new Chart(ctx, {
    type: 'line',
    data: {
      labels,
      datasets: [{
        label: 'Mining Risk Score',
        data: scores,
        borderColor: '#00e5ff',
        backgroundColor: 'rgba(0, 229, 255, 0.1)',
        fill: true,
        tension: 0.3
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: {
        y: { min: 0, max: 1, grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#8a8a9a' } },
        x: { grid: { display: false }, ticks: { color: '#8a8a9a' } }
      }
    }
  })
}

async function analyzeMapLocation(lat, lng) {
  const resultSection = document.getElementById('map-result-display')
  resultSection.classList.remove('hidden')
  resultSection.scrollIntoView({ behavior: 'smooth' })

  const resCoords = document.getElementById('res-coords')
  const resClassification = document.getElementById('res-classification')
  const resNdvi = document.getElementById('res-ndvi')
  const resNight = document.getElementById('res-night')
  const resAcoustic = document.getElementById('res-acoustic')
  const resFinal = document.getElementById('res-final')
  const satelliteImg = document.getElementById('map-satellite-img')

  resCoords.textContent = `${lat.toFixed(4)} / ${lng.toFixed(4)}`
  resClassification.textContent = 'SCANNING...'
  resClassification.className = 'risk-badge'

  try {
    const response = await fetch(`${API_URL}/analyze-map-location`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ latitude: lat, longitude: lng })
    })

    const data = await response.json()

    // Update UI
    resClassification.textContent = data.classification.toUpperCase()
    resClassification.className = `risk-badge badge-${data.classification.toLowerCase()}`

    resNdvi.textContent = data.ndvi_drop.toFixed(3)
    resNight.textContent = data.nightlight_inc.toFixed(3)
    resAcoustic.textContent = data.acoustic_score.toFixed(3)
    resFinal.textContent = data.final_score.toFixed(3)

    satelliteImg.src = data.satellite_image_url

    // Handle Alert Banner
    if (data.classification === 'High') {
      alertBanner.classList.remove('hidden')
    } else {
      alertBanner.classList.add('hidden')
    }

  } catch (error) {
    console.error('Error analyzing map location:', error)
    resClassification.textContent = 'ERROR'
  }
}

function renderHeatmap() {
  heatmapGridEl.innerHTML = ''
  // Generate a 100-cell grid for effect, mapping real regions to random cells
  const regionCells = new Set()
  const regionMap = {}

  regions.forEach(r => {
    let cellIdx = Math.floor(Math.random() * 200)
    while (regionCells.has(cellIdx)) cellIdx = Math.floor(Math.random() * 200)
    regionCells.add(cellIdx)
    regionMap[cellIdx] = r
  })

  for (let i = 0; i < 200; i++) {
    const cell = document.createElement('div')
    cell.className = 'heatmap-cell'
    if (regionMap[i]) {
      const r = regionMap[i]
      cell.classList.add(`cell-${r.current_risk_level.toLowerCase()}`)
      cell.title = `${r.name}: ${r.current_risk_level} Risk`
      cell.onclick = () => selectRegion(r.id)
    }
    heatmapGridEl.appendChild(cell)
  }
}

// Event Listeners
refreshBtn.addEventListener('click', async () => {
  refreshBtn.classList.add('spinning')
  await fetchRegions()
  if (selectedRegionId) await selectRegion(selectedRegionId)
  await updateSummary()
  renderHeatmap()
  setTimeout(() => refreshBtn.classList.remove('spinning'), 1000)
})

analyzeBtn.addEventListener('click', analyzeLocation)

// Initialize
init()
