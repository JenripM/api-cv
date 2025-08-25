"""
Esquemas Pydantic para el análisis de CV usando Gemini
Dividido en dos partes para procesamiento paralelo
"""
from pydantic import BaseModel
from typing import List, Optional, Union


# ===== ESQUEMA PARTE 1: ANÁLISIS BÁSICO =====
# Campos que requieren análisis general del CV y formato
class Metadata(BaseModel):
    candidate_name: str


class FilenameAnalysis(BaseModel):
    filename: str
    ai_feedback: str


class DocumentSizeAnalysis(BaseModel):
    total_pages: int
    ai_feedback: str


class SpellingError(BaseModel):
    current: str
    recommended: str


class SpellingAnalysis(BaseModel):
    errors_found: List[SpellingError]
    spelling_errors: int
    ai_feedback: str


class EssentialElement(BaseModel):
    element: str
    exists: bool
    well_positioned: bool
    easily_distinguishable: bool


class EssentialElements(BaseModel):
    evaluation: List[EssentialElement]
    ai_feedback: str


class FormatOptimizationItem(BaseModel):
    status: str  # "Alto", "Medio", "Bajo"
    ai_feedback: str


class FormatOptimization(BaseModel):
    length: FormatOptimizationItem
    photo: FormatOptimizationItem
    keywords: FormatOptimizationItem


class ImpactVerbsAnalysis(BaseModel):
    score: int
    ai_feedbacks: List[str]


class RoleFitItem(BaseModel):
    level: str  # "Alto", "Medio", "Bajo"
    ai_feedback: str


class RoleFitAnalysis(BaseModel):
    analysis_skills: RoleFitItem
    quantifiable_results: RoleFitItem


class ATSCompliance(BaseModel):
    score: int
    issues: List[str]
    ai_feedbacks: List[str]


class MainAnalysis(BaseModel):
    score: int
    ai_feedback: str


# Esquema para la Parte 1: Análisis Básico (formato, ortografía, elementos esenciales)
class CVAnalysisBasic(BaseModel):
    metadata: Metadata
    filename_analysis: FilenameAnalysis
    document_size_analysis: DocumentSizeAnalysis
    spelling_analysis: SpellingAnalysis
    essential_elements: EssentialElements
    format_optimization: FormatOptimization
    impact_verbs_analysis: ImpactVerbsAnalysis
    role_fit_analysis: RoleFitAnalysis
    ats_compliance: ATSCompliance
    main_analysis: MainAnalysis
    common_errors: str
    strengths: str


# ===== ESQUEMA PARTE 2: ANÁLISIS DETALLADO =====
# Campos que requieren análisis profundo de contenido específico
class WorkExperience(BaseModel):
    company: str
    current: str
    recommended: str


class SkillsToolsAnalysis(BaseModel):
    current_skills: str
    ai_feedback: str


class Volunteering(BaseModel):
    organization: str
    current: str
    recommended: str


class Education(BaseModel):
    degree: str
    institution: str
    date: str
    ai_feedback: str


class KeywordsAnalysis(BaseModel):
    found_keywords: List[str]
    missing_keywords: List[str]
    general_skills: List[str]
    ai_feedback: str


class ExecutiveSummaryAnalysis(BaseModel):
    current: str
    recommended: str


# Esquema para la Parte 2: Análisis Detallado (experiencia, educación, keywords)
class CVAnalysisDetailed(BaseModel):
    work_experience_analysis: List[WorkExperience]
    skills_tools_analysis: SkillsToolsAnalysis
    volunteering_analysis: List[Volunteering]
    education_analysis: List[Education]
    keywords_analysis: KeywordsAnalysis
    executive_summary_analysis: ExecutiveSummaryAnalysis


# ===== ESQUEMA COMPLETO (resultado final) =====
class CVAnalysisResult(BaseModel):
    metadata: Metadata
    filename_analysis: FilenameAnalysis
    document_size_analysis: DocumentSizeAnalysis
    spelling_analysis: SpellingAnalysis
    essential_elements: EssentialElements
    format_optimization: FormatOptimization
    impact_verbs_analysis: ImpactVerbsAnalysis
    role_fit_analysis: RoleFitAnalysis
    work_experience_analysis: List[WorkExperience]
    skills_tools_analysis: SkillsToolsAnalysis
    volunteering_analysis: List[Volunteering]
    education_analysis: List[Education]
    keywords_analysis: KeywordsAnalysis
    executive_summary_analysis: ExecutiveSummaryAnalysis
    ats_compliance: ATSCompliance
    main_analysis: MainAnalysis
    common_errors: str
    strengths: str
