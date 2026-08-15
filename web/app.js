/**
 * TrendWear Integrated S&OP Enterprise Suite
 * 100% Dynamic Multi-Vendor Engine & Role-Segmented Workspace Controller
 */

const API_BASE = "http://localhost:8000/api";
let currentView = "landing";
let activeRole = "executive";
let charts = {};
let currentSimWeek = 6;
let isPlayingSim = false;
let simInterval = null;

// Global Cached Datasets for Dynamic Filtering
let globalProcurementData = null;
let globalMaterialsData = null;
let globalDemandData = null;
let globalMarkdownData = null;

const USER_PROFILES = {
  executive: { name: "Elena Rostova", role: "Executive S&OP Chair", avatar: "👑", defaultView: "executive" },
  planner: { name: "Sarah Chen", role: "Demand & Merchandising Lead", avatar: "📈", defaultView: "demand" },
  merchandising: { name: "Sarah Chen", role: "Demand & Merchandising Lead", avatar: "📈", defaultView: "demand" },
  procurement: { name: "Marcus Vance", role: "Procurement & Sourcing Lead", avatar: "🛒", defaultView: "procurement" },
  production: { name: "David Miller", role: "Plant & Production Lead", avatar: "🏭", defaultView: "capacity" },
  logistics: { name: "Carlos Gomez", role: "Logistics & DC Network Lead", avatar: "🚚", defaultView: "inventory" }
};

document.addEventListener("DOMContentLoaded", async () => {
  lucide.createIcons();
  setupNavigation();
  setupEventListeners();
  await loadAllData();
});

// -------------------------------------------------------------
// AUTHENTICATION & ROLE WORKSPACE SEGMENTATION
// -------------------------------------------------------------
function fillLogin(username) {
  document.getElementById("login-username").value = username;
  document.getElementById("login-password").value = "password";
}

function handleFormLogin(e) {
  e.preventDefault();
  const username = document.getElementById("login-username").value.trim().toLowerCase();
  let mappedRole = "executive";

  if (username.includes("plan") || username.includes("merch") || username.includes("demand")) {
    mappedRole = "planner";
  } else if (username.includes("proc") || username.includes("source") || username.includes("vendor")) {
    mappedRole = "procurement";
  } else if (username.includes("prod") || username.includes("plant") || username.includes("factory")) {
    mappedRole = "production";
  } else if (username.includes("log") || username.includes("dist") || username.includes("dc")) {
    mappedRole = "logistics";
  } else if (username.includes("exec") || username.includes("chair") || username.includes("admin")) {
    mappedRole = "executive";
  }

  enterWorkspace(mappedRole);
}

function goToLandingPage() {
  currentView = "landing";
  document.getElementById("view-landing").classList.remove("hidden");
  document.getElementById("workspace-container").classList.add("hidden");
  
  document.getElementById("workspace-nav-controls").classList.add("hidden");
  document.getElementById("btn-landing-enter").classList.remove("hidden");
}

function enterWorkspace(role = "executive") {
  activeRole = role;
  const profile = USER_PROFILES[role] || USER_PROFILES.executive;

  // Update Header User Profile
  document.getElementById("active-user-name").textContent = profile.name;
  document.getElementById("active-user-role").textContent = profile.role;
  document.getElementById("user-avatar-icon").textContent = profile.avatar;

  // Toggle Viewports
  document.getElementById("view-landing").classList.add("hidden");
  document.getElementById("workspace-container").classList.remove("hidden");
  document.getElementById("workspace-container").classList.add("flex");

  document.getElementById("workspace-nav-controls").classList.remove("hidden");
  document.getElementById("btn-landing-enter").classList.add("hidden");

  // Apply Role-Based Sidebar Navigation Filters
  filterSidebarForRole(role);

  // Switch to Role's Default View
  switchView(profile.defaultView);
  loadActivityFeed();

  showToast(`Welcome, ${profile.name}`, `Authenticated as ${profile.role}. Workspace customized.`, "info");
}

function filterSidebarForRole(role) {
  const isExec = (role === "executive");
  const isPlanner = (role === "planner" || role === "merchandising");
  const isProcurement = (role === "procurement");
  const isProduction = (role === "production");
  const isLogistics = (role === "logistics");

  // Helper to toggle visibility of elements
  const setVisible = (elemId, visible) => {
    const el = document.getElementById(elemId);
    if (el) {
      if (visible) el.classList.remove("hidden");
      else el.classList.add("hidden");
    }
  };

  // Nav Groups
  setVisible("nav-group-demand", isExec || isPlanner);
  setVisible("nav-btn-executive", isExec);
  setVisible("nav-btn-demand", isExec || isPlanner);

  setVisible("nav-group-supply", isExec || isProcurement || isProduction);
  setVisible("nav-btn-materials", isExec || isProcurement);
  setVisible("nav-btn-procurement", isExec || isProcurement);
  setVisible("nav-btn-capacity", isExec || isProduction);

  setVisible("nav-group-logistics", isExec || isPlanner || isProduction || isLogistics);
  setVisible("nav-btn-inventory", isExec || isProduction || isLogistics);
  setVisible("nav-btn-sellthrough", isExec || isPlanner);

  setVisible("nav-group-governance", true); // All teams see Governance
  setVisible("nav-btn-financials", isExec);
  setVisible("nav-btn-scenario", isExec || isPlanner || isProcurement);
  setVisible("nav-btn-workflow", true); // Shared Decision Board visible to ALL roles
}

// -------------------------------------------------------------
// NAVIGATION & VIEW SWITCHER
// -------------------------------------------------------------
function setupNavigation() {
  const navButtons = document.querySelectorAll(".nav-item");
  navButtons.forEach(btn => {
    btn.addEventListener("click", () => {
      const view = btn.getAttribute("data-view");
      switchView(view);
    });
  });
}

function switchView(viewName) {
  currentView = viewName;
  document.querySelectorAll(".nav-item").forEach(b => {
    if (b.getAttribute("data-view") === viewName) {
      b.classList.add("active");
    } else {
      b.classList.remove("active");
    }
  });

  document.querySelectorAll(".view-panel").forEach(panel => {
    if (panel.id === `view-${viewName}`) {
      panel.classList.remove("hidden");
    } else {
      panel.classList.add("hidden");
    }
  });

  window.dispatchEvent(new Event("resize"));
}

