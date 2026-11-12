import streamlit as st
import pandas as pd
from database import (
    init_db, add_product, list_products, add_order,
    list_orders, update_stock, update_order_status, seed_demo_data
)
from optimizer import (
    WarehouseGraph, shortest_path, optimize_pick_route,
    pack_orders, assign_vehicles, forecast_demand
)

# ---------------------------------------------------------
# Page Setup
# ---------------------------------------------------------
st.set_page_config(
    page_title="PickFlow Pro - Intelligent Warehouse System",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Initialize database schema and populate demo records if empty
init_db()
seed_demo_data(force=False)

# Maintain active navigation state
if "active_nav" not in st.session_state:
    st.session_state["active_nav"] = "Dashboard"

def switch_view(new_view):
    st.session_state["active_nav"] = new_view
    for k in ["main_nav_selector", "segmented_nav"]:
        if k in st.session_state:
            st.session_state[k] = new_view

# ---------------------------------------------------------
# Custom Styling (Matches PickFlow Pro UI from screenshot)
# ---------------------------------------------------------
st.html("""
<style>
/* Base overrides */
.stApp {
    background-color: #F8FAFC;
    color: #0F172A;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
}

/* Remove excessive top padding */
.block-container {
    padding-top: 1rem !important;
    padding-bottom: 3rem !important;
    max-width: 1280px !important;
}

/* Top Purple Demo Banner */
.demo-banner {
    background: linear-gradient(90deg, #6366F1, #8B5CF6);
    color: #FFFFFF;
    text-align: center;
    padding: 6px 14px;
    font-size: 0.82rem;
    font-weight: 500;
    border-radius: 8px;
    margin-bottom: 14px;
    box-shadow: 0 1px 3px rgba(99, 102, 241, 0.2);
}

/* Custom Header Bar */
.header-bar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    background: #FFFFFF;
    padding: 12px 24px;
    border-radius: 16px;
    border: 1px solid #E2E8F0;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.03);
    margin-bottom: 22px;
}
.brand-group {
    display: flex;
    align-items: center;
    gap: 12px;
}
.brand-icon {
    width: 42px;
    height: 42px;
    background: linear-gradient(135deg, #4F46E5, #7C3AED);
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-size: 1.4rem;
    box-shadow: 0 2px 8px rgba(79, 70, 229, 0.3);
}
.brand-title {
    font-size: 1.25rem;
    font-weight: 800;
    color: #1E1B4B;
    line-height: 1.2;
    margin: 0;
}
.brand-subtitle {
    font-size: 0.78rem;
    color: #64748B;
    margin: 0;
    font-weight: 500;
}
.header-actions {
    display: flex;
    align-items: center;
    gap: 12px;
}
.badge-pill {
    background: #F1F5F9;
    color: #475569;
    padding: 6px 12px;
    border-radius: 20px;
    font-size: 0.82rem;
    font-weight: 600;
    display: flex;
    align-items: center;
    gap: 6px;
    border: 1px solid #E2E8F0;
}

/* Page Title & Subtitle */
.page-header-title {
    font-size: 1.85rem;
    font-weight: 800;
    color: #0F172A;
    margin-bottom: 2px;
}
.page-header-sub {
    font-size: 0.95rem;
    color: #64748B;
    margin-bottom: 20px;
}

/* KPI Metric Cards */
.kpi-container {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 16px;
    margin-bottom: 28px;
}
.kpi-card {
    border-radius: 18px;
    padding: 20px 22px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.02);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.kpi-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 14px rgba(0, 0, 0, 0.05);
}
.kpi-card-blue {
    background: #F0F7FF;
    border: 1px solid #DBEAFE;
}
.kpi-card-cyan {
    background: #F0FDF4;
    border: 1px solid #DCFCE7;
}
.kpi-card-yellow {
    background: #FEFCE8;
    border: 1px solid #FEF08A;
}
.kpi-card-emerald {
    background: #ECFDF5;
    border: 1px solid #D1FAE5;
}
.kpi-label {
    font-size: 0.85rem;
    font-weight: 600;
    color: #475569;
    margin-bottom: 6px;
}
.kpi-num {
    font-size: 2.1rem;
    font-weight: 800;
    color: #0F172A;
    line-height: 1;
    margin-bottom: 10px;
}
.kpi-badge {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    font-size: 0.78rem;
    font-weight: 700;
    padding: 3px 8px;
    border-radius: 10px;
}
.badge-green {
    background: #DCFCE7;
    color: #166534;
}
.badge-amber {
    background: #FEF3C7;
    color: #92400E;
}
.kpi-icon-box {
    width: 48px;
    height: 48px;
    border-radius: 14px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.45rem;
    color: #FFFFFF;
    flex-shrink: 0;
    box-shadow: 0 3px 8px rgba(0,0,0,0.08);
}
.icon-box-blue { background: #3B82F6; }
.icon-box-cyan { background: #10B981; }
.icon-box-yellow { background: #EAB308; }
.icon-box-emerald { background: #059669; }

/* Quick Actions Section */
.qa-heading {
    font-size: 1.25rem;
    font-weight: 800;
    color: #0F172A;
    margin-bottom: 16px;
}

/* Quick Action Buttons Styling */
.st-key-qa_receive button,
.st-key-qa_pick button,
.st-key-qa_stocktake button,
.st-key-qa_inventory button,
.st-key-qa_reports button,
.st-key-qa_settings button {
    height: 105px !important;
    border-radius: 18px !important;
    border: none !important;
    padding: 16px 20px !important;
    text-align: center !important;
    display: flex !important;
    flex-direction: column !important;
    align-items: center !important;
    justify-content: center !important;
    transition: all 0.22s cubic-bezier(0.4, 0, 0.2, 1) !important;
    white-space: pre-line !important;
}
.st-key-qa_receive button:hover,
.st-key-qa_pick button:hover,
.st-key-qa_stocktake button:hover,
.st-key-qa_inventory button:hover,
.st-key-qa_reports button:hover,
.st-key-qa_settings button:hover {
    transform: translateY(-3px) !important;
    filter: brightness(1.06) !important;
}

/* Individual Quick Action Button Colors */
.st-key-qa_receive button {
    background: linear-gradient(135deg, #10B981 0%, #059669 100%) !important;
    box-shadow: 0 4px 14px rgba(16, 185, 129, 0.3) !important;
}
.st-key-qa_pick button {
    background: linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%) !important;
    box-shadow: 0 4px 14px rgba(37, 99, 235, 0.3) !important;
}
.st-key-qa_stocktake button {
    background: linear-gradient(135deg, #8B5CF6 0%, #7C3AED 100%) !important;
    box-shadow: 0 4px 14px rgba(139, 92, 246, 0.3) !important;
}
.st-key-qa_inventory button {
    background: linear-gradient(135deg, #4F46E5 0%, #4338CA 100%) !important;
    box-shadow: 0 4px 14px rgba(79, 70, 229, 0.3) !important;
}
.st-key-qa_reports button {
    background: linear-gradient(135deg, #F97316 0%, #EA580C 100%) !important;
    box-shadow: 0 4px 14px rgba(249, 115, 22, 0.3) !important;
}
.st-key-qa_settings button {
    background: linear-gradient(135deg, #374151 0%, #1F2937 100%) !important;
    box-shadow: 0 4px 14px rgba(55, 65, 81, 0.3) !important;
}

/* Force bright crisp text on quick action buttons */
.st-key-qa_receive button *,
.st-key-qa_pick button *,
.st-key-qa_stocktake button *,
.st-key-qa_inventory button *,
.st-key-qa_reports button *,
.st-key-qa_settings button * {
    color: #FFFFFF !important;
    font-weight: 700 !important;
}

/* Priority tag chips */
.priority-chip {
    padding: 3px 8px;
    border-radius: 6px;
    font-size: 0.75rem;
    font-weight: 700;
    display: inline-block;
}
.priority-express { background: #FEE2E2; color: #DC2626; }
.priority-standard { background: #DBEAFE; color: #2563EB; }
.priority-low { background: #F1F5F9; color: #64748B; }
</style>
""")

# Top banner
st.html('<div class="demo-banner">PickFlow Pro &bull; Intelligent Warehouse System &bull; Live Optimizer</div>')

# ---------------------------------------------------------
# Navigation Bar Component
# ---------------------------------------------------------
nav_col_brand, nav_col_menu, nav_col_info = st.columns([2.5, 5, 2.5], vertical_alignment="center")

with nav_col_brand:
    st.html("""
    <div class="brand-group">
        <div class="brand-icon">📦</div>
        <div>
            <div class="brand-title">PickFlow Pro</div>
            <div class="brand-subtitle">Intelligent Warehouse System</div>
        </div>
    </div>
    """)

with nav_col_menu:
    nav_options = ["Dashboard", "Inventory", "Receiving", "Order Picking", "Stock Take", "Admin"]
    if hasattr(st, "segmented_control"):
        selected_nav = st.segmented_control(
            label="Navigation Menu",
            options=nav_options,
            default=st.session_state["active_nav"],
            key="main_nav_selector",
            label_visibility="collapsed"
        )
    elif hasattr(st, "pills"):
        selected_nav = st.pills(
            label="Navigation Menu",
            options=nav_options,
            default=st.session_state["active_nav"],
            key="main_nav_selector",
            label_visibility="collapsed"
        )
    else:
        current_idx = nav_options.index(st.session_state["active_nav"]) if st.session_state["active_nav"] in nav_options else 0
        selected_nav = st.radio(
            label="Navigation Menu",
            options=nav_options,
            index=current_idx,
            horizontal=True,
            key="main_nav_selector",
            label_visibility="collapsed"
        )
    if selected_nav and selected_nav != st.session_state["active_nav"]:
        st.session_state["active_nav"] = selected_nav
        st.rerun()

with nav_col_info:
    products_all = list_products()
    orders_all = list_orders()
    low_stock_count = sum(1 for p in products_all if p["quantity"] <= 15)
    st.html(f"""
    <div style="display:flex; justify-content: flex-end; align-items: center; gap: 8px;">
        <span class="badge-pill">🔍 Search</span>
        <span class="badge-pill" style="background:{'#FEF3C7' if low_stock_count > 0 else '#F1F5F9'}; color:{'#92400E' if low_stock_count > 0 else '#475569'};">
            🔔 {low_stock_count} Alerts
        </span>
        <span class="badge-pill">👤 Operator</span>
    </div>
    """)

st.divider()

# Compute live KPIs from database
total_items = sum(p["quantity"] for p in products_all)
orders_picked = sum(1 for o in orders_all if o.get("status") == "PICKED")
low_stock_items = sum(1 for p in products_all if p["quantity"] <= 15)
items_issued_today = sum(o["quantity"] for o in orders_all if o.get("status") == "PICKED")


# =========================================================
# VIEW 1: DASHBOARD (Exact screenshot recreation)
# =========================================================
if st.session_state["active_nav"] == "Dashboard":
    st.html("""
    <div>
        <div class="page-header-title">Warehouse Dashboard</div>
        <div class="page-header-sub">Welcome to PickFlow Pro - Your intelligent warehouse management solution</div>
    </div>
    """)

    # 4 KPI Cards (Matching exact color palette & icons from screenshot)
    kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)

    with kpi_col1:
        st.html(f"""
        <div class="kpi-card kpi-card-blue">
            <div>
                <div class="kpi-label">Total Items</div>
                <div class="kpi-num">{total_items}</div>
                <div class="kpi-badge badge-green">↗ +12 from yesterday</div>
            </div>
            <div class="kpi-icon-box icon-box-blue">📦</div>
        </div>
        """)

    with kpi_col2:
        st.html(f"""
        <div class="kpi-card kpi-card-cyan">
            <div>
                <div class="kpi-label">Orders Picked</div>
                <div class="kpi-num">{orders_picked}</div>
                <div class="kpi-badge badge-green">↗ +5.2% from yesterday</div>
            </div>
            <div class="kpi-icon-box icon-box-cyan">📈</div>
        </div>
        """)

    with kpi_col3:
        st.html(f"""
        <div class="kpi-card kpi-card-yellow">
            <div>
                <div class="kpi-label">Low Stock Items</div>
                <div class="kpi-num">{low_stock_items}</div>
                <div class="kpi-badge badge-amber">⚠ -3 from yesterday</div>
            </div>
            <div class="kpi-icon-box icon-box-yellow">⚠️</div>
        </div>
        """)

    with kpi_col4:
        st.html(f"""
        <div class="kpi-card kpi-card-emerald">
            <div>
                <div class="kpi-label">Items Issued Today</div>
                <div class="kpi-num">{items_issued_today}</div>
                <div class="kpi-badge badge-green">✔ +18 from yesterday</div>
            </div>
            <div class="kpi-icon-box icon-box-emerald">✅</div>
        </div>
        """)

    st.write("")
    st.html('<div class="qa-heading">Quick Actions</div>')

    # Quick Actions Grid (2 rows x 3 columns)
    qa_r1_c1, qa_r1_c2, qa_r1_c3 = st.columns(3)
    with qa_r1_c1:
        if st.button("Receive Stock\nBook items into warehouse", key="qa_receive", width="stretch", icon=":material/move_to_inbox:"):
            switch_view("Receiving")
            st.rerun()

    with qa_r1_c2:
        if st.button("Pick Orders\nIssue items from warehouse", key="qa_pick", width="stretch", icon=":material/shopping_cart_checkout:"):
            switch_view("Order Picking")
            st.rerun()

    with qa_r1_c3:
        if st.button("Stock Take\nPerform inventory count", key="qa_stocktake", width="stretch", icon=":material/sync:"):
            switch_view("Stock Take")
            st.rerun()

    qa_r2_c1, qa_r2_c2, qa_r2_c3 = st.columns(3)
    with qa_r2_c1:
        if st.button("View Inventory\nBrowse all items", key="qa_inventory", width="stretch", icon=":material/inventory_2:"):
            switch_view("Inventory")
            st.rerun()

    with qa_r2_c2:
        if st.button("Reports\nView analytics & reports", key="qa_reports", width="stretch", icon=":material/bar_chart:"):
            switch_view("Admin")
            st.rerun()

    with qa_r2_c3:
        if st.button("Settings\nSystem configuration", key="qa_settings", width="stretch", icon=":material/settings:"):
            switch_view("Admin")
            st.rerun()

    st.write("")
    st.divider()

    # Live Warehouse Overview Section
    dash_col_left, dash_col_right = st.columns([6, 4])

    with dash_col_left:
        st.subheader("📋 Urgent Order Queue (Priority First)")
        pending_orders = [o for o in orders_all if o.get("status") == "PENDING"]
        if pending_orders:
            df_pending = pd.DataFrame(pending_orders)[["id", "sku", "product_name", "quantity", "priority", "delivery_note"]]
            st.dataframe(df_pending, width="stretch", hide_index=True)
            if st.button("Go to Order Picking & Path Optimization →", icon=":material/alt_route:"):
                switch_view("Order Picking")
                st.rerun()
        else:
            st.success("All current orders have been picked and fulfilled!")

    with dash_col_right:
        st.subheader("⚠️ Stock Level Alerts")
        low_stock_list = [p for p in products_all if p["quantity"] <= 15]
        if low_stock_list:
            df_low = pd.DataFrame(low_stock_list)[["sku", "name", "quantity", "location"]]
            st.dataframe(df_low, width="stretch", hide_index=True)
            if st.button("Receive Inbound Stock to Replenish →", icon=":material/add_box:"):
                switch_view("Receiving")
                st.rerun()
        else:
            st.info("All warehouse stock levels are healthy.")


