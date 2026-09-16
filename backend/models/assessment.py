from pydantic import BaseModel
from typing import List, Optional


class QuestionAnswer(BaseModel):
    question: str
    answer: str


class AssessmentRequest(BaseModel):
    skill: str
    evidence: List[str]
    evidence_strength: str = "none"
    questions: List[QuestionAnswer]


class Round2Question(BaseModel):
    id: str
    type: str
    skill: str
    question: str
    starter_code: Optional[str] = None


class Round2Answer(BaseModel):
    id: str
    type: str
    skill: str
    question: str
    answer: str


class Round2EvaluationRequest(BaseModel):
    questions: List[Round2Answer]


class BatchSkillAssessment(BaseModel):
    skill: str
    evidence: List[str]
    evidence_strength: str = "none"
    questions: List[QuestionAnswer]


class BatchAssessmentRequest(BaseModel):
    round: int
    assessments: List[BatchSkillAssessment]