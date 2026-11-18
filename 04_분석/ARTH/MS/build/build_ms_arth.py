#  사용: ST_SHP=<final.shp> python3 figs_arth.py → python3 build_ms_arth.py → python3 esm_arth.py → python3 cover_arth.py → python3 check_ri_arth.py
#  원천: draft/01_manuscript.md(Abstract·Practitioner Points·Introduction·Discussion·Conclusion, [@key]) + content_arth.py(Methods·Results) + numbers_arth.py
import os, re, json, subprocess
from jkms_engine import JKMS
import content_arth as C
HERE = os.path.dirname(os.path.abspath(__file__)); IJ = os.path.dirname(HERE); OUT = os.path.join(IJ, "out"); os.makedirs(OUT, exist_ok=True)
N = C.N; REFS = json.load(open(os.path.join(HERE, "refs_arth.json"), encoding="utf-8"))
DRAFT = os.path.join(IJ, "draft", "01_manuscript.md")
ZENODO = open(os.path.join(OUT, "zenodo_doi.txt")).read().strip() if os.path.exists(os.path.join(OUT, "zenodo_doi.txt")) else ""   # 새 레코드(코드만, 공개 MIT)
GITHUB = "https://github.com/Seongdae-Kim-Hongik/arthritis-care-geography-korea"
AI_STMT = "The author used Claude (Anthropic) and ChatGPT (OpenAI) only for translation and English-language editing of the manuscript."   # 11/4 밤 사용자 지시: 번역·첨삭만

def pandoc_cites(t): return re.sub(r"\s*\[(@[^\]]+)\]", lambda m: "{{" + ",".join(k.strip().lstrip("@") for k in m.group(1).split(";")) + "}}", t)
def read_draft():
    md = open(DRAFT, encoding="utf-8").read(); md = re.sub(r"<!--.*?-->", "", md, flags=re.S); S = {}; cur = None
    for line in md.split("\n"):
        m = re.match(r"^## (.+)$", line)
        if m: cur = m.group(1).strip(); S[cur] = []; continue
        if cur is not None: S[cur].append(line)
    return {k: [p.strip() for p in "\n".join(v).split("\n\n") if p.strip()] for k, v in S.items()}

def springer(r):
    if r["type"] == "web": return f"{r['authors']} ({r['year']}) {r['title']}. {r['url']}. Accessed {r['accessed']}"
    au = r["authors"]; a = ", ".join(au) if len(au) <= 10 else ", ".join(au[:3]) + " et al"
    pg = str(r.get("pages", "")).replace("--", "-").replace("-", "–")
    s = f"{a} ({r['year']}) {r['title'].rstrip('.')}. {r['journal']} {r.get('vol','')}" + (f":{pg}" if pg else "")
    if r.get("doi"): s += f". https://doi.org/{r['doi']}"
    return s
def ama(r):
    if r["type"] == "web": return f"{r['authors']}. {r['title']}. Published {r['year']}. Accessed {r['accessed']}. {r['url']}"
    au = r["authors"]; a = ", ".join(au if len(au) <= 6 else au[:3]) + (", et al" if len(au) > 6 else "")
    vol = r.get("vol", ""); iss = f"({r['issue']})" if r.get("issue") else ""; pg = str(r.get("pages", "")).replace("--", "-")
    s = f"{a}. {r['title'].rstrip('.')}. <i>{r['journal']}</i>. {r['year']};{vol}{iss}" + (f":{pg}" if pg else "") + "."
    if r.get("doi"): s += f" doi:{r['doi']}"
    return s

TAB1_COV = [("pop80_share", "Population aged 80 years or older, %"), ("urban_population_share", "Urban population share, %"), ("clinics_per_100k", "Clinics per 100,000"),
            ("walking_practice_rate", "Walking practice, %"), ("moderate_pa_rate", "Moderate or vigorous activity, %"), ("public_pools_per_100k", "Public swimming pools per 100,000"),
            ("village_sports_facilities_per_100k", "Village sports facilities per 100,000"), ("older_single_household_share", "Older single-person households, %")]