# =========================================================
# VIEW 2: INVENTORY ("View Inventory")
# =========================================================
elif st.session_state["active_nav"] == "Inventory":
    st.html("""
    <div>
        <div class="page-header-title">Warehouse Inventory</div>
        <div class="page-header-sub">Search, inspect and filter current warehouse stock across all aisles</div>
    </div>
    """)

    f_col1, f_col2, f_col3 = st.columns([4, 3, 3])
    with f_col1:
        search_query = st.text_input("Search SKU or Name", placeholder="e.g. SKU-1001 or Tape", label_visibility="collapsed")
    with f_col2:
        aisle_filter = st.selectbox("Filter by Aisle", ["All Aisles", "Aisle A", "Aisle B", "Aisle C"], label_visibility="collapsed")
    with f_col3:
        status_filter = st.selectbox("Stock Status", ["All Stock", "Low Stock (≤15)", "In Stock (>15)"], label_visibility="collapsed")

    filtered_products = products_all
    if search_query:
        q = search_query.strip().lower()
        filtered_products = [p for p in filtered_products if q in p["sku"].lower() or q in p["name"].lower()]
    if aisle_filter != "All Aisles":
        aisle_prefix = aisle_filter.split()[-1]
        filtered_products = [p for p in filtered_products if p["location"].startswith(aisle_prefix)]
    if status_filter == "Low Stock (≤15)":
        filtered_products = [p for p in filtered_products if p["quantity"] <= 15]
    elif status_filter == "In Stock (>15)":
        filtered_products = [p for p in filtered_products if p["quantity"] > 15]

    st.write(f"Showing **{len(filtered_products)}** products")
    if filtered_products:
        st.dataframe(pd.DataFrame(filtered_products), width="stretch", hide_index=True)
    else:
        st.warning("No products matched your search.")

    st.divider()
    st.subheader("Quick Stock Level Adjustment")
    with st.form("inventory_adjust_form"):
        adj_col1, adj_col2, adj_col3 = st.columns([4, 3, 3])
        sku_select = adj_col1.selectbox("Select Product", [f"{p['sku']} - {p['name']} (Qty: {p['quantity']})" for p in products_all])
        delta_val = adj_col2.number_input("Adjustment Units (+/-)", value=0, step=1)
        submit_adj = adj_col3.form_submit_button("Update Stock Level", width="stretch")
        if submit_adj:
            chosen_sku = sku_select.split(" - ")[0]
            try:
                update_stock(chosen_sku, int(delta_val))
                st.success(f"Updated {chosen_sku} by {delta_val} units.")
                st.rerun()
            except ValueError as e:
                st.error(str(e))


