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
            "case1": CaseLibrary.case_1_early_stage_er_positive(),
            "case2": CaseLibrary.case_2_triple_negative(),
            "case3": CaseLibrary.case_3_her2_positive(),
            "case4": CaseLibrary.case_4_metastatic(),
            "case5": CaseLibrary.case_5_borderline_chemo(),
            "case6": CaseLibrary.case_6_adjuvant_vs_neoadjuvant(),
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
    def case_1_early_stage_er_positive() -> CaseScenario:
        """Early-stage ER+/PR+/HER2- breast cancer"""
        return CaseScenario(
            case_id="case1",
            title="Early-stage ER+/PR+ Breast Cancer",
            patient_age=52,
            diagnosis="Invasive ductal carcinoma, left breast",
            stage="IIA (T2N0M0)",
            histology="Invasive ductal carcinoma (IDC)",
            grade="Grade 2 (moderately differentiated)",
            tumor_size="2.5 cm",
            nodes="0/3 sentinel nodes positive",
            biomarkers={
                "ER": "95% positive",
                "PR": "80% positive",
                "HER2": "Negative (IHC 1+)",
                "Ki-67": "18%"
            },
            genomics={
                "Oncotype DX": "Recurrence Score 22 (Intermediate)"
            },
            comorbidities=["Controlled hypertension", "Hypothyroidism on levothyroxine"],
            performance_status="ECOG 0 (fully active)",
            additional_context="""Patient underwent lumpectomy with sentinel lymph node biopsy 3 weeks ago.
Margins are clear. She is now here to discuss adjuvant treatment planning. She is very anxious
about making the right treatment decisions and wants to understand all her options."""
        )

    @staticmethod
    def case_2_triple_negative() -> CaseScenario:
        """Triple-negative breast cancer with node involvement"""
        return CaseScenario(
            case_id="case2",
            title="Triple-Negative Breast Cancer",
            patient_age=48,
            diagnosis="Invasive ductal carcinoma, right breast",
            stage="IIIA (T3N2M0)",
            histology="Invasive ductal carcinoma (IDC)",
            grade="Grade 3 (poorly differentiated)",
            tumor_size="4.2 cm",
            nodes="3/12 axillary nodes positive",
            biomarkers={
                "ER": "Negative (0%)",
                "PR": "Negative (0%)",
                "HER2": "Negative (IHC 0)",
                "Ki-67": "65%"
            },
            genomics={
                "BRCA1/2 testing": "Negative (germline)",
                "PD-L1": "CPS 15 (positive)"
            },
            comorbidities=["None"],
            performance_status="ECOG 0 (fully active)",
            additional_context="""Patient completed neoadjuvant chemotherapy (dose-dense AC-T with pembrolizumab)
4 weeks ago. She underwent mastectomy with axillary lymph node dissection. Pathology showed residual
cancer burden RCB-II (moderate residual disease). She is here to discuss adjuvant/post-neoadjuvant
treatment options."""
        )

    @staticmethod
    def case_3_her2_positive() -> CaseScenario:
        """HER2-positive breast cancer"""
        return CaseScenario(
            case_id="case3",
            title="HER2-Positive Breast Cancer",
            patient_age=56,
            diagnosis="Invasive ductal carcinoma, left breast",
            stage="IIB (T2N1M0)",
            histology="Invasive ductal carcinoma (IDC)",
            grade="Grade 3 (poorly differentiated)",
            tumor_size="3.0 cm",
            nodes="2/8 axillary nodes positive",
            biomarkers={
                "ER": "Negative (5%)",
                "PR": "Negative (0%)",
                "HER2": "Positive (IHC 3+)",
                "Ki-67": "45%"
            },
            genomics=None,
            comorbidities=["Well-controlled Type 2 Diabetes", "Mild asthma"],
            performance_status="ECOG 1 (symptomatic but ambulatory)",
            additional_context="""Patient diagnosed 2 weeks ago via core needle biopsy.
Staging workouts (CT chest/abdomen/pelvis, bone scan) negative for distant metastases.
MUGA scan shows LVEF 60% (normal). She is here to discuss treatment plan. Patient works full-time
and is concerned about treatment duration and impact on her work."""
        )

    @staticmethod
    def case_4_metastatic() -> CaseScenario:
        """Metastatic breast cancer with bone and liver involvement"""
        return CaseScenario(
            case_id="case4",
            title="Metastatic ER+ Breast Cancer (De Novo)",
            patient_age=59,
            diagnosis="Metastatic invasive ductal carcinoma",
            stage="IV (de novo metastatic)",
            histology="Invasive ductal carcinoma (IDC)",
            grade="Grade 2 (moderately differentiated)",
            tumor_size="5.5 cm primary in right breast",
            nodes="Clinical N2 (palpable axillary nodes)",
            biomarkers={
                "ER": "90% positive",
                "PR": "70% positive",
                "HER2": "Negative (IHC 1+)",
                "Ki-67": "25%"
            },
            genomics={
                "Foundation Medicine": "PIK3CA H1047R mutation detected",
                "ESR1 mutations": "Not detected",
                "TMB": "3 mutations/Mb (low)"
            },
            comorbidities=["Osteoporosis", "GERD"],
            performance_status="ECOG 1 (symptomatic with back pain, but ambulatory)",
            additional_context="""Patient presented with back pain. Imaging revealed diffuse bone metastases
(spine, ribs, pelvis) and 3 liver lesions (largest 2.2 cm). Biopsy of liver lesion confirmed metastatic
breast cancer. She is postmenopausal. This is her first diagnosis of breast cancer (de novo stage IV).
She is here to discuss first-line treatment options for metastatic disease."""
        )

    @staticmethod
    def case_5_borderline_chemo() -> CaseScenario:
        """Borderline case where chemotherapy benefit is uncertain"""
        return CaseScenario(
            case_id="case5",
            title="Borderline Chemotherapy Indication",
            patient_age=67,
            diagnosis="Invasive lobular carcinoma, right breast",
            stage="IB (T1cN0M0)",
            histology="Invasive lobular carcinoma (ILC)",
            grade="Grade 2 (moderately differentiated)",
            tumor_size="1.8 cm",
            nodes="0/2 sentinel nodes positive",
            biomarkers={
                "ER": "100% positive",
                "PR": "95% positive",
                "HER2": "Negative (IHC 0)",
                "Ki-67": "12%"
            },
            genomics={
                "Oncotype DX": "Recurrence Score 18 (Intermediate, closer to low)"
            },
            comorbidities=[
                "Chronic kidney disease stage 3a",
                "Atrial fibrillation on anticoagulation",
                "Osteoarthritis"
            ],
            performance_status="ECOG 1 (limited strenuous activity, but ambulatory)",
            additional_context="""Patient underwent lumpectomy 4 weeks ago with clear margins and negative
sentinel nodes. Given her Oncotype score of 18, chemotherapy benefit is uncertain per recent RxPONDER data
(postmenopausal, node-negative). She has significant comorbidities that might increase chemotherapy risk.
Patient is seeking guidance on whether chemotherapy is necessary or if endocrine therapy alone is sufficient."""
        )

    @staticmethod
    def case_6_adjuvant_vs_neoadjuvant() -> CaseScenario:
        """Newly diagnosed ER+ breast cancer - discussing adjuvant vs neoadjuvant chemotherapy"""
        return CaseScenario(
            case_id="case6",
            title="Adjuvant vs Neoadjuvant Chemotherapy Decision",
            patient_age=49,
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
                "Oncotype DX": "Recurrence Score 26 (Intermediate-High, chemo benefit expected)"
            },
            comorbidities=["None"],
            performance_status="ECOG 0 (fully active)",
            additional_context="""Patient diagnosed 2 weeks ago via core needle biopsy. Staging complete -
no evidence of distant metastases. Given Oncotype DX of 26, chemotherapy is indicated along with
endocrine therapy. She is here to discuss treatment sequencing: adjuvant chemotherapy (surgery first,
then chemo) versus neoadjuvant chemotherapy (chemo first, then surgery). She is interested in
breast-conserving surgery if possible and wants to understand the pros and cons of each approach."""
        )


# Create a singleton instance for easy access
case_library = CaseLibrary()