def table1():
    T = N["T1"]; cols = ["W1_2011-15", "W2_2016-19", "W3_2020-24", "2011-2024"]
    rows = [["__H__", "Treated persons"],
            ["  District-years, No."] + [f"{T[c]['n']:,}" for c in cols],
            ["  Treated person-years, million"] + [f"{T[c]['cases']/1e6:.1f}" for c in cols],
            ["  Person-years, million"] + [f"{T[c]['py']/1e6:.1f}" for c in cols],
            ["  Crude rate per 100,000"] + [f"{T[c]['crude']:,.0f}" for c in cols],
            ["  Age-standardized rate per 100,000<sup>a</sup>"] + [f"{T[c]['asr']:,.0f}" for c in cols],
            ["  District STR, median<sup>b</sup>"] + [f"{T[c]['sir_med']:.2f}" for c in cols],
            ["  District STR, P10-P90<sup>b</sup>"] + [f"{T[c]['sir_p10']:.2f}-{T[c]['sir_p90']:.2f}" for c in cols],
            ["__H__", "District characteristics, mean (SD)"]]
    for v, lab in TAB1_COV: rows.append([f"  {lab}"] + [f"{T[c]['cov'][v][0]:.1f} ({T[c]['cov'][v][1]:.1f})" for c in cols])
    foot = (f"<sup>a</sup> Direct standardization to the 2015 national population in ten age groups; window values are means of annual rates ({N['asr_2011']:,.0f} in 2011 and {N['asr_2024']:,.0f} in 2024). "
            "<sup>b</sup> Observed over indirectly age-standardized expected counts summed over the window. P10-P90, 10th-90th percentile; SD, standard deviation; STR, standardized treatment ratio.")
    return ("Table 1 People treated for arthritis and district characteristics by calendar window, Korea, 2011-2024", ["Characteristic", "2011-2015", "2016-2019", "2020-2024", "2011-2024"], rows, [6.2, 2.2, 2.2, 2.2, 2.2], foot)

GROUPS = [("Physical activity and recreation", ["walking_practice_rate", "moderate_pa_rate", "public_sports_facilities_per_100k", "community_gyms_per_100k", "public_pools_per_100k", "village_sports_facilities_per_100k", "older_leisure_facilities_per_1000"]),
          ("Health behaviors and status", ["screening_normalB_obesity_share", "current_smoking_rate", "high_risk_drinking_rate", "perceived_stress_rate", "good_self_rated_health_rate"]),
          ("Social structure", ["older_single_household_share", "employment_rate", "regular_employee_share"]),
          ("Environment and services", ["green_area_share", "beds_per_1000", "public_health_centre_use_rate"]),
          ("Forced controls", ["urban_population_share", "clinics_per_100k", "sex_ratio", "fiscal_independence", "pop80_share"])]
LABEL = {"walking_practice_rate": "Walking practice", "moderate_pa_rate": "Moderate or vigorous activity", "public_sports_facilities_per_100k": "Public sports facilities", "community_gyms_per_100k": "Public community gyms",
         "public_pools_per_100k": "Public swimming pools", "village_sports_facilities_per_100k": "Village sports facilities", "older_leisure_facilities_per_1000": "Senior leisure facilities",
         "screening_normalB_obesity_share": "Obesity management (screening)", "current_smoking_rate": "Current smoking", "high_risk_drinking_rate": "High-risk drinking", "perceived_stress_rate": "Perceived stress",
         "good_self_rated_health_rate": "Good self-rated health", "older_single_household_share": "Older single-person households", "employment_rate": "Employment rate", "regular_employee_share": "Regular employment",
         "green_area_share": "Green area share", "beds_per_1000": "Hospital beds", "public_health_centre_use_rate": "Public health center use",
         "urban_population_share": "Urban population share", "clinics_per_100k": "Clinics", "sex_ratio": "Sex ratio", "fiscal_independence": "Fiscal independence", "pop80_share": "Population aged 80 years or older"}