# =========================================================
# VIEW 3: RECEIVING ("Receive Stock")
# =========================================================
elif st.session_state["active_nav"] == "Receiving":
    st.html("""
    <div>
        <div class="page-header-title">Receive Stock</div>
        <div class="page-header-sub">Book incoming supplier shipments and register new items into warehouse locations</div>
    </div>
    """)

    rec_tab1, rec_tab2 = st.tabs(["Book New SKU / Product", "Inbound Stock Shipment"])

    with rec_tab1:
        st.subheader("Register New Product SKU")
        with st.form("new_product_form"):
            c1, c2 = st.columns(2)
            new_sku = c1.text_input("Product SKU", placeholder="e.g. SKU-1016")
            new_name = c2.text_input("Product Description", placeholder="e.g. Biodegradable Packing Peanuts")
            c3, c4 = st.columns(2)
            new_qty = c3.number_input("Received Quantity", min_value=1, value=50, step=1)
            new_loc = c4.selectbox("Shelf Location", ["A1", "A2", "A3", "B1", "B2", "B3", "C1", "C2", "C3", "PACK"])
            save_prod = st.form_submit_button("Book Item into Warehouse", icon=":material/add_box:")
            if save_prod:
                if not new_sku.strip() or not new_name.strip():
                    st.error("Both SKU and Product Description are required.")
                else:
                    add_product(new_sku.strip().upper(), new_name.strip(), int(new_qty), new_loc)
                    st.success(f"Successfully registered {new_sku.upper()} ({new_name.strip()}) with {new_qty} units at shelf {new_loc}!")
                    st.rerun()

    with rec_tab2:
        st.subheader("Process Inbound Delivery to Existing Stock")
        with st.form("inbound_delivery_form"):
            p_map = {f"{p['sku']} - {p['name']} (Current: {p['quantity']} at {p['location']})": p['sku'] for p in products_all}
            chosen_label = st.selectbox("Select Existing Item", list(p_map.keys()))
            inbound_qty = st.number_input("Inbound Units Received", min_value=1, value=25, step=1)
            inbound_note = st.text_input("Delivery / PO Reference Note", placeholder="PO-9942 from Acme Supplies")
            submit_inbound = st.form_submit_button("Confirm Inbound Receipt", icon=":material/check_circle:")
            if submit_inbound:
                target_sku = p_map[chosen_label]
                update_stock(target_sku, int(inbound_qty))
                st.success(f"Receipt confirmed! Added {inbound_qty} units to {target_sku}.")
                st.rerun()


