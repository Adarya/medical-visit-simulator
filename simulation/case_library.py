"""
Case Library
Pre-defined breast cancer case scenarios for simulation
"""
from dataclasses import dataclass
from typing import Optional, Dict, List


@dataclass
class CaseScenario:
    """Breast cancer case scenario"""
    case_id: str
    title: str
    patient_age: int
    diagnosis: str
    stage: str
    histology: str
    grade: str
    tumor_size: str
    nodes: str
    biomarkers: Dict[str, str]
    genomics: Optional[Dict[str, str]]
    comorbidities: List[str]
    performance_status: str
    additional_context: str

    def format_for_prompt(self) -> str:
        """Format case as a clinical presentation for the oncologist"""
        biomarker_str = ", ".join([f"{k}: {v}" for k, v in self.biomarkers.items()])
        genomic_str = ""
        if self.genomics:
            genomic_str = "\n" + "\n".join([f"  - {k}: {v}" for k, v in self.genomics.items()])

        comorbidity_str = ", ".join(self.comorbidities) if self.comorbidities else "None"

        return f"""PATIENT CASE PRESENTATION:

Age: {self.patient_age} years old
Diagnosis: {self.diagnosis}
Stage: {self.stage}

PATHOLOGY:
- Histology: {self.histology}
- Grade: {self.grade}
- Tumor Size: {self.tumor_size}
- Lymph Nodes: {self.nodes}

BIOMARKERS:
- {biomarker_str}

GENOMIC TESTING:{genomic_str if genomic_str else " Not yet performed"}

MEDICAL HISTORY:
- Comorbidities: {comorbidity_str}
- Performance Status: {self.performance_status}

ADDITIONAL CONTEXT:
{self.additional_context}"""


