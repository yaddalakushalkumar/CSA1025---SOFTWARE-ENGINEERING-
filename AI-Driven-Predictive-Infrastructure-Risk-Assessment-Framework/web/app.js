/**
 * InfraRisk-AI Frontend Application
 * Handles API integration, Leaflet mapping, Chart.js visualizations,
 * and interactive optimization / scenario modeling.
 */

class InfraRiskApp {
  constructor() {
    this.assets = [];
    this.topology = { nodes: [], edges: [] };
    this.analytics = {};
    this.selectedAsset = null;
    this.map = null;
    this.markers = {};
    this.edgePolylines = [];
    this.charts = {};

    this.init();
  }

  async init() {
    this.initNavigationTabs();
    this.initMap();
    await this.refreshAllData();
    this.initCharts();
  }

  initNavigationTabs() {
    const tabs = document.querySelectorAll('.menu-tab');
    tabs.forEach(tab => {
      tab.addEventListener('click', () => {
        tabs.forEach(t => t.classList.remove('active'));
        document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
        
        tab.classList.add('active');
        const target = tab.dataset.tab;
        const panel = document.getElementById(target);
        if (panel) {
          panel.classList.add('active');
          if (target === 'tab-map' && this.map) {
            setTimeout(() => this.map.invalidateSize(), 150);
          }
          if (target === 'tab-degradation') {
            this.renderDegradationCharts();
          }
          if (target === 'tab-societal') {
            this.renderSocietalCharts();
          }
        }
      });
    });
  }