# =========================================================
# VIEW 4: ORDER PICKING ("Pick Orders & Route Optimizer")
# =========================================================
elif st.session_state["active_nav"] == "Order Picking":
    st.html("""
    <div>
        <div class="page-header-title">Order Picking & Route Optimizer</div>
        <div class="page-header-sub">Priority-based order fulfillment and warehouse aisle shortest-path heuristic (Dijkstra)</div>
    </div>
    """)

    pick_tab1, pick_tab2, pick_tab3 = st.tabs(["Active Pick Queue", "Warehouse Route Planner", "Create Customer Order"])

    with pick_tab1:
        st.subheader("Pending Orders (Priority First)")
        pending = [o for o in orders_all if o.get("status") == "PENDING"]
        if pending:
            for ord_item in pending:
                card_col1, card_col2, card_col3, card_col4 = st.columns([1.5, 4, 2.5, 2], vertical_alignment="center")
                pr = ord_item["priority"]
                color_class = "priority-express" if pr == "EXPRESS" else ("priority-standard" if pr == "STANDARD" else "priority-low")
                card_col1.html(f"<span class='priority-chip {color_class}'>{pr}</span><br><small>Order #{ord_item['id']}</small>")
                card_col2.write(f"**{ord_item['product_name']}** ({ord_item['sku']}) &bull; Qty: **{ord_item['quantity']}**")
                card_col3.caption(f"Note: {ord_item['delivery_note'] or 'None'}")
                if card_col4.button("Mark Picked ✔", key=f"pick_btn_{ord_item['id']}", width="stretch"):
                    update_order_status(ord_item['id'], "PICKED")
                    st.toast(f"Order #{ord_item['id']} marked as PICKED!", icon="✅")
                    st.rerun()
                st.divider()
        else:
            st.success("No pending orders to pick! All shipments fulfilled.")

    with pick_tab2:
        st.subheader("Warehouse Aisle Path Optimizer (Dijkstra Heuristic)")
        st.caption("Calculates the shortest walking route through warehouse aisles to collect stops and return to packing station.")
        graph = WarehouseGraph()
        nodes = sorted(graph.adj.keys())

        r_col1, r_col2 = st.columns(2)
        start_node = r_col1.selectbox("Start / Dispatch Station", nodes, index=nodes.index("PACK") if "PACK" in nodes else 0)
        
        # Suggest stops based on locations of pending orders
        sku_to_loc = {p["sku"]: p["location"] for p in products_all}
        pending_locations = [sku_to_loc[o["sku"]] for o in pending if o["sku"] in sku_to_loc and sku_to_loc[o["sku"]] in nodes]
        default_stops = ",".join(list(dict.fromkeys(pending_locations))) if pending_locations else "A1,B2,C1"
        
        stops_input = r_col2.text_input("Pick Stops (Comma-separated aisle nodes)", value=default_stops)

        if st.button("Calculate Optimal Walking Route", icon=":material/directions_walk:"):
            try:
                pick_stops = [s.strip().upper() for s in stops_input.split(",") if s.strip()]
                unknown_nodes = [s for s in [start_node] + pick_stops if s not in graph.adj]
                if unknown_nodes:
                    st.error(f"Unknown aisle node(s): {', '.join(unknown_nodes)}")
                elif pick_stops:
                    route, total_dist = optimize_pick_route(graph, start_node, pick_stops, "PACK")
                    st.success(f"**Optimal Route:** {' → '.join(route)}")
                    st.metric("Total Walking Distance", f"{total_dist:.1f} metres")
                    st.info("Pick sequence generated using nearest-neighbor heuristic over binary-heap Dijkstra paths.")
            except Exception as e:
                st.error(f"Routing error: {e}")

    with pick_tab3:
        st.subheader("Place New Order")
        with st.form("new_order_form"):
            prod_lookup = {p["sku"]: p for p in products_all}
            ord_sku = st.selectbox("Select Product", [f"{p['sku']} - {p['name']} ({p['quantity']} in stock)" for p in products_all])
            sel_sku = ord_sku.split(" - ")[0]
            ord_quantity = st.number_input("Order Quantity", min_value=1, value=1, step=1)
            ord_priority = st.selectbox("Order Priority", ["EXPRESS", "STANDARD", "LOW"])
            ord_note = st.text_input("Delivery / Packaging Instructions", placeholder="Deliver to Bay 3 before noon")
            submit_order = st.form_submit_button("Reserve Stock & Create Order", icon=":material/shopping_cart:")
            if submit_order:
                p_item = prod_lookup[sel_sku]
                if p_item["quantity"] < ord_quantity:
                    st.error(f"Cannot fulfill order: Only {p_item['quantity']} units available in stock.")
                else:
                    update_stock(sel_sku, -int(ord_quantity))
                    oid = add_order(sel_sku, p_item["name"], int(ord_quantity), ord_priority, ord_note)
                    st.success(f"Order #{oid} placed successfully! Stock reserved.")
                    st.rerun()


