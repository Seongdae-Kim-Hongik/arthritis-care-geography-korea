import os, subprocess, pandas as pd
from docx.oxml.ns import qn
from jkms_engine import JKMS
import content_arth as C
from build_ms_arth import LABEL, GROUPS
from numbers_arth import ROB
HERE = os.path.dirname(os.path.abspath(__file__)); IJ = os.path.dirname(HERE); OUT = os.path.join(IJ, "out"); B = os.path.dirname(IJ)
N = C.N
SHORT = {"public_pools_per_100k": "Pools", "village_sports_facilities_per_100k": "Village sports", "moderate_pa_rate": "Moderate PA", "older_leisure_facilities_per_1000": "Senior leisure",
         "older_single_household_share": "Older single HH", "regular_employee_share": "Regular employment", "beds_per_1000": "Hospital beds", "public_health_centre_use_rate": "Health center use"}
ORD = ["public_pools_per_100k", "village_sports_facilities_per_100k", "moderate_pa_rate", "regular_employee_share", "beds_per_1000", "public_health_centre_use_rate", "older_leisure_facilities_per_1000", "older_single_household_share"]
assert set(ORD) == set(ROB)
SRC = {"kchs": "Community Health Survey (KDCA)", "chk": "NHIS statistics", "pop": "Statistics Korea", "fac": "Public sports facility survey (MCST)", "vil": "Village sports facility survey (MCST)", "eloc": "KOSIS local statistics", "ext": "Resident registration (derived)", "kosis": "KOSIS"}
f3 = lambda t: f"{t[0]:.3f} ({t[1]:.3f}-{t[2]:.3f})" + ("*" if t[3] else "")
J = JKMS(cite="sup"); d = J.doc
for s in d.sections:
    ln = s._sectPr.find(qn("w:lnNumType"))
    if ln is not None: s._sectPr.remove(ln)
J.para("<b>Online Resource 1</b>"); J.para(f"<b>{C.TITLE}</b>"); J.para("Author details are given on the separate title page (double-anonymized review).")
J.para("Contents. Supplementary Methods, Tables S1-S4, list of persistent hot spots, and STROBE and RECORD checklist.", before=6)
J.head("Supplementary Methods", 1)
SM = [("Outcome.", "Annual numbers of unique persons treated with a principal diagnosis of arthritis (ICD-10 M00-M19 and M22-M25) under National Health Insurance or Medical Aid, by district of residence, from the Regional Medical Care Utilization Statistics of the National Health Insurance Service (major diseases by district). Counts are by date of care in all care settings except pharmacies, including Korean medicine clinics, and are attributed to the district of residence of the insured person, not to the location of the treating facility."),
      ("Expected counts.", "National age-specific treatment rates for the same diagnoses in ten groups (0-9 to 50-59 years in 10-year groups, 60-64, 65-69, 70-74, and 75 years or older) came from the national disease-classification statistics of the NHIS, divided by the national population in each age group. District age structures came from resident registration statistics by 5-year group, aggregated to the same groups. Expected counts were rescaled each year so that their national sum equaled the observed sum. National tables are not published by sex. In the 2023 resident registration file, the age block of Changwon duplicated the 2022 block; the 2023 total was replaced with the official total (1,009,038) and the age distribution was reconstructed from the national residual."),
      ("Covariates.", "Each covariate was standardized across all district-years. Missing years were filled within districts by linear interpolation where neighboring years existed and otherwise by the district mean; Table S1 lists the source, observed years, prespecified direction, and filled cells. The share of the population aged 80 years or older was forced into every model because the oldest standardization group (75 years or older) cannot capture differences in very old age."),
      ("Models.", "Software: R 4.6.0 with R-INLA; Python 3.9 for data preparation, emerging hot spot analysis, and figures. Negative binomial likelihood, log expected counts as offset, BYM2 district effect with penalized-complexity priors (P(σ > 0.5) = 0.01; P(φ < 0.5) = 2/3), and first-order random-walk and independent year effects. District adjacency was defined by shared boundaries (593 edges); six island districts were linked to their nearest neighbor, and Jeju Island (two districts) formed a separate connected component. Multiverse: 200 random subsets of the hypothesis covariates, each fitted with all forced controls. Knorr-Held interactions were added with Kronecker-product structure matrices (type I: independent; II: RW1 in time × independent districts; III: independent years × ICAR in space; IV: RW1 × ICAR), with sum-to-zero constraints defined separately for each connected component of the graph. The Spatial+-type method regressed each standardized covariate on the 23 lowest-frequency eigenvectors of the graph Laplacian, skipping all zero eigenvalues, and used the residuals. Emerging hot spot analysis applied Getis-Ord Gi* to annual empirical Bayes-smoothed ratios with Mann-Kendall trend tests of the Gi* z-scores, following the 17 standard categories."),
      ("Sensitivity analyses.", "Table S3 lists every alternative specification with WAIC and the eight subset-stable covariates. Imputed values were perturbed 20 times with normal noise of the within-district observed standard deviation and pooled by Rubin's rules; this is a perturbation of imputed values, not model-based multiple imputation. Comparison outcomes (treated gastric cancer, C16; treated infectious diseases, A00-B99) used the same covariates with their own age-standardized expected counts.")]