// -------------------------------------------------------------
// EVENT LISTENERS & REAL-TIME CONTROLS
// -------------------------------------------------------------
function setupEventListeners() {
  // Scenario Simulator Live Inputs
  document.getElementById("sim-demand").addEventListener("input", (e) => {
    const val = e.target.value;
    document.getElementById("sim-demand-val").textContent = `${val >= 0 ? "+" : ""}${val}%`;
  });
  document.getElementById("sim-leadtime").addEventListener("input", (e) => {
    const val = e.target.value;
    document.getElementById("sim-leadtime-val").textContent = `+${val} Week${val != 1 ? "s" : ""}`;
  });
  document.getElementById("sim-s004").addEventListener("input", (e) => {
    const val = e.target.value;
    document.getElementById("sim-s004-val").textContent = `${val}%`;
  });

  document.getElementById("btn-run-sim").addEventListener("click", runLiveSimulation);

  // Capacity Shifter
  document.getElementById("btn-execute-shift").addEventListener("click", executeCapacityShift);

  // 6-Week Sim Playback
  document.getElementById("btn-sim-play").addEventListener("click", toggleSimPlayback);
  document.getElementById("btn-sim-prev").addEventListener("click", () => stepSimWeek(-1));
  document.getElementById("btn-sim-next").addEventListener("click", () => stepSimWeek(1));

  // Search in Demand Table
  const searchInput = document.getElementById("demand-search");
  if (searchInput) {
    searchInput.addEventListener("input", (e) => {
      const q = e.target.value.toLowerCase();
      let visibleCount = 0;
      document.querySelectorAll("#demand-table tbody tr").forEach(row => {
        const txt = row.textContent.toLowerCase();
        const matches = txt.includes(q);
        row.style.display = matches ? "" : "none";
        if (matches) visibleCount++;
      });
    });
  }
}

function applyPreset(demand, leadtime, s004Cap) {
  document.getElementById("sim-demand").value = demand;
  document.getElementById("sim-demand-val").textContent = `${demand >= 0 ? "+" : ""}${demand}%`;
  document.getElementById("sim-leadtime").value = leadtime;
  document.getElementById("sim-leadtime-val").textContent = `+${leadtime} Week${leadtime != 1 ? "s" : ""}`;
  document.getElementById("sim-s004").value = s004Cap;
  document.getElementById("sim-s004-val").textContent = `${s004Cap}%`;
  runLiveSimulation();
  showToast("Preset Applied", `Simulating demand: ${demand}% | High-Risk Vendor: ${s004Cap}%`, "info");
}

function resetScenarioBaseline() {
  applyPreset(0, 0, 0);
  showToast("Baseline Restored", "All scenario shocks reset to standard operating plan.", "info");
}

// -------------------------------------------------------------
// REAL-TIME ACTIVITY STREAM DRAWER
// -------------------------------------------------------------
function toggleActivityDrawer() {
  const drawer = document.getElementById("activity-drawer");
  drawer.classList.toggle("translate-x-full");
  loadActivityFeed();
}

async function loadActivityFeed() {
  try {
    const res = await fetch(`${API_BASE}/activity/feed`);
    const data = await res.json();
    const container = document.getElementById("activity-feed-container");
    container.innerHTML = data.feed.map(evt => {
      const typeBg = evt.type === 'danger' ? 'border-rose-600/40 bg-rose-950/20' : (evt.type === 'warning' ? 'border-amber-600/40 bg-amber-950/20' : 'border-indigo-500/30 bg-slate-950');
      const textCol = evt.type === 'danger' ? 'text-rose-400' : (evt.type === 'warning' ? 'text-amber-400' : 'text-indigo-300');
      return `
        <div class="p-2.5 rounded-lg border ${typeBg} text-xs space-y-1">
          <div class="flex justify-between items-center">
            <span class="font-mono text-[10px] text-slate-400">${evt.time}</span>
            <span class="font-semibold text-[11px] ${textCol}">${evt.role}</span>
          </div>
          <div class="text-slate-200 text-[11px]">${evt.action}</div>
        </div>
      `;
    }).join("");
  } catch (err) {
    console.error("Activity feed error:", err);
  }
}

// -------------------------------------------------------------
// 100% DYNAMIC SOURCING ALLOCATION ENGINE (PROCUREMENT)
// -------------------------------------------------------------
function populateFabricDropdown(pricingMatrix) {
  const select = document.getElementById("sourcing-fabric-select");
  if (!select || !pricingMatrix) return;

  const fabrics = [...new Set(pricingMatrix.map(m => `${m.fabric_id} - ${m.fabric_name}`))];
  select.innerHTML = fabrics.map(f => {
    const fabId = f.split(" - ")[0];
    return `<option value="${fabId}">${f}</option>`;
  }).join("");

  loadDynamicFabricSliders();
}

function loadDynamicFabricSliders() {
  if (!globalProcurementData || !globalProcurementData.supplier_fabric_matrix) return;
  const select = document.getElementById("sourcing-fabric-select");
  const selectedFabId = select ? select.value : "FAB_001";

  const matrix = globalProcurementData.supplier_fabric_matrix;
  const qualified = matrix.filter(m => m.fabric_id === selectedFabId);

  // Find fabric details from globalMaterialsData
  let netReq = 35000;
  let fabName = "Material";
  let leadTime = "4.5";
  if (globalMaterialsData) {
    const fabMeta = globalMaterialsData.find(f => f.fabric_id === selectedFabId);
    if (fabMeta) {
      netReq = fabMeta.total_net_req || fabMeta.total_gross_req || 35000;
      fabName = fabMeta.fabric_name;
      leadTime = fabMeta.lead_time_weeks;
    }
  }

  // Update Summary Banner
  const bannerName = document.getElementById("banner-fab-name");
  if (bannerName) bannerName.textContent = `${selectedFabId} (${fabName})`;
  const bannerNet = document.getElementById("banner-net-req");
  if (bannerNet) bannerNet.textContent = `${netReq.toLocaleString()} Meters`;
  const bannerLt = document.getElementById("banner-lead-time");
  if (bannerLt) bannerLt.textContent = `${leadTime} Weeks`;

  const container = document.getElementById("dynamic-sourcing-sliders");
  if (!container) return;

  if (qualified.length === 0) {
    container.innerHTML = `<div class="text-xs text-slate-400 col-span-3">No qualified suppliers mapped.</div>`;
    return;
  }

  // Equal initial share
  const initialShare = Math.round(100 / qualified.length);

  container.innerHTML = qualified.map((v, idx) => {
    const isRisky = v.computed_risk_category === "HIGH";
    const accentCol = isRisky ? "accent-rose-500" : (idx === 0 ? "accent-emerald-500" : "accent-indigo-500");
    const textCol = isRisky ? "text-rose-400" : (idx === 0 ? "text-emerald-400" : "text-indigo-400");
    return `
      <div class="space-y-1">
        <div class="flex justify-between items-center text-xs">
          <span class="text-slate-300 font-semibold">${v.supplier_name} (${v.supplier_id}):</span>
          <span class="font-mono ${textCol} font-bold dynamic-slider-val" id="dyn-val-${v.supplier_id}">${initialShare}%</span>
        </div>
        <input type="range" id="dyn-slider-${v.supplier_id}" min="0" max="100" value="${initialShare}" step="5" class="w-full ${accentCol} dynamic-vendor-slider" data-supplier="${v.supplier_id}" data-otd="${v.otd_score}" data-cost="${v.unit_cost_per_meter}" data-moq="${v.moq_meters}" oninput="recalcDynamicSourcingMetrics()">
        <div class="flex justify-between items-center text-[10px] font-mono">
          <span class="text-slate-400">$${v.unit_cost_per_meter}/m • OTD ${(v.otd_score * 100).toFixed(0)}%</span>
          <span class="text-slate-400" id="dyn-moq-badge-${v.supplier_id}">MOQ: ${v.moq_meters.toLocaleString()}m</span>
        </div>
      </div>
    `;
  }).join("");

  recalcDynamicSourcingMetrics();
}