# =========================================================
# VIEW 5: STOCK TAKE ("Perform Inventory Count")
# =========================================================
elif st.session_state["active_nav"] == "Stock Take":
    st.html("""
    <div>
        <div class="page-header-title">Stock Take & Inventory Audit</div>
        <div class="page-header-sub">Perform physical cycle counts, flag inventory discrepancies and reconcile variances</div>
    </div>
    """)

    st.subheader("Live Warehouse Cycle Count Sheet")
    st.caption("Compare on-hand physical count against system records.")

    audit_data = []
    for p in products_all:
        audit_data.append({
            "SKU": p["sku"],
            "Description": p["name"],
            "Location": p["location"],
            "System Count": p["quantity"],
            "Status": "Low Stock" if p["quantity"] <= 15 else "Adequate"
        })

    st.dataframe(pd.DataFrame(audit_data), width="stretch", hide_index=True)

    st.divider()
    st.subheader("Reconcile Discrepancy")
    with st.form("stock_reconcile_form"):
        sc1, sc2, sc3 = st.columns([4, 3, 3])
        sku_audit = sc1.selectbox("Select SKU to Reconcile", [f"{p['sku']} - {p['name']}" for p in products_all])
        target_sku_audit = sku_audit.split(" - ")[0]
        current_rec = next((p for p in products_all if p["sku"] == target_sku_audit), None)
        phys_count = sc2.number_input("Physical Count Observed", min_value=0, value=current_rec["quantity"] if current_rec else 0, step=1)
        submit_reconcile = sc3.form_submit_button("Apply Reconciled Count", width="stretch")
        if submit_reconcile and current_rec:
            variance = phys_count - current_rec["quantity"]
            update_stock(target_sku_audit, variance)
            st.success(f"Reconciled {target_sku_audit}: System updated to {phys_count} units (Variance: {variance:+d}).")
            st.rerun()