for h, t in SM: J.para(f"<b>{h}</b> {t}")
import unicodedata
WM = pd.read_csv(os.path.join(B, "results_std3", "S4b_window_spatialRR.csv"), encoding="utf-8-sig"); WM["fbd_region"] = WM.fbd_region.map(lambda x: unicodedata.normalize("NFC", x))
nh = WM[WM["class"] == "hotspot"].groupby("sigungu_cd").size(); allhot = sorted(nh[nh == 3].index.astype(str)); assert len(allhot) == N["hot_all_windows"]
NM = pd.read_csv(os.path.join(B, "results_std3", "S6_spatial_RR.csv"), dtype={"sigungu_cd": str}).set_index("sigungu_cd").fbd_region.map(lambda x: unicodedata.normalize("NFC", x))
PROV = {"서울시": "Seoul", "부산시": "Busan", "대구시": "Daegu", "인천시": "Incheon", "광주시": "Gwangju", "대전시": "Daejeon", "울산시": "Ulsan", "세종시": "Sejong", "경기도": "Gyeonggi", "강원도": "Gangwon", "충청북도": "North Chungcheong",
        "충청남도": "South Chungcheong", "전라북도": "North Jeolla", "전라남도": "South Jeolla", "경상북도": "North Gyeongsang", "경상남도": "South Gyeongsang", "제주도": "Jeju"}
J.para(f"<b>Persistent hot spots.</b> The {len(allhot)} districts that were hot spots in all three windows, by province and district code (KOSIS sigungu code): "
       + "; ".join(f"{p} ({', '.join(c for c in allhot if NM[c].startswith(k))})" for k, p in PROV.items() if any(NM[c].startswith(k) for c in allhot)) + ". District names for each code are given in the analytic panel in the data archive.")
# Table S1
M = pd.read_csv(os.path.join(B, "panel_META_ARTH_std3.csv"), encoding="utf-8-sig").set_index("variable")
rows = []
for g, vs in GROUPS:
    rows.append(["__H__", g])
    for v in vs:
        m = M.loc[v]; pre = str(m.source_column).split("__")[0]; imp = int(m.n_imputed_interp + m.n_imputed_sgg_mean + m.n_imputed_year_mean)
        rows.append([f"  {LABEL[v]}", SRC.get(pre, pre), f"{int(m.obs_year_min)}-{int(m.obs_year_max)}", ("NA" if m.role == "forced" else str(m.expected_direction).replace("-", "−")), f"{imp:,}"])
J.page_break(); J.table("Table S1. Source, observed years, prespecified direction, and filled cells (of 3,206 district-years) for each covariate", ["Covariate", "Source", "Years", "Direction", "Filled cells"], rows, [4.6, 4.6, 2.0, 1.9, 1.9],
        "KDCA, Korea Disease Control and Prevention Agency; MCST, Ministry of Culture, Sports and Tourism; NHIS, National Health Insurance Service; NA, no direction prespecified (forced control).", fs=9)
# Table S2
LO = pd.read_csv(os.path.join(B, "results_std3", "S41_leaveout_ranges.csv")).set_index(["set", "cov"])
rows = []
for v in ORD:
    mv = N["mv"][v]; rt = dict(zip(("kept", "n_specs"), N["ret14"][v])); rb = N["rubin"][v]; ev = N["evalue"][v]
    rows.append([SHORT[v], f"{100*mv['cred_frac']:.0f} / {100*mv['sign_agree']:.0f}", f"{rt['kept']}/{rt['n_specs']}; {LO.loc[('province', v), 'n_cred_same_sign']}/17; {LO.loc[('year', v), 'n_cred_same_sign']}/14",
                 f"{rb['IRR_pooled']:.3f} ({rb['lo']:.3f}-{rb['hi']:.3f})", f3(N["bw"][v + "__within"]), f3(N["bw"][v + "__between"]), f"{ev['E_point']:.2f} / {ev['E_limit']:.2f}"])