function recalcDynamicSourcingMetrics() {
  const sliders = document.querySelectorAll(".dynamic-vendor-slider");
  const select = document.getElementById("sourcing-fabric-select");
  const selectedFabId = select ? select.value : "FAB_001";

  let netReq = 35000;
  if (globalMaterialsData) {
    const fabMeta = globalMaterialsData.find(f => f.fabric_id === selectedFabId);
    if (fabMeta) netReq = fabMeta.total_net_req || fabMeta.total_gross_req || 35000;
  }

  let totalShare = 0;
  let weightedRisk = 0;
  let weightedCost = 0;
  let activeVendors = 0;
  let moqViolations = 0;

  sliders.forEach(slider => {
    const val = parseInt(slider.value);
    const supId = slider.getAttribute("data-supplier");
    const otd = parseFloat(slider.getAttribute("data-otd"));
    const cost = parseFloat(slider.getAttribute("data-cost"));
    const moq = parseInt(slider.getAttribute("data-moq")) || 2500;

    const allocatedMeters = Math.round(netReq * (val / 100));

    const valEl = document.getElementById(`dyn-val-${supId}`);
    if (valEl) valEl.textContent = `${val}% (${allocatedMeters.toLocaleString()}m)`;

    // Live MOQ validation badge
    const moqBadge = document.getElementById(`dyn-moq-badge-${supId}`);
    if (moqBadge) {
      if (val > 0 && allocatedMeters < moq) {
        moqBadge.innerHTML = `<span class="badge badge-rose text-[9px]">⚠️ Sub-MOQ (${allocatedMeters.toLocaleString()}m < ${moq.toLocaleString()}m)</span>`;
        moqViolations++;
      } else {
        moqBadge.innerHTML = `<span class="text-slate-400">MOQ: ${moq.toLocaleString()}m</span>`;
      }
    }

    totalShare += val;
    weightedRisk += (val * (1.0 - otd));
    weightedCost += (val * cost);
    if (val > 0) activeVendors++;
  });

  if (totalShare === 0) totalShare = 1;
  const avgRiskPct = ((weightedRisk / totalShare) * 100).toFixed(1);
  const avgCost = (weightedCost / totalShare).toFixed(2);
  const otd = (100 - avgRiskPct).toFixed(1);

  // Update allocated share banner
  const bannerAlloc = document.getElementById("banner-total-alloc");
  if (bannerAlloc) {
    bannerAlloc.textContent = `${totalShare}%`;
    bannerAlloc.className = totalShare === 100 ? "text-emerald-400 font-bold" : "text-amber-400 font-bold";
  }

  const riskEl = document.getElementById("live-risk-index");
  if (riskEl) {
    if (moqViolations > 0) {
      riskEl.textContent = `MOQ Warning (${moqViolations} Sub-MOQ)`;
      riskEl.className = 'text-rose-400 font-bold';
    } else {
      riskEl.textContent = `${avgRiskPct}% (${avgRiskPct > 20 ? 'High Risk' : (avgRiskPct > 10 ? 'Moderate' : 'Low')})`;
      riskEl.className = avgRiskPct > 20 ? 'text-rose-400 font-bold' : (avgRiskPct > 10 ? 'text-amber-400 font-bold' : 'text-emerald-400 font-bold');
    }
  }

  const costEl = document.getElementById("live-cost-index");
  if (costEl) costEl.textContent = `$${avgCost} / m (Total: ${totalShare}%)`;

  const otdEl = document.getElementById("live-otd-index");
  if (otdEl) otdEl.textContent = `${otd}%`;

  const divEl = document.getElementById("live-div-index");
  if (divEl) divEl.textContent = `${activeVendors} Active Vendors`;
}

// -------------------------------------------------------------
// UNIVERSAL PURCHASE ORDER MODAL & EXPORT ACTIONS
// -------------------------------------------------------------
function openPOModal() {
  openPOModalFor("S001", "Apex Textile Mills", "FAB_001", "Silk Blend Weave", 10000, 18.50, "W05");
}

function openPOModalFor(supplierId, supplierName, fabricId, fabricName, orderQty, unitPrice, period) {
  const docId = `PO-2026-${fabricId}-${Math.floor(1000 + Math.random() * 9000)}`;
  const totalCost = (orderQty * unitPrice);

  document.getElementById("po-doc-id").textContent = `${docId} • Authorized by S&OP Optimizer`;
  document.getElementById("po-vendor-name").textContent = `${supplierName} (${supplierId})`;
  document.getElementById("po-delivery-period").textContent = `${period}`;
  document.getElementById("po-fabric-name").textContent = `${fabricId} (${fabricName || 'Material'})`;
  document.getElementById("po-order-qty").textContent = `${orderQty.toLocaleString()} Meters`;
  document.getElementById("po-unit-price").textContent = `$${unitPrice.toFixed(2)} / m`;
  document.getElementById("po-total-cost").textContent = `$${totalCost.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}`;

  document.getElementById("po-modal").classList.remove("hidden");
}

function closePOModal() {
  document.getElementById("po-modal").classList.add("hidden");
}

function downloadPOCSV() {
  const docId = document.getElementById("po-doc-id").textContent.split(" • ")[0];
  const vendor = document.getElementById("po-vendor-name").textContent;
  const period = document.getElementById("po-delivery-period").textContent;
  const material = document.getElementById("po-fabric-name").textContent;
  const qty = document.getElementById("po-order-qty").textContent.replace(/[^0-9]/g, "");
  const price = document.getElementById("po-unit-price").textContent.replace(/[^0-9.]/g, "");
  const total = document.getElementById("po-total-cost").textContent.replace(/[^0-9.]/g, "");

  const csvContent = "data:text/csv;charset=utf-8," + 
    "PO_Number,Vendor,Delivery_Period,Material,Order_Qty_Meters,Unit_Price_USD,Total_Cost_USD\n" +
    `"${docId}","${vendor}","${period}","${material}",${qty},${price},${total}\n`;

  const encodedUri = encodeURI(csvContent);
  const link = document.createElement("a");
  link.setAttribute("href", encodedUri);
  link.setAttribute("download", `${docId}.csv`);
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);

  showToast("PO Downloaded", `${docId}.csv exported successfully.`, "success");
}