def table2():
    rows = []; assert sum(len(v) for g, v in GROUPS[:-1]) == N["n_hyp"]
    for g, vs in GROUPS:
        rows.append(["__H__", g])
        for v in vs:
            m = N["main"][v]; mv = N["mv"].get(v); k = N["s43"][("KH_typeIV", v)]
            rr = f"{m['IRR']:.3f} ({m['lo']:.3f}-{m['hi']:.3f})" + ("*" if m["cred"] else "")
            kk = f"{k[0]:.3f} ({k[1]:.3f}-{k[2]:.3f})" + ("*" if k[3] else "")
            rows.append([f"  {LABEL[v]}", rr, f"{100*mv['cred_frac']:.0f}" if mv else "NA", ("Yes" if mv["robust"] else "No") if mv else "NA", kk])
    foot = (f"Rate ratios (RRs) per 1 standard deviation with 95% credible intervals (CrIs); * 95% CrI excludes 1 (judged before rounding). Principal model: negative binomial with BYM2 district effect and random-walk and independent year effects (n = {N['n_rows']:,} district-years). "
            f"<sup>a</sup> Share of the 200 covariate-subset specifications containing the covariate in which its 95% CrI excluded 1. <sup>b</sup> Credible in at least 75% of specifications with the same sign in at least 95%. "
            f"Type IV adds a Knorr-Held type IV space-time interaction (ΔWAIC {C.dW('KH_typeIV'):,.0f}). NA, not applicable (forced controls were in every specification).")
    return ("Table 2 District correlates of age-standardized arthritis treatment, principal and space-time interaction models", ["Covariate", "Principal model RR (95% CrI)", "Credible %<sup>a</sup>", "Subset stable<sup>b</sup>", "Type IV model RR (95% CrI)"], rows, [5.1, 3.25, 1.7, 1.7, 3.25], foot)

FIGCAP = {
 1: "Geography and trend of arthritis treatment in Korea. (a) Residual spatial rate ratio (RR) by district, 2011-2024: posterior mean of the exponentiated BYM2 district effect from the principal model. Solid black outlines, hot spots (posterior probability RR > 1 above 0.95); dashed blue outlines, cold spots (below 0.05); thick gray lines, province boundaries. (b) National crude and directly age-standardized (2015 population) treatment rates.",
 2: "Persistence of the district pattern. (a) Emerging hot spot analysis of empirical Bayes-smoothed standardized treatment ratios, 2011-2024 (Getis-Ord Gi* with Mann-Kendall trend); numbers of districts in parentheses. (b) Number of calendar windows (2011-2015, 2016-2019, 2020-2024) in which each district was a hot or cold spot in the principal model refitted in each window.",
 3: "Subset-stable district correlates across models. Rate ratios per 1 standard deviation with 95% credible intervals from the principal model, models with Knorr-Held type II and type IV space-time interactions, and the principal model fitted to the number of people treated for infectious diseases as a comparison outcome; log scale.",
}

def title_page(D, wordcount, nrefs):
    J = JKMS(cite="bracket")
    J.para("<b>Title page</b>")
    J.para(f"<b>{C.TITLE}</b>")
    J.para("Seongdae Kim (ORCID 0000-0000-0000-0000)".replace("0000-0000-0000-0000", ORCID))
    J.para("Department of Biohealth Convergence Open Sharing System, Hongik University, 94 Wausan-ro, Mapo-gu, Seoul 04066, Republic of Korea")
    J.para("<b>Corresponding author:</b> Seongdae Kim, Department of Biohealth Convergence Open Sharing System, Hongik University, 94 Wausan-ro, Mapo-gu, Seoul 04066, Republic of Korea. Email: kimsd@hongik.ac.kr", before=6)
    abw = sum(len(re.sub(r'<[^>]+>', '', p).split()) for p in D['Abstract'])
    J.para(f"<b>Word count:</b> {wordcount:,} (main text); abstract {abw} words; 2 tables; 3 figures; {nrefs} references")
    J.head("Statements and Declarations", 1)
    for h, t in DECL: J.head(h, 2); J.para(t)
    return J