J.landscape_section()
J.table("Table S2. Multiverse results, retention, perturbed imputed values, within-district and between-district components, and E-values for the subset-stable covariates", ["Covariate", "Credible / same sign, %", "Retained: Table S3; province; year", "Perturbed imputation RR (95% CrI)", "Within-district RR (95% CrI)", "Between-district RR (95% CrI)", "E-value point / limit"], rows,
        [3.0, 2.6, 3.3, 3.8, 3.8, 3.8, 2.6],
        "Credible and same-sign shares from 200 covariate-subset specifications. Retained = credible with the principal-model sign in the alternative specifications of Table S3 containing the covariate, in the 17 leave-one-province fits, and in the 14 leave-one-year fits. Perturbed imputation: 20 replicates pooled by Rubin's rules. Within = two-way-centered deviation (district and year means removed); between = district mean. E-values per 1 SD for the point estimate and the credible limit closer to 1. HH, households; PA, physical activity; RR, rate ratio; CrI, credible interval. * 95% CrI excludes 1.", fs=9)
# Table S3
NAMES = {"main_queen": "Principal model (refit)", "iid_only": "Independent district effect only", "icar_besag": "ICAR district effect only", "no_spatial": "No district effect", "pc_phi_flat": "BYM2, neutral prior on φ", "pc_relaxA": "BYM2, relaxed precision prior A", "pc_relaxB": "BYM2, relaxed precision prior B",
         "knn3": "Neighbors: 3 nearest", "knn4": "Neighbors: 4 nearest", "knn5": "Neighbors: 5 nearest", "KH_typeI": "Knorr-Held type I", "KH_typeII": "Knorr-Held type II", "KH_typeIII": "Knorr-Held type III", "KH_typeIV": "Knorr-Held type IV",
         "C1_poisson_lognormal": "Poisson with observation-level effect", "C2_rw2_year": "RW2 year effect", "C3_ar1_year": "AR1 year effect", "C4_sido_year_iid": "Province-by-year effect", "B3_smooth_forced": "Forced controls smoothed",
         "D1_spatial_plus": "Spatial+-type adjustment", "E0_nolag_from2012": "No lag, from 2012", "E0_nolag_from2013": "No lag, from 2013", "E1_lag1": "Covariates lagged 1 year", "E2_lag2": "Covariates lagged 2 years",
         "F3_extreme_R7": "Extreme district-years excluded", "G1_kchs_ma3": "Survey covariates, 3-year moving average", "H4_odd_years": "Odd years only", "H4_even_years": "Even years only",
         "s577": "Adjacency graph without boundary corrections", "s8": "Expected counts from eight age groups", "s2": "Share aged 80 years or older omitted"}
S = {**N["s43"], **N["s41"]}; WA = {**N["s43_waic"], **N["s41_waic"]}
for v in ("s577", "s2", "s8"):
    S.update({(v, c): t for c, t in N["sens_main"][v].items()})
    WA[v] = float(pd.read_csv(os.path.join(B, f"results_{v}", "S3_main_fit.csv")).WAIC.iloc[0])
def cell(a, v):
    t = S.get((a, v)); return "-" if t is None else f"{t[0]:.3f}" + ("*" if t[3] else "")
rows = [[NAMES[a], f"{WA[a]:,.0f}"] + [cell(a, v) for v in ORD] for a in NAMES if a in WA]
J.page_break()
J.table("Table S3. WAIC and rate ratios per 1 SD for the eight subset-stable covariates in alternative specifications", ["Specification", "WAIC"] + [SHORT[v] for v in ORD], rows, [5.4, 1.6] + [2.08] * 8,
        f"Principal model WAIC {N['waic_main']:,.1f}; the refit in the first row differs only by Monte Carlo variation. * 95% credible interval excludes 1 (judged before rounding). WAIC values are comparable only within the same years, outcome, and expected counts. Leave-one-province and leave-one-year fits and perturbation replicates are summarized in Table S2. HH, households; PA, physical activity.", fs=8)
# Table S4
LONG = {"public_pools_per_100k": "Public swimming pools", "village_sports_facilities_per_100k": "Village sports facilities", "moderate_pa_rate": "Moderate physical activity", "regular_employee_share": "Regular employment",
        "beds_per_1000": "Hospital beds", "public_health_centre_use_rate": "Public health center use", "older_leisure_facilities_per_1000": "Senior leisure facilities", "older_single_household_share": "Older single-person households"}