function copyPOText() {
  const docId = document.getElementById("po-doc-id").textContent.split(" • ")[0];
  const vendor = document.getElementById("po-vendor-name").textContent;
  const material = document.getElementById("po-fabric-name").textContent;
  const qty = document.getElementById("po-order-qty").textContent;
  const total = document.getElementById("po-total-cost").textContent;

  const summary = `TrendWear S&OP Purchase Order\nPO: ${docId}\nVendor: ${vendor}\nMaterial: ${material}\nQuantity: ${qty}\nTotal Cost: ${total}`;
  navigator.clipboard.writeText(summary).then(() => {
    showToast("Copied to Clipboard", "Purchase Order summary copied.", "success");
  });
}

function confirmReleasePO() {
  const docId = document.getElementById("po-doc-id").textContent.split(" • ")[0];
  const vendor = document.getElementById("po-vendor-name").textContent;
  const material = document.getElementById("po-fabric-name").textContent;

  closePOModal();
  showToast("PO Released to Vendor EDI", `${docId} dispatched to ${vendor} for ${material}.`, "success");
}

// -------------------------------------------------------------
// LIVE INLINE DEMAND OVERRIDE (MERCHANDISING)
// -------------------------------------------------------------
function openDemandTuneModal(skuId, currentDemand) {
  document.getElementById("tune-sku-id").value = skuId;
  document.getElementById("tune-new-demand").value = currentDemand;
  document.getElementById("demand-tune-modal").classList.remove("hidden");
}

function closeDemandTuneModal() {
  document.getElementById("demand-tune-modal").classList.add("hidden");
}

async function submitDemandTune() {
  const skuId = document.getElementById("tune-sku-id").value;
  const newDemand = parseInt(document.getElementById("tune-new-demand").value);

  const res = await fetch(`${API_BASE}/demand/override`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ sku_id: skuId, new_demand: newDemand })
  });
  const data = await res.json();

  closeDemandTuneModal();
  showToast("Demand Forecast Updated", `${skuId} demand adjusted to ${newDemand.toLocaleString()} units. BOM & Margins recalculated.`, "success");
  await loadAllData();
  await loadActivityFeed();
}

// -------------------------------------------------------------
// 100% DYNAMIC SKU MARKDOWN SIMULATOR
// -------------------------------------------------------------
function populateMarkdownSkuDropdown(recommendations) {
  const select = document.getElementById("markdown-sku-select");
  if (!select || !recommendations) return;

  select.innerHTML = recommendations.map(s => `
    <option value="${s.sku_id}">${s.sku_id} - ${s.category} (${s.mover_class})</option>
  `).join("");

  updateDynamicMarkdownSim();
}

function updateDynamicMarkdownSim() {
  if (!globalMarkdownData) return;
  const select = document.getElementById("markdown-sku-select");
  const selectedSkuId = select ? select.value : "SKU_001";
  const depth = parseInt(document.getElementById("mark-depth-slider").value);

  document.getElementById("mark-slider-val").textContent = `${depth}% Discount`;

  const item = globalMarkdownData.find(s => s.sku_id === selectedSkuId) || globalMarkdownData[0];
  const excessUnits = item.inventory_value_at_risk > 0 ? (item.inventory_value_at_risk / 35.0) : 5000;
  const baseUnitCost = 35.00;
  const clearancePct = Math.min(1.0, 0.20 + (depth * 0.016));
  const unitsSold = Math.round(excessUnits * clearancePct);
  const capitalRecovered = unitsSold * (baseUnitCost * (1 - depth/100));
  const velocityLift = Math.round((clearancePct - 0.20) * 450);

  document.getElementById("mark-capital-recovered").textContent = `$${capitalRecovered.toLocaleString(undefined, {maximumFractionDigits: 0})}`;
  document.getElementById("mark-velocity-lift").textContent = `+${velocityLift}%`;
}

async function executeMarkdownClearance() {
  const select = document.getElementById("markdown-sku-select");
  const skuId = select ? select.value : "SKU_001";
  const depth = parseInt(document.getElementById("mark-depth-slider").value) / 100;
  const capital = parseFloat(document.getElementById("mark-capital-recovered").textContent.replace(/[^0-9.-]+/g,""));

  const res = await fetch(`${API_BASE}/markdown/execute`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ sku_id: skuId, discount_pct: depth, recovered_capital: capital })
  });
  const data = await res.json();

  showToast("Markdown Clearance Approved", `Recovers $${capital.toLocaleString()} working capital for ${skuId}.`, "success");
  await loadActivityFeed();
  await loadFinancialsData();
}

// -------------------------------------------------------------
// 6-WEEK SIMULATION PLAYBACK (TIME-TRAVEL)
// -------------------------------------------------------------
function toggleSimPlayback() {
  const btn = document.getElementById("btn-sim-play");
  if (!isPlayingSim) {
    isPlayingSim = true;
    btn.innerHTML = `<i data-lucide="pause" class="w-3 h-3 text-amber-400"></i> Pause`;
    lucide.createIcons();
    currentSimWeek = 1;
    stepSimWeek(0);
    simInterval = setInterval(() => {
      if (currentSimWeek < 6) {
        stepSimWeek(1);
      } else {
        clearInterval(simInterval);
        isPlayingSim = false;
        btn.innerHTML = `<i data-lucide="play" class="w-3 h-3"></i> Play W1-W6`;
        lucide.createIcons();
        showToast("Simulation Complete", "6-Week Fast-Fashion Lifecycle Reconciled.", "success");
      }
    }, 1800);
  } else {
    clearInterval(simInterval);
    isPlayingSim = false;
    btn.innerHTML = `<i data-lucide="play" class="w-3 h-3"></i> Play W1-W6`;
    lucide.createIcons();
  }
}

function stepSimWeek(delta) {
  currentSimWeek = Math.max(1, Math.min(6, currentSimWeek + delta));
  document.getElementById("current-sim-week-badge").textContent = `Week ${currentSimWeek} of 6`;

  const weekEvents = {
    1: "Week 1: Long-lead fabric orders released to Tier-1 global suppliers.",
    2: "Week 2: Factory capacity assigned across 5 manufacturing hubs.",
    3: "Week 3: In-season sell-through flags fast/slow mover signals.",
    4: "Week 4: Sourcing MILP optimizer solves fabric arrivals and shifts overloaded plant volume.",
    5: "Week 5: Plant P003 production reaches peak; rebalances 1,440 units to P004 flex line.",
    6: "Week 6: Seasonal Jackets demand peak met; markdowns clear remaining inventory."
  };

  showToast(`Horizon: Week ${currentSimWeek}`, weekEvents[currentSimWeek], "info");
}

