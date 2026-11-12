# Smart Warehouse & Delivery Optimizer

A runnable, DSA-focused M.Tech prototype built with Python, Streamlit and SQLite.

## Features
- Inventory CRUD with SKU hash-index lookup (SQLite primary-key index).
- Stock validation and transactional stock reservation when an order is created.
- Priority-based order queue (priority rank + indexed SQL ordering).
- Warehouse graph represented by adjacency lists.
- Dijkstra shortest path using a binary heap.
- Multi-stop picking route using nearest-next-stop heuristic.
- 0/1 Knapsack packing optimizer (weights discretized to 0.1 kg).
- First-Fit Decreasing vehicle capacity assignment heuristic.
- Moving-average demand forecast baseline.
- Dashboard with inventory and order status.

## Requirements
- Python 3.10+
- pip

## Run locally

```bash
# 1. Create and activate virtual environment
python -m venv .venv

# Windows PowerShell:
.venv\Scripts\Activate.ps1

# Windows CMD:
.venv\Scripts\activate.bat

# macOS/Linux:
source .venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Start the app
streamlit run app.py
```

Open the local URL printed by Streamlit (usually http://localhost:8501).

## Suggested first run
1. Open Inventory and add SKU-1001 / Laptop / 30 / A1.
2. Add more products with shelf locations from the demo map: PACK, A1, A2, A3, B1, B2, B3, C1, C2, C3.
3. Create EXPRESS and STANDARD orders.
4. Use Warehouse route with stops such as A1,B2,C1.
5. Try the packing and vehicle assignment panels.

## Project structure
```text
smart_warehouse_optimizer/
├── app.py
├── database.py
├── optimizer.py
├── requirements.txt
├── README.md
├── tests/
│   └── test_optimizer.py
└── .gitignore
```

## DSA and complexity
| Component | Technique | Expected complexity |
|---|---|---|
| Product lookup | SQLite primary-key index / hash-index concept | O(log n) B-tree in SQLite; Python dict average O(1) |
| Order scheduling | Priority rank + indexed ordering | O(log n) insertion in heap; DB index query |
| Warehouse shortest path | Dijkstra + binary heap | O((V+E) log V) |
| Multi-stop picking | Nearest-next-stop heuristic + Dijkstra | O(k(V+E)logV), approximate |
| Packing | 0/1 Knapsack DP | O(nW), W is capacity in 0.1 kg units |
| Vehicle loading | First-Fit Decreasing | O(n log n + nm), n loads, m vehicles |
| Forecast | Moving average | O(h*w), h horizon and w window |

## Important engineering notes
- The route planner is a heuristic for stop ordering; it does not claim a globally optimal TSP tour.
- Knapsack is exact for the discretized 0.1 kg weights. For large capacities, DP memory/time can grow; use a solver or approximation for production.
- First-Fit Decreasing is a heuristic, not guaranteed optimal.
- Moving average is a baseline, not a production forecasting model.
- The demo warehouse graph is synthetic. Replace it with measured aisle coordinates and distances for real deployment.
- This is a local prototype. For multi-user production, add authentication, role-based access, audit logs, migrations, API validation, concurrency tests, monitoring and deployment hardening.

## Research / evaluation extension
Run controlled experiments comparing:
- Dijkstra vs A* (when an admissible geometric heuristic is available).
- Nearest-next-stop vs 2-opt / exact TSP on small maps.
- First-Fit Decreasing vs integer programming / best-fit heuristics.
- Moving average vs seasonal naive / exponential smoothing / XGBoost.

Report route length, runtime, memory, forecast MAE/RMSE, stockout rate and vehicle utilization on reproducible datasets.
