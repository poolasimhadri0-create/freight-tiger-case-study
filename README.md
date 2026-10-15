# FreightTiger AI / Software Engineer Intern Case Study
## Shipping Cost Anomaly Detection & Operational Explanation System

### 1. Executive Summary
This project provides an automated, reproducible anomaly detection engine designed for FreightTiger to monitor freight costs across corridors. The system identifies weekly shipping cost spikes, evaluates each corridor against two independent baselines, retrieves context notes from operational logs, and produces a structured review CSV distinguishing genuinely justified cost surges (e.g. natural disasters, festival surcharges) from unexplained anomalies requiring human review.

---

### 2. Project Architecture & Workflow

```text
freight_tiger_project/
├── data/
│   ├── shipment_records.csv         # Raw shipment events (2,940 records, 2024-2025)
│   ├── context_notes.csv            # Operational incident log (10 notes)
│   └── sample_output_format_v2.csv  # Target evaluation specification
├── main.py                          # Core processing, baseline computation, & report generator
├── test_reproducibility.py          # Automated verification script testing output determinism
├── requirements.txt                 # Dependencies
├── cost_log.txt                     # Token & execution cost accounting
├── output.csv                       # Final generated audit report matching specification
└── README.md                        # Documentation & interview walkthrough guide
```

---

### 3. Core Mathematical Methodology

#### A. Metric: Cost per Tonne-Kilometre
Shipping efficiency is assessed per tonne-km to account for freight mass and transit distance:
$$\text{Cost per tonne-km} = \frac{\sum \text{Freight Cost (INR)}}{\sum (\text{Quantity in Tonnes} \times \text{Distance in km})}$$
*Note:* Aggregation is performed at the route-week level using pooled sums ($\frac{\sum \text{cost}}{\sum \text{tonne-km}}$) rather than averaging individual shipment ratios, preventing distortion from unweighted small shipments.

#### B. Weekly Partitioning
- Weeks run strictly Monday to Sunday.
- The `week_of` identifier represents the calendar Monday (`YYYY-MM-DD`).

#### C. Baseline 1: Route's Own Historical Average (`vs_own_history`)
- Computed as the rolling average of up to the **preceding 8 available weeks** for that specific corridor.
- **Strictly excludes the current week** (`shift(1)`) to avoid self-referential bias and target leakage.
$$\Delta\%_{\text{history}} = \frac{\text{Current Cost} - \text{History Avg}}{\text{History Avg}} \times 100\%$$

#### D. Baseline 2: Peer Routes Average (`vs_similar_routes`)
- Compares the corridor against other corridors within the same `route_type` (Short, Medium, or Long) during the same calendar week.
- **Strictly excludes the corridor itself** from its peer group average.
$$\Delta\%_{\text{peers}} = \frac{\text{Current Cost} - \text{Peer Avg}}{\text{Peer Avg}} \times 100\%$$

---

### 4. Anomaly Detection & Evidence Retrieval

#### Anomaly Threshold
A route-week is flagged as an anomaly if either:
- Its cost exceeds the peer average by $\ge 20\%$, OR
- Its cost exceeds its own 8-week historical baseline by $\ge 20\%$.

#### Context Evidence Verification
When an anomaly is flagged, the system queries `context_notes.csv`:
1. **Corridor & Temporal Proximity:** Matches the specific corridor (or national notes) within the applicable timeframe.
2. **Operational Causality Check:**
   - **Genuine Operational Causes:** e.g., Note `N001` (flooding requiring detours on Chennai-Bangalore) and `N002` (regional festival surcharge on Ahmedabad-Mumbai).
     $\rightarrow$ `flagged = "No (justified)"`, `matched_note_id = "<NoteID>"`.
   - **Non-Justifying / Stable Reports:** e.g., Note `N006` notes stable demand, `N004` affects routes outside the dataset, and `N010` compliance costs were absorbed without rate changes.
     $\rightarrow$ `flagged = "Yes"`, `matched_note_id = ""`.
   - **No Record:** Unexplained corridor spike.
     $\rightarrow$ `flagged = "Yes"`, `matched_note_id = ""`.

---

### 5. Setup & Execution

#### Step 1: Set up Virtual Environment
```bash
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On Linux / Mac:
source .venv/bin/activate
```

#### Step 2: Install Requirements
```bash
pip install -r requirements.txt
```

#### Step 3: Run the Anomaly Engine
```bash
python main.py
```
Outputs generated:
- `output.csv` (contains the anomaly report matching FreightTiger's format)
- `cost_log.txt` (contains token and execution tracking)

#### Step 4: Verify Reproducibility
```bash
python test_reproducibility.py
```
Asserts identical SHA256 checksums across 3 consecutive executions.

---

### 6. Verification & Reproducibility Evidence
- **Sample Target Match:**
  - `Delhi-Jaipur` (2024-11-11): Cost `4.17`, `+35.5% vs past avg`, `+21.0% vs similar routes`, Flagged `Yes`. (Exact match).
  - `Ahmedabad-Mumbai` (2025-01-20): Cost `3.29`, `+29.5% vs past avg`, `+22.5% vs similar routes`, Flagged `No (justified)`, Note `N002`. (Exact match).
  - `Mumbai-Pune` (2025-09-15): Cost `3.98`, `+9.2% vs past avg`, `+23.6% vs similar routes`, Flagged `Yes`, Note `N006` non-justifying. (Exact match).
- **Run Hash Consistency:**
  - SHA256: `ab751c7714257d2132dddbe2e3b6c582365a37b5c0bfa10504e9c5334f48f9cd` (100% bit-for-bit identical across all test runs).

---

### 7. LLM & Token Cost Accounting
As detailed in `cost_log.txt`:
- Architecture: Deterministic rule-based & retrieval parsing
- Total LLM Calls: `0`
- Input / Output Tokens: `0`
- Total Cost: `$0.00`
- *Rationale:* Deterministic retrieval guarantees that numeric metrics, baseline percentages, and anomaly classifications are completely reproducible, eliminating token expenses, latency, and hallucinations.