// -------------------------------------------------------------
// FLOATING TOAST NOTIFICATIONS
// -------------------------------------------------------------
function showToast(title, msg, type = "info") {
  const toast = document.getElementById("action-toast");
  const tTitle = document.getElementById("toast-title");
  const tMsg = document.getElementById("toast-msg");
  const tIcon = document.getElementById("toast-icon");

  tTitle.textContent = title;
  tMsg.textContent = msg;

  if (type === "success") {
    tIcon.className = "p-1.5 rounded-lg bg-emerald-500/20 text-emerald-400";
    toast.className = "fixed bottom-6 right-6 z-50 glass-card p-3.5 px-4 border-emerald-500/40 bg-slate-900 shadow-2xl flex items-center gap-3 transition-all duration-300";
  } else {
    tIcon.className = "p-1.5 rounded-lg bg-indigo-500/20 text-indigo-400";
    toast.className = "fixed bottom-6 right-6 z-50 glass-card p-3.5 px-4 border-indigo-500/40 bg-slate-900 shadow-2xl flex items-center gap-3 transition-all duration-300";
  }

  toast.classList.remove("hidden");
  setTimeout(() => {
    toast.classList.add("hidden");
  }, 4000);
}

// -------------------------------------------------------------
// DATA LOADING PIPELINE
// -------------------------------------------------------------
async function loadAllData() {
  try {
    await Promise.all([
      loadDashboard(),
      loadDemandData(),
      loadMaterialsData(),
      loadProcurementData(),
      loadCapacityData(),
      loadInventoryData(),
      loadSellThroughData(),
      loadFinancialsData(),
      loadWorkflowData()
    ]);
    await runLiveSimulation();
  } catch (err) {
    console.error("Data loading error:", err);
  }
}

// -------------------------------------------------------------
// VIEW 1: EXECUTIVE COCKPIT
// -------------------------------------------------------------
async function loadDashboard() {
  const res = await fetch(`${API_BASE}/dashboard`);
  const data = await res.json();

  document.getElementById("kpi-revenue").textContent = `$${data.kpis.gross_revenue.toLocaleString()}`;
  document.getElementById("kpi-margin").textContent = `$${data.kpis.net_gross_margin.toLocaleString()}`;
  document.getElementById("kpi-margin-pct").textContent = `${data.kpis.gross_margin_pct}%`;
  document.getElementById("kpi-capacity").textContent = `${data.kpis.overall_capacity_utilization}%`;
  document.getElementById("kpi-cogs").textContent = `$${data.kpis.material_cogs.toLocaleString()}`;

  const risksContainer = document.getElementById("top-risks-container");
  risksContainer.innerHTML = data.top_risks.map(r => `
    <div class="p-2.5 rounded-lg bg-slate-900 border border-slate-800 text-xs flex justify-between items-center">
      <div>
        <div class="font-semibold text-slate-200">${r.title}</div>
        <div class="text-[11px] text-slate-400">${r.detail}</div>
      </div>
      <span class="badge ${r.level === 'HIGH' ? 'badge-rose' : 'badge-amber'}">${r.level}</span>
    </div>
  `).join("");

  renderDemandCapacityChart();
}