class CaseLibrary:
    """Library of pre-defined cases"""

    @staticmethod
    def get_all_cases() -> Dict[str, CaseScenario]:
        """Get all available cases"""
        return {
            "brca2_case": CaseLibrary.brca2_carrier_adjuvant_vs_neoadjuvant(),
        }

    @staticmethod
    def get_case(case_id: str) -> Optional[CaseScenario]:
        """Get specific case by ID"""
        return CaseLibrary.get_all_cases().get(case_id)

    @staticmethod
    def get_case_titles() -> Dict[str, str]:
        """Get case IDs and titles for selection"""
        cases = CaseLibrary.get_all_cases()
        return {case_id: case.title for case_id, case in cases.items()}

    @staticmethod
    def brca2_carrier_adjuvant_vs_neoadjuvant() -> CaseScenario:
        """BRCA2 carrier with ER+ breast cancer - discussing comprehensive treatment plan"""
        return CaseScenario(
            case_id="brca2_case",
            title="BRCA2 Carrier: Comprehensive Treatment Planning",
            patient_age=40,
            diagnosis="Invasive ductal carcinoma, left breast",
            stage="IIA (T2N0M0)",
            histology="Invasive ductal carcinoma (IDC)",
            grade="Grade 2 (moderately differentiated)",
            tumor_size="2.8 cm (by imaging and clinical exam)",
            nodes="Clinically node-negative (no palpable nodes, normal ultrasound)",
            biomarkers={
                "ER": "90% positive",
                "PR": "75% positive",
                "HER2": "Negative (IHC 1+)",
                "Ki-67": "22%"
            },
            genomics={
                "Oncotype DX": "Recurrence Score 26 (Intermediate-High, chemo benefit expected)",
                "BRCA2": "Known germline mutation (diagnosed 3 years ago after mother's breast cancer)"
            },
            comorbidities=["None"],
            performance_status="ECOG 0 (fully active)",
            additional_context="""Patient is a 40-year-old premenopausal woman with newly diagnosed breast cancer.
She was diagnosed 2 weeks ago via core needle biopsy. Staging workup complete - no distant metastases.

BRCA2 STATUS (KNOWN): Patient has a known pathogenic BRCA2 germline mutation, diagnosed 3 years ago when her
mother was diagnosed with breast cancer at age 45. She has been in high-risk surveillance (annual MRI + mammogram).
Current cancer was detected on routine screening MRI. Her two sisters have also tested positive for the same
BRCA2 mutation; one had prophylactic bilateral mastectomy last year.

THREE TREATMENT COMPONENTS TO DISCUSS:

1. CHEMOTHERAPY (DEFINITELY INDICATED):
   - Oncotype DX 26 = clear chemotherapy benefit per TAILORx trial data
   - Standard regimen options: TC (docetaxel/cyclophosphamide) × 4 cycles OR dose-dense AC-T
   - Duration: 3-4 months
   - Side effects: Hair loss, nausea, fatigue, neutropenia risk, premature menopause risk

2. ENDOCRINE THERAPY (ESSENTIAL - ER 90% POSITIVE):
   - Premenopausal ER+ disease requires discussion of:
     * Tamoxifen alone (5-10 years) - standard of care
     * Ovarian suppression + aromatase inhibitor (more aggressive, used in high-risk premenopausal)
     * Ovarian suppression methods: monthly injections (Lupron) vs. surgical removal
   - Must continue for at least 5 years, possibly 10 years
   - Side effects: Hot flashes, mood changes, bone density loss (with AI), menopausal symptoms

3. SURGERY - TIMING AND EXTENT (KEY DECISION POINT):

   TIMING OPTIONS:
   a) ADJUVANT SEQUENCE: Surgery → Chemo → Endocrine therapy (traditional approach)
      - Pros: Immediate tumor removal, accurate pathologic staging, patient preference for "getting it out"
      - Cons: Larger tumor may require wider excision, miss chance to downstage

   b) NEOADJUVANT SEQUENCE: Chemo → Surgery → Endocrine therapy (increasingly common)
      - Pros: May shrink tumor (better cosmetic outcome with lumpectomy), in vivo test of chemo sensitivity,
        pathologic complete response (pCR) is prognostic, growing evidence base
      - Cons: Delays definitive local control, requires more monitoring, patient anxiety about "waiting"
      - NOTE: RxPONDER trial shows neoadjuvant approach is equivalent for survival in ER+ disease

   EXTENT OPTIONS (BRCA2 impacts this significantly):
   a) Breast-conserving surgery (lumpectomy) + radiation
      - Patient's preference
      - Feasible for 2.8 cm tumor (may be even smaller after neoadjuvant chemo if chosen)
      - Requires radiation therapy (6 weeks, 5 days/week)
      - BUT: As BRCA2 carrier, 40% risk of contralateral breast cancer - will need ongoing surveillance

   b) Unilateral mastectomy (left breast only)
      - Treats current cancer
      - Avoids radiation
      - Still need surveillance of right breast (BRCA2 risk remains)

   c) Bilateral mastectomy (both breasts)
      - Treats current cancer AND eliminates future breast cancer risk
      - Many BRCA2+ patients choose this (her sister did prophylactically)
      - Reconstruction options: immediate vs. delayed; implant vs. autologous (DIEP flap)
      - Major surgery with longer recovery but eliminates surveillance burden

PATIENT CONTEXT:
- Married with two children (ages 5 and 8)
- Works full-time (elementary school teacher)
- Strong family history: Mother (breast cancer at 45), maternal aunt (ovarian cancer at 52)
- Two sisters both BRCA2+; one already had prophylactic bilateral mastectomy
- Has been anxious about "when, not if" she'd get cancer since genetic testing 3 years ago
- Wants to "do everything right" and minimize future risk
- Concerned about treatment impact on ability to care for children during school year
- Asking about optimal timing to start treatment (summer vs. during school year)

ADDITIONAL CONSIDERATIONS FOR DISCUSSION:
- Risk-reducing salpingo-oophorectomy (removing ovaries): typically recommended by age 40-45 in BRCA2 carriers
  (10-20% ovarian cancer risk). Could be done after cancer treatment completed.
- Genetic counseling for her children (50% chance each child inherited BRCA2)
- Fertility preservation: Chemo may cause premature ovarian failure - should she consider egg/embryo freezing?
  (Would delay treatment start by 2-3 weeks)

SUMMARY FOR ONCOLOGIST:
This visit should cover ALL THREE treatment components comprehensively:
1. Chemotherapy: Which regimen, what to expect
2. Endocrine therapy: Tamoxifen vs. ovarian suppression + AI, duration
3. Surgery: Adjuvant vs. neoadjuvant timing AND lumpectomy vs. unilateral vs. bilateral mastectomy extent

The BRCA2 mutation significantly influences surgical decision-making but doesn't change chemo/endocrine indications."""
        )


# Create a singleton instance for easy access
case_library = CaseLibrary()