# =========================================================
# VIEW 6: ADMIN ("Reports, Settings & Dispatch Optimization")
# =========================================================
elif st.session_state["active_nav"] == "Admin":
    st.html("""
    <div>
        <div class="page-header-title">Reports, Dispatch & Settings</div>
        <div class="page-header-sub">Algorithmic knapsack vehicle loading, fleet bin-packing, demand forecasting and system setup</div>
    </div>
    """)

    adm_tab1, adm_tab2, adm_tab3, adm_tab4 = st.tabs([
        "Demand Forecasting", "Vehicle Loading (Knapsack)", "Fleet Assignment", "System Settings"
    ])

    with adm_tab1:
        st.subheader("Demand Forecasting (Moving-Average Baseline)")
        f_sales = st.text_input("Historical Daily Sales (Comma-separated)", "18, 22, 19, 25, 28, 24, 31, 35")
        f_horizon = st.slider("Days to Forecast Ahead", min_value=1, max_value=14, value=5)
        if st.button("Generate Forecast", icon=":material/trending_up:"):
            try:
                hist = [float(x.strip()) for x in f_sales.split(",") if x.strip()]
                preds = forecast_demand(hist, horizon=f_horizon)
                
                chart_df = pd.DataFrame({
                    "Period": [f"Day -{len(hist)-i}" for i in range(len(hist))] + [f"Forecast +{i+1}" for i in range(len(preds))],
                    "Sales": hist + [round(x, 1) for x in preds],
                    "Type": ["Historical"] * len(hist) + ["Forecast"] * len(preds)
                })
                st.bar_chart(chart_df, x="Period", y="Sales", color="Type", width="stretch")
                st.caption(f"Forecasted values: {[round(x, 1) for x in preds]}")
            except Exception as e:
                st.error(f"Forecast error: {e}")

    with adm_tab2:
        st.subheader("Vehicle Load Optimization (Exact 0/1 Knapsack DP)")
        st.caption("Select packages that maximize total priority value while strictly respecting vehicle payload capacity.")
        pkg_input = st.text_area("Packages (Format: Name, Weight_KG, Value)",
                                 "Order-101, 6.5, 140\nOrder-102, 12.0, 260\nOrder-103, 4.0, 95\nOrder-104, 15.0, 310\nOrder-105, 8.5, 180")
        truck_cap = st.number_input("Vehicle Weight Capacity (KG)", min_value=5.0, value=25.0, step=1.0)
        if st.button("Optimize Vehicle Load", icon=":material/local_shipping:"):
            try:
                items_list = []
                for line in pkg_input.splitlines():
                    if line.strip():
                        n, w, v = [x.strip() for x in line.split(",")]
                        items_list.append({"name": n, "weight": float(w), "value": float(v)})
                chosen_pkgs, loaded_w, total_val = pack_orders(items_list, float(truck_cap))
                m1, m2, m3 = st.columns(3)
                m1.metric("Selected Packages", len(chosen_pkgs))
                m2.metric("Total Loaded Weight", f"{loaded_w:.1f} kg / {truck_cap:.1f} kg")
                m3.metric("Total Priority Value", f"${total_val:.1f}")
                st.dataframe(pd.DataFrame(chosen_pkgs), width="stretch", hide_index=True)
            except Exception as e:
                st.error(f"Knapsack optimizer error: {e}")

    with adm_tab3:
        st.subheader("Fleet Vehicle Assignment (First-Fit Decreasing Bin Packing)")
        st.caption("Distribute customer loads across available delivery fleet vehicles.")
        cust_loads = st.text_input("Customer Shipment Loads (KG, comma-separated)", "18, 25, 12, 35, 20, 15")
        fleet_caps = st.text_input("Vehicle Capacities (KG, comma-separated)", "60, 45, 30")
        if st.button("Assign Fleet", icon=":material/rv_hookup:"):
            try:
                loads = [float(x.strip()) for x in cust_loads.split(",") if x.strip()]
                caps = [float(x.strip()) for x in fleet_caps.split(",") if x.strip()]
                fleet_res = assign_vehicles(loads, caps)
                for v in fleet_res:
                    st.write(f"🚚 **Vehicle {v['vehicle']}** (Capacity: {v['capacity']} kg &bull; Remaining: {v['remaining']} kg)")
                    if v["customers"]:
                        st.dataframe(pd.DataFrame(v["customers"]), width="stretch", hide_index=True)
                    else:
                        st.info("Empty vehicle (no loads assigned).")
            except Exception as e:
                st.error(f"Fleet assignment error: {e}")

    with adm_tab4:
        st.subheader("Database & Demo Controls")
        st.write("Reset database and seed realistic demo products and orders to match the PickFlow Pro UI.")
        if st.button("Seed / Reset Demo Warehouse Data", icon=":material/restart_alt:"):
            seed_demo_data(force=True)
            st.success("Database re-seeded with realistic warehouse items and orders!")
            st.rerun()