function renderDemandCapacityChart() {
  const ctx = document.getElementById("chart-demand-capacity");
  if (!ctx) return;
  if (charts.demandCapacity) charts.demandCapacity.destroy();

  charts.demandCapacity = new Chart(ctx, {
    type: "line",
    data: {
      labels: ["W01", "W02", "W03", "W04", "W05", "W06", "W07", "W08", "W09", "W10", "W11", "W12"],
      datasets: [
        {
          label: "Total S&OP Demand (Units)",
          data: [42000, 44500, 43800, 45200, 47000, 58400, 46000, 44000, 43500, 42000, 41000, 45000],
          borderColor: "#6366f1",
          backgroundColor: "rgba(99, 102, 241, 0.12)",
          fill: true,
          tension: 0.3,
          borderWidth: 2.5
        },
        {
          label: "Plant Available Capacity",
          data: [58000, 58000, 58000, 58000, 58000, 58000, 58000, 58000, 58000, 58000, 58000, 58000],
          borderColor: "#10b981",
          borderDash: [5, 5],
          borderWidth: 2,
          pointRadius: 0
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { labels: { color: "#94a3b8", font: { size: 11 } } } },
      scales: {
        x: { grid: { color: "rgba(51, 65, 85, 0.2)" }, ticks: { color: "#94a3b8" } },
        y: { grid: { color: "rgba(51, 65, 85, 0.2)" }, ticks: { color: "#94a3b8" } }
      }
    }
  });
}

// -------------------------------------------------------------
// VIEW 2: DEMAND PLANNING
// -------------------------------------------------------------
async function loadDemandData() {
  const res = await fetch(`${API_BASE}/demand`);
  const data = await res.json();
  globalDemandData = data.skus;

  const catMap = {};
  data.categories.forEach(c => {
    if (!catMap[c.category]) catMap[c.category] = [];
    if (c.period.startsWith("W") && parseInt(c.period.slice(1)) <= 6) {
      catMap[c.category].push(c.forecasted_demand_units);
    }
  });

  const catColors = ["#6366f1", "#ec4899", "#8b5cf6", "#3b82f6", "#10b981", "#f59e0b"];
  const catDatasets = Object.keys(catMap).map((cat, i) => ({
    label: cat,
    data: catMap[cat],
    backgroundColor: catColors[i % catColors.length],
    borderRadius: 3
  }));

  const ctxCat = document.getElementById("chart-category-demand");
  if (ctxCat) {
    if (charts.categoryDemand) charts.categoryDemand.destroy();
    charts.categoryDemand = new Chart(ctxCat, {
      type: "bar",
      data: {
        labels: ["W01", "W02", "W03", "W04", "W05", "W06"],
        datasets: catDatasets
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          x: { stacked: true, grid: { color: "rgba(51, 65, 85, 0.2)" }, ticks: { color: "#94a3b8" } },
          y: { stacked: true, grid: { color: "rgba(51, 65, 85, 0.2)" }, ticks: { color: "#94a3b8" } }
        },
        plugins: { legend: { labels: { color: "#94a3b8", font: { size: 10 } } } }
      }
    });
  }

  const ctxReg = document.getElementById("chart-regional-demand");
  if (ctxReg) {
    if (charts.regionalDemand) charts.regionalDemand.destroy();
    charts.regionalDemand = new Chart(ctxReg, {
      type: "doughnut",
      data: {
        labels: ["North America", "Europe", "Asia-Pacific", "Latin America"],
        datasets: [{
          data: [38, 32, 20, 10],
          backgroundColor: ["#6366f1", "#8b5cf6", "#ec4899", "#10b981"],
          borderWidth: 0
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { position: "bottom", labels: { color: "#94a3b8", font: { size: 10 } } } }
      }
    });
  }

  const tbody = document.querySelector("#demand-table tbody");
  if (tbody) {
    tbody.innerHTML = data.skus.map(s => `
      <tr>
        <td class="font-mono font-semibold text-indigo-300">${s.sku_id}</td>
        <td>${s.sku_name}</td>
        <td><span class="badge badge-indigo">${s.category}</span></td>
        <td class="font-mono">$${s.unit_price}</td>
        <td class="font-mono font-bold">${s.total_demand.toLocaleString()}</td>
        <td class="font-mono text-emerald-400">$${(s.total_demand * s.unit_price).toLocaleString()}</td>
        <td>
          <button class="px-2 py-1 rounded bg-slate-800 hover:bg-slate-700 text-indigo-300 border border-slate-700 text-[10px] font-semibold" onclick="openDemandTuneModal('${s.sku_id}', ${s.total_demand})">
            Tune
          </button>
        </td>
      </tr>
    `).join("");
  }
}

// -------------------------------------------------------------
// VIEW 3: BOM & MATERIAL NETTING
// -------------------------------------------------------------
async function loadMaterialsData() {
  const res = await fetch(`${API_BASE}/materials`);
  const data = await res.json();
  globalMaterialsData = data.fabric_summary;

  const tbody = document.querySelector("#mrp-summary-table tbody");
  if (tbody) {
    tbody.innerHTML = data.fabric_summary.map(f => {
      const cov = Math.min(100, Math.max(0, f.avg_inv_coverage));
      const meterColor = cov >= 80 ? 'meter-fill-emerald' : (cov >= 40 ? 'meter-fill-amber' : 'meter-fill-rose');
      return `
      <tr>
        <td class="font-mono font-bold text-indigo-300">${f.fabric_id}</td>
        <td>${f.fabric_name}</td>
        <td><span class="badge ${f.criticality === 'HIGH' ? 'badge-rose' : 'badge-indigo'}">${f.criticality}</span></td>
        <td class="font-mono">${f.lead_time_weeks} wks</td>
        <td class="font-mono">${f.total_gross_req.toLocaleString()}</td>
        <td class="font-mono font-bold ${f.total_net_req > 0 ? 'text-amber-300' : 'text-emerald-400'}">${f.total_net_req.toLocaleString()}</td>
        <td>
          <div class="micro-meter">
            <div class="meter-track"><div class="${meterColor}" style="width: ${cov}%"></div></div>
            <span class="font-mono text-[10px]">${f.avg_inv_coverage.toFixed(0)}%</span>
          </div>
        </td>
        <td>
          <span class="badge ${f.total_net_req > 0 ? 'badge-amber' : 'badge-emerald'}">
            ${f.total_net_req > 0 ? 'DEFICIT' : 'COVERED'}
          </span>
        </td>
      </tr>
    `}).join("");
  }
}

// -------------------------------------------------------------
// VIEW 4: SOURCING & PROCUREMENT OPTIMIZER
// -------------------------------------------------------------
async function loadProcurementData() {
  const res = await fetch(`${API_BASE}/procurement`);
  const data = await res.json();
  globalProcurementData = data;

  // Populate dynamic fabric dropdown
  populateFabricDropdown(data.supplier_fabric_matrix);

  const tbodyAlloc = document.querySelector("#supplier-alloc-table tbody");
  if (tbodyAlloc) {
    tbodyAlloc.innerHTML = data.supplier_allocation_summary.map(s => `
      <tr>
        <td class="font-mono font-bold text-indigo-300">${s.supplier_id}</td>
        <td>${s.supplier_name}</td>
        <td><span class="badge ${s.supplier_risk_category === 'HIGH' ? 'badge-rose' : 'badge-emerald'}">${s.supplier_risk_category}</span></td>
        <td class="font-mono font-bold">${s.total_allocated_meters.toLocaleString()}</td>
        <td class="font-mono text-emerald-400">$${s.total_purchase_cost.toLocaleString()}</td>
        <td class="font-mono">${s.mean_risk_score.toFixed(1)}</td>
      </tr>
    `).join("");
  }

  const ctx = document.getElementById("chart-supplier-share");
  if (ctx) {
    if (charts.supplierShare) charts.supplierShare.destroy();
    charts.supplierShare = new Chart(ctx, {
      type: "doughnut",
      data: {
        labels: data.supplier_allocation_summary.map(s => s.supplier_name),
        datasets: [{
          data: data.supplier_allocation_summary.map(s => s.total_allocated_meters),
          backgroundColor: ["#6366f1", "#10b981", "#ec4899", "#f59e0b", "#8b5cf6", "#3b82f6", "#14b8a6", "#f43f5e"],
          borderWidth: 0
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { position: "bottom", labels: { color: "#94a3b8", font: { size: 9 } } } }
      }
    });
  }

  const tbodyPO = document.querySelector("#procurement-plan-table tbody");
  if (tbodyPO) {
    tbodyPO.innerHTML = data.procurement_plan.map(p => `
      <tr>
        <td class="font-mono font-semibold">${p.fabric_id}</td>
        <td>${p.supplier_name}</td>
        <td class="font-mono">${p.period}</td>
        <td class="font-mono font-bold">${p.recommended_order_qty.toLocaleString()}</td>
        <td class="font-mono">$${p.unit_price}</td>
        <td class="font-mono text-emerald-400">$${p.purchase_cost.toLocaleString()}</td>
        <td class="font-mono text-amber-300 font-bold">${p.po_release_week}</td>
        <td class="font-mono text-indigo-300">${p.expected_arrival_week}</td>
        <td><span class="badge ${p.delivery_risk === 'HIGH' ? 'badge-rose' : 'badge-emerald'}">${p.delivery_risk}</span></td>
        <td>
          <button class="px-2 py-0.5 rounded bg-indigo-600/30 hover:bg-indigo-600 text-indigo-200 text-[10px] font-semibold transition" onclick="openPOModalFor('${p.supplier_id}', '${p.supplier_name}', '${p.fabric_id}', 'Raw Fabric', ${p.recommended_order_qty}, ${p.unit_price}, '${p.expected_arrival_week}')">
            Generate PO
          </button>
        </td>
      </tr>
    `).join("");
  }
}

// -------------------------------------------------------------
// VIEW 5: PLANT CAPACITY & BOTTLENECK SHIFTING
// -------------------------------------------------------------
async function loadCapacityData() {
  const res = await fetch(`${API_BASE}/capacity`);
  const data = await res.json();

  const tbody = document.querySelector("#capacity-table tbody");
  if (tbody) {
    tbody.innerHTML = data.plant_capacity.map(c => {
      const util = c.utilization_pct;
      const meterColor = util > 100 ? 'meter-fill-rose' : (util >= 85 ? 'meter-fill-amber' : 'meter-fill-emerald');
      const width = Math.min(100, util);
      return `
      <tr class="${c.capacity_status === 'OVERLOADED' ? 'bg-rose-950/30' : ''}">
        <td class="font-mono font-bold text-indigo-300">${c.plant_id}</td>
        <td>${c.plant_name}</td>
        <td>${c.region}</td>
        <td class="font-mono">${c.period}</td>
        <td class="font-mono">${c.max_units_capacity.toLocaleString()}</td>
        <td class="font-mono">${c.already_allocated_units.toLocaleString()}</td>
        <td>
          <div class="micro-meter">
            <div class="meter-track"><div class="${meterColor}" style="width: ${width}%"></div></div>
            <span class="font-mono font-bold text-[11px] ${util > 100 ? 'text-rose-400' : 'text-slate-200'}">${util}%</span>
          </div>
        </td>
        <td>
          ${c.capacity_status === 'OVERLOADED' 
            ? `<button class="px-2 py-0.5 rounded bg-rose-600 hover:bg-rose-500 text-white text-[10px] font-bold" onclick="rebalanceP003()">Rebalance</button>`
            : `<span class="badge badge-emerald text-[10px]">Optimal</span>`}
        </td>
      </tr>
    `}).join("");
  }
}

async function rebalanceP003() {
  document.getElementById("shift-source").value = "P003";
  document.getElementById("shift-target").value = "P004";
  document.getElementById("shift-period").value = "W06";
  document.getElementById("shift-units").value = "1440";
  await executeCapacityShift();
}

async function executeCapacityShift() {
  const source = document.getElementById("shift-source").value;
  const target = document.getElementById("shift-target").value;
  const period = document.getElementById("shift-period").value;
  const units = parseInt(document.getElementById("shift-units").value);

  const res = await fetch(`${API_BASE}/capacity/shift`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      source_plant: source,
      target_plant: target,
      period: period,
      units_to_shift: units
    })
  });
  const data = await res.json();
  const fb = document.getElementById("shift-feedback");
  if (fb) {
    fb.classList.remove("hidden");
    fb.textContent = `✓ ${data.business_impact}`;
  }
  showToast("Bottleneck Rebalanced", `Shifted ${units.toLocaleString()} units from ${source} to ${target}.`, "success");
  await loadCapacityData();
  await loadDashboard();
  await loadActivityFeed();
}