  initMap() {
    if (typeof L === 'undefined') {
      console.warn('Leaflet library not loaded, using SVG fallback.');
      const mapContainer = document.getElementById('infraMap');
      if (mapContainer) {
        mapContainer.innerHTML = '<div style="display:flex;align-items:center;justify-content:center;height:100%;color:#94a3b8;flex-direction:column;gap:0.5rem;"><svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#38bdf8" stroke-width="1.5"><polygon points="1 6 1 22 8 18 16 22 23 18 23 2 16 6 8 2 1 6"></polygon></svg><p>Metropolitan Infrastructure Network Topology (30 Assets Online)</p></div>';
      }
      return;
    }

    try {
      // Center map around metropolitan coordinates
      this.map = L.map('infraMap', {
        zoomControl: true,
        attributionControl: false
      }).setView([40.7180, -74.0050], 12);

      // Dark Tile Layer (CartoDB Dark Matter)
      L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
        maxZoom: 18,
        subdomains: 'abcd'
      }).addTo(this.map);
    } catch (e) {
      console.error('Error initializing Leaflet map:', e);
    }
  }

  async refreshAllData() {
    try {
      await Promise.all([
        this.fetchAnalytics(),
        this.fetchTopology(),
        this.fetchAssets(),
        this.fetchTopsisRankings()
      ]);
      this.populateAssetDropdown();
      this.renderMapElements();
      this.renderAssetTable();
    } catch (err) {
      console.error('Failed to load system data:', err);
    }
  }

  async fetchAnalytics() {
    const res = await fetch('/api/analytics/overview');
    if (!res.ok) return;
    this.analytics = await res.json();
    const kpis = this.analytics.kpis;
    
    document.getElementById('kpiTotalAssets').innerText = kpis.total_assets;
    document.getElementById('kpiAvgShi').innerText = kpis.average_network_shi + ' / 100';
    document.getElementById('kpiAvgPf').innerText = (kpis.average_failure_probability * 100).toFixed(1) + '%';
    document.getElementById('kpiCriticalCount').innerText = kpis.critical_assets_count;
    document.getElementById('kpiPopServed').innerText = (kpis.total_served_population / 1e3).toFixed(0) + 'k';
  }

  async fetchTopology() {
    const res = await fetch('/api/network/topology');
    if (res.ok) {
      this.topology = await res.json();
    }
  }

  async fetchAssets() {
    const res = await fetch('/api/assets');
    if (res.ok) {
      this.assets = await res.json();
    }
  }

  async fetchTopsisRankings() {
    const res = await fetch('/api/prioritization/topsis');
    if (res.ok) {
      const rankings = await res.json();
      this.renderTopsisTable(rankings);
    }
  }

  renderMapElements() {
    if (!this.map) return;

    // Clear previous markers & polylines
    Object.values(this.markers).forEach(m => this.map.removeLayer(m));
    this.edgePolylines.forEach(p => this.map.removeLayer(p));
    this.markers = {};
    this.edgePolylines = [];

    // Draw network topology edges
    const nodeCoords = {};
    this.topology.nodes.forEach(n => {
      nodeCoords[n.id] = [n.lat, n.lng];
    });

    this.topology.edges.forEach(edge => {
      const u = nodeCoords[edge.source];
      const v = nodeCoords[edge.target];
      if (u && v) {
        const polyline = L.polyline([u, v], {
          color: '#38bdf8',
          weight: 2,
          opacity: 0.45,
          dashArray: '4, 4'
        }).addTo(this.map);
        this.edgePolylines.push(polyline);
      }
    });

    // Draw asset nodes with color-coded risk markers
    this.topology.nodes.forEach(node => {
      let markerColor = '#10b981'; // Green (Routine)
      if (node.cri >= 45.0) markerColor = '#f43f5e'; // Red (Critical)
      else if (node.cri >= 25.0) markerColor = '#f97316'; // Orange (High)
      else if (node.cri >= 12.0) markerColor = '#f59e0b'; // Amber (Medium)

      const iconHtml = `<div style="
        background-color: ${markerColor};
        width: 14px;
        height: 14px;
        border-radius: 50%;
        border: 2px solid white;
        box-shadow: 0 0 10px ${markerColor};
      "></div>`;

      const customIcon = L.divIcon({
        className: 'custom-map-pin',
        html: iconHtml,
        iconSize: [14, 14],
        iconAnchor: [7, 7]
      });

      const marker = L.marker([node.lat, node.lng], { icon: customIcon }).addTo(this.map);
      marker.bindTooltip(`<strong>${node.name}</strong><br>CRI: ${node.cri} | SHI: ${node.shi}`, {
        direction: 'top',
        className: 'map-tooltip'
      });

      marker.on('click', () => {
        this.selectAsset(node.id);
      });

      this.markers[node.id] = marker;
    });
  }

  selectAsset(assetId) {
    const asset = this.assets.find(a => a.id === assetId);
    if (!asset) return;

    this.selectedAsset = asset;
    document.getElementById('emptyDetailPrompt').style.display = 'none';
    document.getElementById('assetDetailContent').style.display = 'block';

    document.getElementById('detailAssetName').innerText = asset.name;
    document.getElementById('detailAssetId').innerText = `${asset.id} • ${asset.district}`;
    document.getElementById('detailTypeBadge').innerText = asset.asset_type;
    
    // Fetch live risk metrics for this asset
    fetch(`/api/assets/${assetId}/risk`)
      .then(r => r.json())
      .then(risk => {
        document.getElementById('detailCriVal').innerText = risk.composite_risk_index.toFixed(1);
        document.getElementById('detailShiVal').innerText = asset.structural_health_index.toFixed(1);
        document.getElementById('detailPfVal').innerText = (risk.failure_probability_1yr * 100).toFixed(1) + '%';
        document.getElementById('detailSocVal').innerText = risk.composite_societal_impact.toFixed(1) + '/100';

        const fill = document.getElementById('detailShiProgress');
        fill.style.width = asset.structural_health_index + '%';
        if (asset.structural_health_index < 40) fill.style.background = '#f43f5e';
        else if (asset.structural_health_index < 70) fill.style.background = '#f59e0b';
        else fill.style.background = '#10b981';
      });

    // Populate Telemetry
    const t = asset.telemetry;
    document.getElementById('telVibration').innerText = t.vibration_rms_g.toFixed(2) + ' g';
    document.getElementById('telStrain').innerText = t.strain_microstrain.toFixed(0) + ' &mu;&epsilon;';
    document.getElementById('telCorrosion').innerText = t.corrosion_rate_mpy.toFixed(1) + ' mpy';
    document.getElementById('telAcoustic').innerText = t.acoustic_energy_db.toFixed(1) + ' dB';
    document.getElementById('telAnomaly').innerText = (t.telemetry_anomaly_score * 100).toFixed(0) + '% Anomaly';

    // Populate Societal
    const s = asset.societal;
    document.getElementById('socHosp').innerText = s.hospital_proximity_km.toFixed(1) + ' km';
    document.getElementById('socSvi').innerText = (s.social_vulnerability_index * 100).toFixed(0) + 'th %tile';
    document.getElementById('socTraffic').innerText = s.daily_traffic_volume_aadt.toLocaleString() + ' AADT';
    document.getElementById('socDetour').innerText = s.detour_length_km.toFixed(1) + ' km';

    // Center map on asset
    this.map.panTo([asset.latitude, asset.longitude]);
  }

  renderAssetTable() {
    const tbody = document.getElementById('assetTableBody');
    tbody.innerHTML = '';

    fetch('/api/risk-assessment')
      .then(r => r.json())
      .then(assessments => {
        document.getElementById('tableCountBadge').innerText = `Showing ${assessments.length} assets`;

        assessments.forEach(ass => {
          const asset = this.assets.find(a => a.id === ass.asset_id);
          const tr = document.createElement('tr');
          
          let badgeClass = 'badge-success';
          if (ass.condition_state === 'CRITICAL') badgeClass = 'badge-danger';
          else if (ass.condition_state === 'POOR') badgeClass = 'badge-warning';
          else if (ass.condition_state === 'FAIR') badgeClass = 'badge-info';

          tr.innerHTML = `
            <td><strong>${ass.asset_id}</strong></td>
            <td>${ass.asset_name}</td>
            <td>${asset ? asset.district : '--'}</td>
            <td><span class="badge badge-info">${ass.asset_type}</span></td>
            <td><strong>${ass.current_shi.toFixed(1)}</strong></td>
            <td><span class="badge ${badgeClass}">${ass.condition_state}</span></td>
            <td>${(ass.failure_probability_1yr * 100).toFixed(1)}%</td>
            <td>${ass.composite_societal_impact.toFixed(1)}</td>
            <td><strong class="highlight-red">${ass.composite_risk_index.toFixed(1)}</strong></td>
            <td><span class="badge ${ass.priority_tier.includes('P1') ? 'badge-danger' : 'badge-warning'}">${ass.priority_tier}</span></td>
            <td><button class="btn btn-secondary btn-sm" onclick="app.selectAsset('${ass.asset_id}')">Inspect</button></td>
          `;
          tbody.appendChild(tr);
        });
      });
  }

  filterAssets() {
    const dist = document.getElementById('districtFilter').value;
    const type = document.getElementById('typeFilter').value;

    this.topology.nodes.forEach(node => {
      const marker = this.markers[node.id];
      const matchDist = !dist || node.district === dist;
      const matchType = !type || node.type === type;

      if (matchDist && matchType) {
        if (!this.map.hasLayer(marker)) marker.addTo(this.map);
      } else {
        if (this.map.hasLayer(marker)) this.map.removeLayer(marker);
      }
    });
  }

  populateAssetDropdown() {
    const select = document.getElementById('degradationAssetSelect');
    select.innerHTML = '';
    this.assets.forEach(a => {
      const opt = document.createElement('option');
      opt.value = a.id;
      opt.innerText = `${a.id} - ${a.name} (SHI: ${a.structural_health_index})`;
      select.appendChild(opt);
    });
  }

  initCharts() {
    if (typeof Chart === 'undefined') {
      console.warn('Chart.js not loaded, skipping chart canvas initialization.');
      return;
    }
    // Trajectory Chart
    const ctxTraj = document.getElementById('trajectoryChart').getContext('2d');
    this.charts.trajectory = new Chart(ctxTraj, {
      type: 'line',
      data: {
        labels: Array.from({ length: 10 }, (_, i) => `Yr ${i + 1}`),
        datasets: [
          {
            label: 'Structural Health Index (SHI)',
            borderColor: '#38bdf8',
            backgroundColor: 'rgba(56, 189, 248, 0.1)',
            data: [],
            yAxisID: 'y'
          },
          {
            label: 'Failure Probability (Pf)',
            borderColor: '#f43f5e',
            backgroundColor: 'rgba(244, 63, 94, 0.1)',
            data: [],
            yAxisID: 'y1'
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          y: { min: 0, max: 100, title: { display: true, text: 'SHI (0-100)' } },
          y1: { min: 0, max: 1, position: 'right', title: { display: true, text: 'Failure Probability (0.0 - 1.0)' } }
        }
      }
    });

    // Markov Chart
    const ctxMarkov = document.getElementById('markovChart').getContext('2d');
    this.charts.markov = new Chart(ctxMarkov, {
      type: 'bar',
      data: {
        labels: ['Yr 0', 'Yr 1', 'Yr 2', 'Yr 3', 'Yr 4', 'Yr 5'],
        datasets: [
          { label: 'Excellent', data: [], backgroundColor: '#10b981' },
          { label: 'Good', data: [], backgroundColor: '#38bdf8' },
          { label: 'Fair', data: [], backgroundColor: '#f59e0b' },
          { label: 'Poor', data: [], backgroundColor: '#f97316' },
          { label: 'Critical', data: [], backgroundColor: '#f43f5e' }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          x: { stacked: true },
          y: { stacked: true, max: 1.0, title: { display: true, text: 'Probability' } }
        }
      }
    });

    // Radar Telemetry Chart
    const ctxRadar = document.getElementById('telemetryRadarChart').getContext('2d');
    this.charts.radar = new Chart(ctxRadar, {
      type: 'radar',
      data: {
        labels: ['Vibration Strain', 'Corrosion Rate', 'Acoustic Energy', 'Traffic Load', 'Environmental Stress', 'SVI Equity'],
        datasets: [{
          label: 'Stress Profile',
          data: [65, 80, 55, 75, 85, 60],
          borderColor: '#6366f1',
          backgroundColor: 'rgba(99, 102, 241, 0.2)'
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: { r: { min: 0, max: 100 } }
      }
    });
  }

  async renderDegradationCharts() {
    if (typeof Chart === 'undefined') return;
    const assetId = document.getElementById('degradationAssetSelect').value || (this.assets[0] && this.assets[0].id);
    if (!assetId) return;

    // Fetch Trajectory
    const trajRes = await fetch(`/api/assets/${assetId}/trajectory?years=10`);
    if (trajRes.ok) {
      const data = await trajRes.json();
      const shiData = data.trajectory.map(t => t.projected_shi);
      const pfData = data.trajectory.map(t => t.failure_probability);

      this.charts.trajectory.data.datasets[0].data = shiData;
      this.charts.trajectory.data.datasets[1].data = pfData;
      this.charts.trajectory.update();
    }

    // Fetch Markov
    const markovRes = await fetch(`/api/assets/${assetId}/markov?years=5`);
    if (markovRes.ok) {
      const mData = await markovRes.json();
      const dist = mData.yearly_state_probabilities; // 6 elements (Yr 0 to 5), each array of 5
      for (let stateIdx = 0; stateIdx < 5; stateIdx++) {
        this.charts.markov.data.datasets[stateIdx].data = dist.map(yearVec => yearVec[stateIdx]);
      }
      this.charts.markov.update();
    }
  }

  async renderSocietalCharts() {
    if (typeof Chart === 'undefined') return;
    const res = await fetch('/api/risk-assessment');
    if (!res.ok) return;
    const assessments = await res.json();

    // Risk Matrix Scatter Chart
    const scatterCanvas = document.getElementById('riskMatrixChart');
    if (!this.charts.riskMatrix) {
      this.charts.riskMatrix = new Chart(scatterCanvas.getContext('2d'), {
        type: 'scatter',
        data: {
          datasets: [{
            label: 'Assets (Failure Prob vs Societal Impact)',
            data: assessments.map(a => ({ x: a.failure_probability_1yr, y: a.composite_societal_impact, label: a.asset_name })),
            backgroundColor: assessments.map(a => a.composite_risk_index > 40 ? '#f43f5e' : (a.composite_risk_index > 20 ? '#f59e0b' : '#10b981')),
            pointRadius: 6
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            x: { min: 0, max: 1.0, title: { display: true, text: '1-Yr Failure Probability (Pf)' } },
            y: { min: 0, max: 100, title: { display: true, text: 'Composite Societal Impact (0-100)' } }
          }
        }
      });
    }

    // Societal Breakdown Bar Chart
    const breakdownCanvas = document.getElementById('societalBreakdownChart');
    if (!this.charts.societalBreakdown) {
      const avgEmerg = assessments.reduce((s, a) => s + a.emergency_impact_score, 0) / assessments.length;
      const avgEcon = assessments.reduce((s, a) => s + a.economic_impact_score, 0) / assessments.length;
      const avgEquity = assessments.reduce((s, a) => s + a.equity_vulnerability_score, 0) / assessments.length;
      const avgEnv = assessments.reduce((s, a) => s + a.environmental_impact_score, 0) / assessments.length;

      this.charts.societalBreakdown = new Chart(breakdownCanvas.getContext('2d'), {
        type: 'bar',
        data: {
          labels: ['Emergency Access', 'Economic Detour', 'SVI Equity', 'Environmental Spillover'],
          datasets: [{
            label: 'Average Network Impact Score',
            data: [avgEmerg, avgEcon, avgEquity, avgEnv],
            backgroundColor: ['#ef4444', '#f59e0b', '#8b5cf6', '#10b981']
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: { y: { min: 0, max: 100 } }
        }
      });
    }
  }

  renderTopsisTable(rankings) {
    const tbody = document.getElementById('topsisTableBody');
    tbody.innerHTML = '';
    rankings.slice(0, 15).forEach(r => {
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td><span class="badge ${r.rank <= 3 ? 'badge-danger' : 'badge-info'}">#${r.rank}</span></td>
        <td><strong>${r.asset_id}</strong></td>
        <td>${r.asset_name}</td>
        <td>${r.district}</td>
        <td><strong class="highlight-blue">${(r.topsis_closeness_score * 100).toFixed(1)}%</strong></td>
        <td><strong class="highlight-red">${r.cri.toFixed(1)}</strong></td>
        <td>${(r.failure_probability_1yr * 100).toFixed(1)}%</td>
        <td>${r.societal_impact.toFixed(1)}</td>
        <td>${(r.svi * 100).toFixed(0)}th</td>
      `;
      tbody.appendChild(tr);
    });
  }

  updateBudgetDisplay(val) {
    document.getElementById('budgetDisplay').innerText = '$' + (val / 1e6).toFixed(1) + 'M';
  }

  updateCrewDisplay(val) {
    document.getElementById('crewDisplay').innerText = Number(val).toLocaleString() + ' days';
  }

  updateWeightDisplay(elemId, val) {
    document.getElementById(elemId).innerText = val + '%';
  }

  async executeOptimization() {
    const status = document.getElementById('optimizerStatus');
    status.innerText = 'Executing Evolutionary Genetic Algorithm...';
    status.style.color = '#38bdf8';

    const budget = parseFloat(document.getElementById('budgetSlider').value);
    const crew = parseInt(document.getElementById('crewSlider').value);
    const wEmerg = parseFloat(document.getElementById('wEmergSlider').value) / 100.0;
    const wEquity = parseFloat(document.getElementById('wEquitySlider').value) / 100.0;

    try {
      const url = `/api/optimize?budget_limit=${budget}&max_crew_days=${crew}&emergency_weight=${wEmerg}&equity_weight=${wEquity}`;
      const res = await fetch(url, { method: 'POST' });
      const summary = await res.json();

      document.getElementById('optAllocatedBudget').innerText = '$' + (summary.total_budget_allocated_usd / 1e6).toFixed(2) + 'M';
      document.getElementById('optUtilPct').innerText = `Budget Utilization: ${summary.budget_utilization_pct.toFixed(1)}% of $${(budget / 1e6).toFixed(1)}M`;
      
      document.getElementById('optCrewDays').innerText = `${summary.total_crew_days_used} / ${crew}`;
      document.getElementById('optCrewLimit').innerText = `Crew Utilization: ${((summary.total_crew_days_used / crew) * 100).toFixed(1)}%`;

      document.getElementById('optShiGain').innerText = `+${(summary.average_network_shi_after - summary.average_network_shi_before).toFixed(1)} pts`;
      document.getElementById('optShiComparison').innerText = `Pre: ${summary.average_network_shi_before} → Post: ${summary.average_network_shi_after}`;

      document.getElementById('optRiskReduction').innerText = `-${summary.aggregate_risk_reduction_pct.toFixed(1)}%`;
      document.getElementById('optRiskComparison').innerText = `Pre CRI: ${summary.total_societal_risk_before.toFixed(0)} → Post: ${summary.total_societal_risk_after.toFixed(0)}`;

      document.getElementById('optTreatedBadge').innerText = `${summary.assets_treated_count} of ${summary.total_assets} Assets Treated`;

      // Render Schedule Table
      const schedBody = document.getElementById('scheduleTableBody');
      schedBody.innerHTML = '';
      summary.schedule.forEach(item => {
        const tr = document.createElement('tr');
        let badgeClass = 'badge-success';
        if (item.recommended_action === 'COMPLETE_RECONSTRUCTION') badgeClass = 'badge-danger';
        else if (item.recommended_action === 'MAJOR_RETROFIT') badgeClass = 'badge-warning';
        else if (item.recommended_action === 'DO_NOTHING') badgeClass = 'badge-info';

        tr.innerHTML = `
          <td><strong>${item.asset_id}</strong></td>
          <td>${item.asset_name}</td>
          <td><span class="badge ${badgeClass}">${item.action_label}</span></td>
          <td><strong>$${item.estimated_cost_usd.toLocaleString()}</strong></td>
          <td>${item.required_crew_days}d</td>
          <td>${item.expected_post_shi.toFixed(1)}</td>
          <td>${(item.post_failure_probability_1yr * 100).toFixed(1)}%</td>
          <td><strong class="highlight-blue">-${item.risk_reduction_achieved.toFixed(1)}</strong></td>
          <td>${item.societal_benefit_score.toFixed(1)}</td>
          <td><span class="badge badge-success">${item.benefit_cost_ratio.toFixed(2)}x</span></td>
        `;
        schedBody.appendChild(tr);
      });

      status.innerText = `Optimization converged successfully! Total risk reduced by ${summary.aggregate_risk_reduction_pct.toFixed(1)}%.`;
      status.style.color = '#10b981';
    } catch (err) {
      status.innerText = 'Optimization failed: ' + err.message;
      status.style.color = '#f43f5e';
    }
  }

  async executeScenarioSimulation() {
    const weather = parseFloat(document.getElementById('weatherSlider').value);
    const equity = parseFloat(document.getElementById('equityBoostSlider').value);
    const emerg = parseFloat(document.getElementById('emergBoostSlider').value);
    const budget = parseFloat(document.getElementById('simBudgetSlider').value);

    const body = {
      budget_limit_usd: budget,
      max_crew_days: 2000,
      extreme_weather_multiplier: weather,
      equity_weight_boost: equity,
      emergency_route_weight_boost: emerg,
      planning_horizon_years: 5
    };

    const res = await fetch('/api/simulate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body)
    });

    if (res.ok) {
      const simData = await res.json();
      const distData = simData.district_equity_distribution;
      const districts = Object.keys(distData);
      const allocated = districts.map(d => distData[d].allocated_investment_usd / 1e6);
      const svis = districts.map(d => distData[d].avg_svi * 100);

      // Render District Equity Chart
      const ctxDist = document.getElementById('districtEquityChart').getContext('2d');
      if (this.charts.distEquity) this.charts.distEquity.destroy();
      this.charts.distEquity = new Chart(ctxDist, {
        type: 'bar',
        data: {
          labels: districts,
          datasets: [
            { label: 'Allocated Capital ($M)', data: allocated, backgroundColor: '#38bdf8', yAxisID: 'y' },
            { label: 'District SVI (%tile)', data: svis, type: 'line', borderColor: '#f59e0b', backgroundColor: '#f59e0b', yAxisID: 'y1' }
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            y: { title: { display: true, text: 'Investment ($ Millions)' } },
            y1: { position: 'right', min: 0, max: 100, title: { display: true, text: 'SVI Percentile' } }
          }
        }
      });

      // Render Sim Risk Comparison Chart
      const opt = simData.optimization_summary;
      const ctxRisk = document.getElementById('simRiskComparisonChart').getContext('2d');
      if (this.charts.simRisk) this.charts.simRisk.destroy();
      this.charts.simRisk = new Chart(ctxRisk, {
        type: 'doughnut',
        data: {
          labels: ['Post-Intervention Remaining Risk', 'Achieved Risk Reduction'],
          datasets: [{
            data: [opt.total_societal_risk_after, opt.total_societal_risk_before - opt.total_societal_risk_after],
            backgroundColor: ['#f43f5e', '#10b981']
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false
        }
      });
    }
  }
}

// Global initialization
let app;
window.addEventListener('DOMContentLoaded', () => {
  app = new InfraRiskApp();
});
