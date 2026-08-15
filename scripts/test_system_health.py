import urllib.request
import json

def run_health_check():
    base = 'http://127.0.0.1:8000/api'
    results = []

    # 1. Health
    res = urllib.request.urlopen(f'{base}/health')
    d = json.loads(res.read().decode('utf-8'))
    results.append(('Health Check', d.get('status') == 'ONLINE', str(d.get('status'))))

    # 2. Dashboard
    res = urllib.request.urlopen(f'{base}/dashboard')
    d = json.loads(res.read().decode('utf-8'))
    margin = d['kpis']['gross_margin_pct']
    results.append(('Executive Dashboard', margin == 33.0, f"Margin: {margin}% | Revenue: ${d['kpis']['gross_revenue']:,.0f}"))

    # 3. Demand
    res = urllib.request.urlopen(f'{base}/demand')
    d = json.loads(res.read().decode('utf-8'))
    results.append(('Demand Planning', len(d['skus']) == 50, f"{len(d['skus'])} SKUs, {len(d['categories'])} Category rows"))

    # 4. Materials (MRP)
    res = urllib.request.urlopen(f'{base}/materials')
    d = json.loads(res.read().decode('utf-8'))
    results.append(('BOM Netting (MRP)', len(d['fabric_summary']) == 30, f"{len(d['fabric_summary'])} Raw Fabrics"))

    # 5. Procurement & Dynamic Matrix
    res = urllib.request.urlopen(f'{base}/procurement')
    d = json.loads(res.read().decode('utf-8'))
    matrix_count = len(d.get('supplier_fabric_matrix', []))
    results.append(('Sourcing & Multi-Vendor Matrix', matrix_count > 0, f"{len(d['supplier_allocation_summary'])} Suppliers, {matrix_count} Pricing Pairs"))

    # 6. Plant Capacity
    res = urllib.request.urlopen(f'{base}/capacity')
    d = json.loads(res.read().decode('utf-8'))
    results.append(('Plant Capacity (5 Hubs)', len(d['plant_capacity']) > 0, f"{len(d['plant_capacity'])} Capacity Records"))

    # 7. Inventory & DC
    res = urllib.request.urlopen(f'{base}/inventory')
    d = json.loads(res.read().decode('utf-8'))
    results.append(('DC Inventory & Lanes', len(d['dc_summary']) > 0, f"{len(d['dc_summary'])} DC Hubs, {len(d['logistics_lanes'])} Lanes"))

    # 8. Markdowns
    res = urllib.request.urlopen(f'{base}/markdowns')
    d = json.loads(res.read().decode('utf-8'))
    results.append(('In-Season Markdowns', len(d['sku_recommendations']) == 50, f"{len(d['sku_recommendations'])} SKU Profiles"))

    # 9. Financials
    res = urllib.request.urlopen(f'{base}/financials')
    d = json.loads(res.read().decode('utf-8'))
    results.append(('Consolidated Financials', d.get('gross_margin_pct') == 33.0, f"Net Margin: ${d.get('net_gross_margin'):,.0f} ({d.get('gross_margin_pct')}%)"))

    # 10. S&OP Cycle & Decisions
    res = urllib.request.urlopen(f'{base}/sop/cycle')
    d = json.loads(res.read().decode('utf-8'))
    results.append(('S&OP Decision Board', len(d['decisions']) > 0, f"{len(d['decisions'])} Audited Decisions"))

    # 11. Activity Feed
    res = urllib.request.urlopen(f'{base}/activity/feed')
    d = json.loads(res.read().decode('utf-8'))
    results.append(('Live Activity Feed', len(d.get('feed', [])) > 0, f"{len(d.get('feed', []))} Live Events Logged"))

    # 12. POST Capacity Shift
    req = urllib.request.Request(f'{base}/capacity/shift', data=json.dumps({'source_plant': 'P003', 'target_plant': 'P004', 'period': 'W06', 'units_to_shift': 1440}).encode('utf-8'), headers={'Content-Type': 'application/json'})
    res = urllib.request.urlopen(req)
    d = json.loads(res.read().decode('utf-8'))
    results.append(('Capacity Shift POST', d.get('status') == 'FEASIBLE', str(d.get('business_impact'))))

    # 13. POST Scenario Run
    req = urllib.request.Request(f'{base}/scenario/run', data=json.dumps({'category': 'Jackets', 'demand_pct_change': 50.0, 'fabric_lead_time_delay_weeks': 1, 'supplier_s004_capacity_pct': -30.0}).encode('utf-8'), headers={'Content-Type': 'application/json'})
    res = urllib.request.urlopen(req)
    d = json.loads(res.read().decode('utf-8'))
    results.append(('What-If Scenario POST', 'comparison' in d, f"Demand Delta: +{d['comparison']['demand_units']['delta_pct']}%"))

    # 14. Static UI & Cache Headers
    res = urllib.request.urlopen('http://127.0.0.1:8000/')
    hdrs = dict(res.getheaders())
    html = res.read().decode('utf-8')
    no_num = ('1. Demand' not in html and '2. Supply' not in html and '3. In-Season' not in html and '4. Financials' not in html)
    has_clean = ('Demand & Merchandising' in html and 'Supply & Operations' in html and 'Governance & Strategy' in html)
    has_no_cache = 'no-store' in hdrs.get('Cache-Control', '')
    results.append(('Clean UI Headers & No-Cache', no_num and has_clean and has_no_cache, f"No-Cache: {has_no_cache} | Clean Headers: {has_clean}"))

    print('=====================================================')
    print('          TRENDWEAR S&OP FULL SYSTEM AUDIT           ')
    print('=====================================================')
    all_passed = True
    for name, passed, detail in results:
        status = 'PASS' if passed else 'FAIL'
        if not passed: all_passed = False
        print(f'[{status}] {name:32} -> {detail}')
    print('=====================================================')
    if all_passed:
        print('FINAL STATUS: ALL 13 SUBSYSTEMS 100% OPERATIONAL')
    else:
        print('FINAL STATUS: ISSUES DETECTED')

if __name__ == '__main__':
    run_health_check()