// -------------------------------------------------------------
// VIEW 6: INVENTORY & DC LOGISTICS
// -------------------------------------------------------------
async function loadInventoryData() {
  const res = await fetch(`${API_BASE}/inventory`);
  const data = await res.json();

  const container = document.getElementById("dc-cards-container");
  if (container) {
    container.innerHTML = data.dc_summary.map(dc => `
      <div class="stat-card border-slate-800">
        <div class="text-xs text-slate-400 uppercase font-mono font-bold">${dc.location_id}</div>
        <div class="text-xl font-bold font-['Outfit'] mt-1 text-white">${dc.total_available.toLocaleString()} units</div>
        <div class="text-xs text-slate-400 mt-2 flex justify-between">
          <span>Reserved: ${dc.total_reserved.toLocaleString()}</span>
          <span>Avg Age: ${dc.avg_age_days.toFixed(0)}d</span>
        </div>
      </div>
    `).join("");
  }

  const tbody = document.querySelector("#logistics-table tbody");
  if (tbody) {
    tbody.innerHTML = data.logistics_lanes.slice(0, 25).map(l => `
      <tr>
        <td class="font-mono font-bold text-indigo-300">${l.dc_id}</td>
        <td class="font-mono">${l.store_id}</td>
        <td class="font-mono text-emerald-400">$${l.transportation_cost_per_unit}</td>
        <td class="font-mono">${l.transport_lead_time_days} days</td>
        <td class="font-mono">${(l.service_level * 100).toFixed(1)}%</td>
      </tr>
    `).join("");
  }
}

// -------------------------------------------------------------
// VIEW 7: SELL-THROUGH & MARKDOWNS
// -------------------------------------------------------------
async function loadSellThroughData() {
  const res = await fetch(`${API_BASE}/markdowns`);
  const data = await res.json();
  globalMarkdownData = data.sku_recommendations;

  populateMarkdownSkuDropdown(data.sku_recommendations);

  const tbody = document.querySelector("#markdown-table tbody");
  if (tbody) {
    tbody.innerHTML = data.sku_recommendations.map(s => `
      <tr class="${s.action_alert === 'STOCKOUT_VULNERABILITY_ALERT' ? 'bg-rose-950/20' : (s.recommended_discount_pct >= 0.35 ? 'bg-amber-950/20' : '')}">
        <td class="font-mono font-bold text-indigo-300">${s.sku_id}</td>
        <td>${s.category}</td>
        <td class="font-mono">${(s.mean_sell_through * 100).toFixed(1)}%</td>
        <td class="font-mono font-bold ${s.weeks_of_stock < 4 ? 'text-rose-400' : ''}">${s.weeks_of_stock} WOS</td>
        <td><span class="badge ${s.mover_class === 'FAST_MOVER' ? 'badge-indigo' : (s.mover_class === 'SLOW_MOVER' ? 'badge-amber' : 'badge-emerald')}">${s.mover_class}</span></td>
        <td class="font-mono font-bold ${s.recommended_discount_pct > 0 ? 'text-amber-300' : 'text-slate-400'}">${(s.recommended_discount_pct * 100).toFixed(0)}%</td>
        <td class="font-mono text-rose-300">$${s.inventory_value_at_risk.toLocaleString()}</td>
        <td><span class="badge ${s.action_alert === 'STOCKOUT_VULNERABILITY_ALERT' ? 'badge-rose' : (s.action_alert === 'CRITICAL_EXCESS_INVENTORY' ? 'badge-amber' : 'badge-emerald')}">${s.action_alert}</span></td>
      </tr>
    `).join("");
  }
}