rows = [[LONG[v], f3((N["main"][v]["IRR"], N["main"][v]["lo"], N["main"][v]["hi"], N["main"][v]["cred"])), f3(N["nco"][("GCA", v)]), f3(N["nco"][("INFECT", v)])] for v in ORD]
NC = {"seatbelt_wearing_rate": "Negative control: seat-belt wearing", "cpr_awareness_rate": "Negative control: resuscitation awareness", "waste_recycling_rate": "Negative control: waste recycling"}
J.page_break()
J.table("Table S4. Comparison outcomes, negative-control exposures, and model checks", ["Covariate", "Arthritis (principal model)", "Gastric cancer (C16)", "Infectious diseases (A00-B99)"], rows, [6.0, 5.6, 5.6, 5.6],
        "Rate ratios per 1 SD (95% credible interval) for the eight subset-stable covariates; each comparison outcome was fitted with the same covariates and its own age-standardized expected counts. "
        + "Negative-control exposures added one at a time to the principal model: " + "; ".join(f"{NC[k].split(': ')[1]} {v['IRR']:.3f} ({v['lo']:.3f}-{v['hi']:.3f})" + ("*" if v["cred"] else "") for k, v in N["negctl"].items()) + ". "
        + f"Model checks: 95% posterior predictive coverage {100*N['ppc']['coverage95']:.1f}% (50%: {100*N['ppc']['coverage50']:.1f}%; PIT Kolmogorov-Smirnov P {'<0.001' if N['ppc']['pit_ks_p'] < 0.001 else format(N['ppc']['pit_ks_p'], '.3f')}); held-out 2024 coverage conditional on national totals {100*N['oos']['coverage95']:.1f}%; residual Moran's I {N['moran_resid']:.3f} (permutation P {N['moran_resid_p']:.2f}); "
        + f"structured spatial, unstructured spatial, covariate, and year components {100*N['varpart']['spatial_structured']['share_of_linear_predictor_var']:.1f}%, {100*N['varpart']['spatial_unstructured']['share_of_linear_predictor_var']:.1f}%, {100*N['varpart']['fixed_covariates']['share_of_linear_predictor_var']:.1f}%, and {100*N['varpart']['year_effects']['share_of_linear_predictor_var']:.1f}% of linear predictor variance. * 95% credible interval excludes 1.", fs=9)
# STROBE / RECORD
CK = [("Title and abstract", "1", "Title page; Abstract"), ("Background/rationale", "2", "Introduction"), ("Objectives", "3", "Introduction, final paragraph"), ("Study design", "4", "Methods 2.1"), ("Setting", "5", "Methods 2.1"), ("Participants", "6", "Methods 2.1 (district populations; ecological)"),
      ("Variables", "7", "Methods 2.2-2.3; Table S1"), ("Data sources/measurement", "8", "Methods 2.1-2.3; Supplementary Methods"), ("Bias", "9", "Methods 2.5; Tables S2-S4"), ("Study size", "10", "Methods 2.1 (all 229 districts)"), ("Quantitative variables", "11", "Methods 2.3"),
      ("Statistical methods", "12", "Methods 2.4-2.5"), ("Descriptive data", "14", "Results 3.1; Table 1"), ("Outcome data", "15", "Results 3.1"), ("Main results", "16", "Results 3.2-3.3; Table 2"), ("Other analyses", "17", "Results 3.4; Fig. 3; Tables S2-S4"),
      ("Key results", "18", "Discussion 4.1"), ("Limitations", "19", "Discussion 4.4"), ("Interpretation", "20", "Discussion 4.1-4.3"), ("Generalizability", "21", "Discussion 4.4-4.5"), ("Funding", "22", "Title page, Statements and Declarations"),
      ("RECORD 6.1 codes/algorithms", "R6.1", "Methods 2.1 (M00-M19, M22-M25 principal diagnosis)"), ("RECORD 7.1 codes for variables", "R7.1", "Table S1; Supplementary Methods"), ("RECORD 12.1 data access", "R12.1", "Only published aggregate statistics were used"),
      ("RECORD 12.2 data cleaning", "R12.2", "Supplementary Methods (boundaries, filled cells, Changwon 2023)"), ("RECORD 12.3 data linkage", "R12.3", "District-level merging by district code; no person-level linkage"), ("RECORD 22.1 data access statement", "R22.1", "Data availability statement")]
J.page_break(); J.table("STROBE and RECORD checklist for this ecological study of routinely collected data", ["Item", "No.", "Where reported"], [[a, b, c] for a, b, c in CK], [5.6, 1.6, 7.8], "Item 13 (participant flow) is not applicable to aggregate district data.", fs=9)
for s in d.sections:   # 가로 섹션이 줄번호를 다시 넣으므로 저장 전에 모두 끈다
    ln = s._sectPr.find(qn("w:lnNumType"))
    if ln is not None: s._sectPr.remove(ln)
p = os.path.join(OUT, "ESM_1.docx"); J.doc_title = "Online Resource 1"; J.save(p)
subprocess.run(["/opt/homebrew/bin/soffice", "--headless", "-env:UserInstallation=file:///tmp/lo_arth_ri_esm", "--convert-to", "pdf", "--outdir", OUT, p], check=True, capture_output=True)
print("saved", p, len(rows))