ORCID = "0000-0002-1525-0091"
DECL = [
 ("Funding", "No funding was received for conducting this study."),
 ("Competing interests", "The author has no relevant financial or non-financial interests to disclose."),
 ("Ethics approval", "The study was approved by the Institutional Review Board of Hongik University (approval no. 7002340-202511-HR-012). Only published aggregate district statistics were analyzed."),
 ("Consent to participate", "Not applicable. Informed consent was waived by the Institutional Review Board because only aggregated, deidentified public statistics were analyzed."),
 ("Consent to publish", "Not applicable."),
 ("Clinical trial number", "Not applicable."),
 ("Data availability", "All source data are publicly available aggregate statistics from the National Health Insurance Service, Statistics Korea (KOSIS), the Korea Disease Control and Prevention Agency, and the Ministry of Culture, Sports and Tourism, as cited in the Methods and listed in Online Resource 1 (Table S1)."),
 ("Code availability", "The analysis code is openly available on GitHub (GITHUB_URL) and archived on Zenodo (ZENODO_URL) under the MIT license."),
 ("Author contributions", "Seongdae Kim conceived and designed the study, curated the data, performed the analysis, interpreted the results, and wrote and revised the manuscript. The author read and approved the final manuscript."),
 ("Use of artificial intelligence", AI_STMT),
]

def build(wordcount=0, nrefs=0):
    D = read_draft(); J = JKMS(cite="bracket")
    J.para(f"<b>{C.TITLE}</b>")
    J.head("Abstract", 1)
    for p in D["Abstract"]: J.para(pandoc_cites(p))
    J.para(f"<b>Keywords</b> {C.KEYWORDS}", before=6)
    J.page_break(); J.counting = True
    J.head("1 Introduction", 1)
    for p in D["Introduction"]: J.para(pandoc_cites(p), indent=True)
    J.head("2 Materials and methods", 1)
    for i, (h, p) in enumerate(C.METHODS, 1): J.head(f"2.{i} {h}", 2); J.para(pandoc_cites(p), indent=True)
    J.head("3 Results", 1)
    for i, (h, p) in enumerate(C.RESULTS, 1): J.head(f"3.{i} {h}", 2); J.para(pandoc_cites(p), indent=True)
    J.head("4 Discussion", 1); sub = 0
    for p in D["Discussion"]:
        if p.startswith("### "): sub += 1; J.head(f"4.{sub} {p[4:].strip()}", 2); continue
        J.para(pandoc_cites(p), indent=True)
    J.head("5 Conclusion", 1)
    for p in D["Conclusion"]: J.para(pandoc_cites(p), indent=True)
    J.counting = False; bw = J.body_words
    J.page_break(); J.head("References", 1)
    for n, k in enumerate(J.cites, 1): J.para(f"{n}. {springer(REFS[k])}")
    J.page_break(); J.head("Figure captions", 1)
    for k in (1, 2, 3): J.para(f"<b>Fig. {k}</b> {FIGCAP[k].rstrip('.')}")
    for t in (table1(), table2()):
        J.page_break(); J.table(t[0], t[1], t[2], t[3], t[4], fs=9, title_bold=True)
    return J, bw, D

if __name__ == "__main__":
    J, bw, D = build(0); nr = len(J.cites); J, bw2, D = build(bw, nr); assert bw == bw2 and nr == len(J.cites)
    p = os.path.join(OUT, "Manuscript_anonymized.docx"); J.doc_title = C.TITLE; J.save(p)
    G = "https://github.com/Seongdae-Kim-Hongik/arthritis-care-geography-korea"; Z = f"https://doi.org/{ZENODO}" if ZENODO else "ZENODO_PENDING"
    DECL[:] = [(h, t.replace("GITHUB_URL", G).replace("ZENODO_URL", Z)) for h, t in DECL]
    T = title_page(D, bw, nr); pt = os.path.join(OUT, "Title_page.docx"); T.doc_title = C.TITLE; T.save(pt)
    for q in (p, pt): subprocess.run(["/opt/homebrew/bin/soffice", "--headless", "-env:UserInstallation=file:///tmp/lo_arth_ri", "--convert-to", "pdf", "--outdir", OUT, q], check=True, capture_output=True)
    abs_w = sum(len(re.sub(r"<[^>]+>", "", x).split()) for x in D["Abstract"])
    open(os.path.join(OUT, "wordcount.txt"), "w").write(f"body_words={bw}\nabstract_words={abs_w}\nrefs={len(J.cites)}\ntables=2\nfigures=3\n")
    print(f"body {bw} | abstract {abs_w} | refs {len(J.cites)}")