// -------------------------------------------------------------
// VIEW 8: FINANCIAL WATERFALL
// -------------------------------------------------------------
async function loadFinancialsData() {
  const res = await fetch(`${API_BASE}/financials`);
  const data = await res.json();

  const plContainer = document.getElementById("pl-statement");
  if (plContainer) {
    plContainer.innerHTML = `
      <div class="flex justify-between py-1 border-b border-slate-800"><span>Gross Forecasted Revenue</span><strong class="font-mono text-indigo-300">$${data.gross_revenue.toLocaleString()}</strong></div>
      <div class="flex justify-between py-1 border-b border-slate-800 text-rose-400"><span>Material COGS</span><strong class="font-mono">-$${data.material_cogs.toLocaleString()}</strong></div>
      <div class="flex justify-between py-1 border-b border-slate-800 text-rose-400"><span>Freight & Logistics</span><strong class="font-mono">-$${data.logistics_cost.toLocaleString()}</strong></div>
      <div class="flex justify-between py-1 border-b border-slate-800 text-amber-400"><span>In-Season Markdown Erosion</span><strong class="font-mono">-$${data.markdown_erosion.toLocaleString()}</strong></div>
      <div class="flex justify-between py-2 border-t-2 border-slate-700 text-emerald-400 text-sm"><span class="font-bold">Consensus Gross Margin</span><strong class="font-mono font-bold">$${data.net_gross_margin.toLocaleString()} (${data.gross_margin_pct}%)</strong></div>
    `;
  }

  const ctx = document.getElementById("chart-waterfall");
  if (ctx) {
    if (charts.waterfall) charts.waterfall.destroy();
    charts.waterfall = new Chart(ctx, {
      type: "bar",
      data: {
        labels: data.waterfall.map(w => w.step),
        datasets: [{
          label: "P&L Waterfall ($)",
          data: data.waterfall.map(w => w.amount),
          backgroundColor: data.waterfall.map(w => w.type === "positive" ? "#6366f1" : (w.type === "negative" ? "#f43f5e" : "#10b981")),
          borderRadius: 6
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          x: { grid: { color: "rgba(51, 65, 85, 0.2)" }, ticks: { color: "#94a3b8" } },
          y: { grid: { color: "rgba(51, 65, 85, 0.2)" }, ticks: { color: "#94a3b8" } }
        }
      }
    });
  }
}

// -------------------------------------------------------------
// VIEW 9: WHAT-IF SCENARIO SIMULATOR
// -------------------------------------------------------------
async function runLiveSimulation() {
  const category = document.getElementById("sim-category").value;
  const demandChange = parseFloat(document.getElementById("sim-demand").value);
  const leadtimeDelay = parseInt(document.getElementById("sim-leadtime").value);
  const s004Cap = parseFloat(document.getElementById("sim-s004").value);

  const res = await fetch(`${API_BASE}/scenario/run`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      category: category,
      demand_pct_change: demandChange,
      fabric_lead_time_delay_weeks: leadtimeDelay,
      supplier_s004_capacity_pct: s004Cap
    })
  });
  const data = await res.json();
  const c = data.comparison;

  const grid = document.getElementById("sim-cards-grid");
  if (grid) {
    grid.innerHTML = `
      <div class="stat-card border-slate-800">
        <span class="text-xs text-slate-400">Total Demand Units</span>
        <div class="text-lg font-bold mt-1 font-mono text-white">${c.demand_units.scenario.toLocaleString()}</div>
        <div class="text-xs ${c.demand_units.delta_pct >= 0 ? 'text-emerald-400' : 'text-rose-400'} font-mono">${c.demand_units.delta_pct >= 0 ? '+' : ''}${c.demand_units.delta_pct}% vs Baseline</div>
      </div>
      <div class="stat-card border-slate-800">
        <span class="text-xs text-slate-400">Gross Fabric Need (m)</span>
        <div class="text-lg font-bold mt-1 font-mono text-white">${c.fabric_requirement_meters.scenario.toLocaleString()}</div>
        <div class="text-xs text-amber-400 font-mono">+${c.fabric_requirement_meters.delta_pct}% Material Surge</div>
      </div>
      <div class="stat-card border-slate-800">
        <span class="text-xs text-slate-400">P003 Utilization %</span>
        <div class="text-lg font-bold mt-1 font-mono ${c.plant_p003_utilization_pct.scenario > 95 ? 'text-rose-400' : 'text-white'}">${c.plant_p003_utilization_pct.scenario}%</div>
        <div class="text-xs text-slate-400 font-mono">Baseline: ${c.plant_p003_utilization_pct.baseline}%</div>
      </div>
      <div class="stat-card border-slate-800">
        <span class="text-xs text-slate-400">Projected Margin %</span>
        <div class="text-lg font-bold mt-1 font-mono text-purple-300">${c.gross_margin_pct.scenario}%</div>
        <div class="text-xs text-emerald-400 font-mono">$${c.gross_revenue.scenario.toLocaleString()} Rev</div>
      </div>
    `;
  }

  const list = document.getElementById("sim-actions-list");
  if (list) {
    list.innerHTML = data.recommended_actions.map(act => `
      <li class="flex items-start gap-2">
        <i data-lucide="check-circle" class="w-4 h-4 text-emerald-400 mt-0.5"></i>
        <span>${act}</span>
      </li>
    `).join("");
  }
  lucide.createIcons();
}

// -------------------------------------------------------------
// VIEW 10: SHARED S&OP DECISION BOARD
// -------------------------------------------------------------
async function loadWorkflowData() {
  const res = await fetch(`${API_BASE}/sop/cycle`);
  const data = await res.json();

  const stepper = document.getElementById("workflow-stepper");
  if (stepper) {
    stepper.innerHTML = data.status.stages_flow.map((stg, i) => `
      <div class="p-3 rounded-xl bg-slate-900 border border-slate-800 flex items-center gap-2.5">
        <div class="w-7 h-7 rounded-full bg-indigo-600/30 text-indigo-300 flex items-center justify-center font-bold text-xs">
          ${i + 1}
        </div>
        <div>
          <div class="text-[11px] font-bold uppercase tracking-wider text-slate-300">${stg.replace('_', ' ')}</div>
          <span class="badge badge-emerald text-[9px] mt-0.5">COMPLETED</span>
        </div>
      </div>
    `).join("");
  }

  const tbody = document.querySelector("#decisions-table tbody");
  if (tbody) {
    tbody.innerHTML = data.decisions.map(d => `
      <tr>
        <td class="font-mono text-indigo-300 font-bold">${d.sop_cycle_id}</td>
        <td><span class="badge badge-indigo">${d.stage}</span></td>
        <td>${d.owner_role}</td>
        <td class="font-semibold text-white">${d.decision}</td>
        <td><span class="badge badge-emerald">${d.status}</span></td>
        <td class="font-mono text-emerald-400">${d.financial_impact}</td>
        <td>${d.approved_by}</td>
        <td class="font-mono text-[11px] text-slate-400">${d.timestamp}</td>
      </tr>
    `).join("");
  }
}

function openDecisionModal() {
  document.getElementById("decision-modal").classList.remove("hidden");
}

function closeDecisionModal() {
  document.getElementById("decision-modal").classList.add("hidden");
}

async function submitDecision() {
  const stage = document.getElementById("modal-stage").value;
  const title = document.getElementById("modal-title").value;
  const reason = document.getElementById("modal-reason").value;
  const fin = document.getElementById("modal-fin").value;
  const by = document.getElementById("modal-by").value;

  if (!title || !by) {
    alert("Please fill in decision title and approver name.");
    return;
  }

  await fetch(`${API_BASE}/sop/decide`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      cycle_id: "CYCLE_2026_M08",
      stage: stage,
      owner_role: USER_PROFILES[activeRole]?.role || "Executive S&OP Chair",
      decision: title,
      status: "APPROVED",
      reason: reason,
      financial_impact: fin || "Reconciled",
      risk_impact: "Reviewed",
      approved_by: by
    })
  });

  closeDecisionModal();
  showToast("Decision Signed Off", `${title} recorded in audit ledger.`, "success");
  await loadWorkflowData();
  await loadActivityFeed();
}
