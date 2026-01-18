<p align="center">
  <img src="final_submission/images/TEAM-EKLAVYA-logo.png" width="250" alt="Team Eklavya Logo">
</p>

# 📡 UIDAI Intelligent Audit Framework: Team Eklavya

[![GitHub License](https://img.shields.io/badge/Audit-Statistical-blue.svg)](https://github.com/Akshay-gurav-31/UIDAI-DATA-HACKATHON-2026)
[![Platform](https://img.shields.io/badge/Platform-UIDAI_Data_Hackathon-orange.svg)](#)

### **Empowering Aadhaar Ecosystem through Microscopic Data Auditing & Anomaly Detection**

This framework is a sophisticated, data-driven audit system designed to identify administrative bottlenecks, reporting latencies, and cross-API inconsistencies within UIDAI datasets. By utilizing Welch's T-Test and Z-Score normalization, our system distinguishes organic transaction demand from systematic administrative pulse patterns.

---

## 🏗️ System Architecture & Data Pipeline

Our architecture is built for high-scale processing and mathematical precision.

![System Architecture](final_submission/images/High-Level%20System%20Architecture.png)

1. **Ingestion Layer:** Automated, memory-efficient chunked loading (100K blocks) via Python Pandas.
2. **Standardization Engine:** Fuzzy Matching (Levenshtein Distance Algorithm) used to resolve district-level naming conflicts between Enrolment and Update APIs.
3. **Statistical Validator:** Anomaly flagging using Z-Score (|Z| > 2.0) and validation of anomalies via Welch's T-test (p < 0.05).
4. **Audit Reporting:** Automated generation of Jury-safe PDF/DOCX reports and interactive data-visuals.

---

## 🏥 Operational Dashboards

Full-spectrum visibility into the national Aadhaar pulse.

![Dashboard Prototype](final_submission/images/dashbaord.png)

*Figure: Command Center interface showing real-time anomaly flagging and reporting cycle pulse.*

---

## 📊 High-Impact Findings

### 1. The Naming Paradox (Ghost Districts)

Audit revealed that 6.5% of "Ghost Districts" (High Enrolment / Zero Updates) were artifacts of naming mismatches across backend APIs.

* **Methodology:** Cross-API Header Auditing.
* **Impact:** Resolved data silos for ~234K transaction records.

### 2. The Monthly Pulse (Batch Processing Delay)

Quantitative proof that 91.3% of transaction data is reported on a 30-day batch cycle.

* **Finding:** Identified a "Batch Pulse" on the 1st of every month, obscuring daily societal trends.
* **Recommendation:** Transition high-growth administrative units to daily ingestion.

### 3. Administrative Process Coupling

Discovered a near-perfect **Pearson Correlation (r = 0.99)** between disparate update streams.

* **Conclusion:** Proves artificial synchronization at the operational level, suggesting load-balancing opportunities.

---

## 🛠️ Reproduction & Deployment

Professional-grade automation for immediate audit execution.

1. **Environment Setup:**
```bash
pip install -r requirements.txt
```

2. **Run Intelligence Audit:**
```bash
python analysis/build_pro_report.py
```

3. **Verify Artifacts:**
Check the `final_submission/` directory for the professional PDF report and the `notebooks/` directory for deep-dive statistical proof.

---

## 🏆 Submission Deliverables

* **Executive Summary:** [Team_Eklavya_Submission_FINAL.pdf](final_submission/Team_Eklavya_Submission_FINAL.pdf)
* **Technical Evidence:** See `/notebooks` for Z-score and T-test validation logs.
* **Live Demo:** [Eklavya Prototype](https://github.com/Akshay-gurav-31/UIDAI-DATA-HACKATHON-2026)

---

## 👥 Meet the Team

<p align="center">
  <img src="final_submission/images/team.png" width="1200" alt="Team Eklavya Group">
</p>

<table align="center">
  <tr>
    <th align="center">Name</th>
    <th align="center">Role</th>
    <th align="center">LinkedIn</th>
  </tr>
  <tr>
    <td align="center"><b>Yesha Parwani</b></td>
    <td align="center">Team Leader</td>
    <td align="center"><a href="https://www.linkedin.com/in/yesha-parwani/">Profile</a></td>
  </tr>
  <tr>
    <td align="center"><b>Akshay Gurav</b></td>
    <td align="center">Developer / Analyst</td>
    <td align="center"><a href="https://www.linkedin.com/in/akshay---gurav/">Profile</a></td>
  </tr>
  <tr>
    <td align="center"><b>Shreyash Kumar</b></td>
    <td align="center">Research Lead</td>
    <td align="center"><a href="https://www.linkedin.com/in/shreyash-kumar-9774b622a/">Profile</a></td>
  </tr>
  <tr>
    <td align="center"><b>Ashit Patel</b></td>
    <td align="center">Data Analyst</td>
    <td align="center"><a href="https://www.linkedin.com/in/ashit-patel-163815226/">Profile</a></td>
  </tr>
  <tr>
    <td align="center"><b>Nishita Chhabaria</b></td>
    <td align="center">Documentation Support</td>
    <td align="center"><a href="https://www.linkedin.com/in/nishita-chhabaria-a626582a0/">Profile</a></td>
  </tr>
</table>

---

**Disclaimer:** All data utilized is anonymized synthetic/sample data provided by the UIDAI public portal for hackathon purposes.
