import { useEffect, useState } from "react";
import "./App.css";
import Assessment from "./components/Assessment";
const API_BASE_URL =
  import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

function App() {
  // Always open VeriSkill at the homepage
  useEffect(() => {
    window.history.scrollRestoration = "manual";

    window.scrollTo({
      top: 0,
      left: 0,
      behavior: "auto"
    });

    return () => {
      window.history.scrollRestoration = "auto";
    };
  }, []);
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [assessmentQuestions, setAssessmentQuestions] = useState({});
  const [error, setError] = useState("");
  const [evaluation, setEvaluation] = useState(null);
  const [evaluationLoading, setEvaluationLoading] = useState(false);

  const [assessmentRound, setAssessmentRound] = useState(1);
  const [nextAssessmentQuestions, setNextAssessmentQuestions] =
    useState({});

  const scrollToSection = (id) => {
    document.getElementById(id)?.scrollIntoView({
      behavior: "smooth"
    });
  };

  const goHome = () => {
    window.scrollTo({
      top: 0,
      behavior: "smooth"
    });
  };

  const handleFileChange = (event) => {
    const selectedFile = event.target.files[0];

    if (!selectedFile) return;

    if (selectedFile.type !== "application/pdf") {
      setError("Please select a PDF resume.");
      setFile(null);
      return;
    }

    setFile(selectedFile);
    setError("");
    setResult(null);
    setEvaluation(null);
    setAssessmentRound(1);
    setNextAssessmentQuestions({});
  };

  const analyzeResume = async () => {
    if (!file) {
      setError("Please select a resume first.");
      return;
    }

    setLoading(true);
    setError("");

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch(
        `${API_BASE_URL}/resume/upload`,
        {
          method: "POST",
          body: formData
        }
      );

      if (!response.ok) {
        throw new Error("Failed to analyze resume.");
      }

      const data = await response.json();

      setResult(data);
      setAssessmentQuestions(
        data.assessment_questions || {}
      );

      setTimeout(() => {
        scrollToSection("analysis");
      }, 200);

    } catch (err) {
      console.error(err);

      setError(
        "Could not connect to VeriSkill backend. Make sure FastAPI is running."
      );
    } finally {
      setLoading(false);
    }
  };

  const handleAssessmentComplete = async (answers) => {
    setEvaluationLoading(true);
    setError("");

    try {
      // =========================================================
      // ROUND 1
      // =========================================================

      if (assessmentRound === 1) {
        const groupedAnswers = {};

        // IMPORTANT:
        // Keep ALL questions, including unanswered questions.
        // The backend already converts empty answers to 0 locally.
        answers.forEach((item) => {
          if (!groupedAnswers[item.skill]) {
            groupedAnswers[item.skill] = [];
          }

          groupedAnswers[item.skill].push({
            question: item.question,
            answer: item.answer ? item.answer.trim() : ""
          });
        });

        const evaluationResults = [];

        // Evaluate every assessment skill
        for (const [skill, questions] of Object.entries(groupedAnswers)) {
          const evidence =
            result?.skill_evidence?.[skill]?.evidence || [];

          const evidenceStrength =
            result?.skill_evidence?.[skill]?.evidence_strength || "none";

          const response = await fetch(
            `${API_BASE_URL}/assessment/evaluate`,
            {
              method: "POST",
              headers: {
                "Content-Type": "application/json"
              },
              body: JSON.stringify({
                skill,
                evidence,
                evidence_strength: evidenceStrength,
                questions
              })
            }
          );

          if (!response.ok) {
            throw new Error(`Failed to evaluate ${skill}`);
          }

          const data = await response.json();

          evaluationResults.push(data);
        }

        // Store complete Round 1 evaluation
        // including skills with 0 scores.
        setEvaluation(evaluationResults);

        // =======================================================
        // GENERATE ROUND 2
        // =======================================================

        const labResponse = await fetch(
          `${API_BASE_URL}/technical-lab`,
          {
            method: "POST",
            headers: {
              "Content-Type": "application/json"
            },
            body: JSON.stringify({
              skills:
                result?.assessment_skills ||
                result?.skills ||
                [],

              skill_evidence:
                result?.skill_evidence || {}
            })
          }
        );

        if (!labResponse.ok) {
          throw new Error(
            "Failed to generate Technical Verification Lab"
          );
        }

        const labData = await labResponse.json();

        const round2Questions = {};

        (labData.questions || []).forEach((item) => {
          if (!round2Questions[item.skill]) {
            round2Questions[item.skill] = [];
          }

          round2Questions[item.skill].push({
            id: item.id,
            type: item.type,
            question: item.question,
            starter_code: item.starter_code
          });
        });

        if (Object.keys(round2Questions).length === 0) {
          throw new Error(
            "No Round 2 questions were generated."
          );
        }

        setNextAssessmentQuestions(round2Questions);
        setAssessmentRound(2);

        setTimeout(() => {
          scrollToSection("assessment");
        }, 300);

        return;
      }

      // =========================================================
      // ROUND 2
      // =========================================================

      if (assessmentRound === 2) {
        const groupedAnswers = {};

        answers.forEach((item) => {
          if (!groupedAnswers[item.skill]) {
            groupedAnswers[item.skill] = [];
          }

          groupedAnswers[item.skill].push({
            question: item.question,
            answer: item.answer ? item.answer.trim() : ""
          });
        });

        const round2Results = [];

        for (const [skill, questions] of Object.entries(
          groupedAnswers
        )) {
          const evidence =
            result?.skill_evidence?.[skill]?.evidence || [];

          const evidenceStrength =
            result?.skill_evidence?.[skill]
              ?.evidence_strength || "none";

          const response = await fetch(
            `${API_BASE_URL}/assessment/evaluate`,
            {
              method: "POST",
              headers: {
                "Content-Type": "application/json"
              },
              body: JSON.stringify({
                skill,
                evidence,
                evidence_strength: evidenceStrength,
                questions
              })
            }
          );

          if (!response.ok) {
            throw new Error(
              `Failed to evaluate Round 2 ${skill}`
            );
          }

          const data = await response.json();

          round2Results.push(data);
        }

        // =======================================================
        // FINAL REPORT
        // =======================================================

        // Keep Round 1 results as the primary skill report.
        // This means unanswered Round 1 skills remain visible
        // with 0 scores instead of disappearing.
        setEvaluation((previousResults) => {
          const round1Results = previousResults || [];

          const combined = round1Results.map((round1Item) => {
            const round2Item = round2Results.find(
              (item) => item.skill === round1Item.skill
            );

            if (!round2Item) {
              return round1Item;
            }

            return {
              ...round1Item,

              round2_score: round2Item.overall_score,
              round2_evaluation:
                round2Item.overall_evaluation,
              round2_results: round2Item.results || []
            };
          });

          return combined;
        });

        setNextAssessmentQuestions({});

        setTimeout(() => {
          scrollToSection("final-report");
        }, 300);
      }

    } catch (err) {
      console.error(
        "Assessment evaluation error:",
        err
      );

      setError(
        "Could not evaluate assessment. Please check the backend and try again."
      );
    } finally {
      setEvaluationLoading(false);
    }
  };
  return (
    <div className="app">

      {/* ================================================= */}
      {/* NAVBAR */}
      {/* ================================================= */}

      <header className="navbar">

        <div
          className="brand"
          onClick={goHome}
        >
          <div className="brand-icon">
            V
          </div>

          <div>
            <div className="brand-name">
              VeriSkill
            </div>

            <div className="brand-subtitle">
              AI VERIFICATION PLATFORM
            </div>
          </div>
        </div>

        <nav className="nav-links">

          <button
            onClick={goHome}
          >
            Home
          </button>

          <button
            onClick={() =>
              scrollToSection("how-it-works")
            }
          >
            How it works
          </button>

          <button
            onClick={() =>
              scrollToSection("why-veriskill")
            }
          >
            Why VeriSkill
          </button>

          <button
            className="nav-cta"
            onClick={() =>
              scrollToSection("verification")
            }
          >
            Start Verification →
          </button>

        </nav>

      </header>


      {/* ================================================= */}
      {/* HERO */}
      {/* ================================================= */}

      <section className="hero-section">

        <div className="hero-orb orb-one"></div>
        <div className="hero-orb orb-two"></div>
        <div className="hero-grid"></div>

        <div className="hero-content">

          <div className="hero-badge">
            <span className="pulse-dot"></span>
            AI-POWERED TECHNICAL VERIFICATION
          </div>

          <h1>

            Don't just read the
            <br />

            <span className="gradient-text">
              resume.
            </span>

            <br />

            <span className="floating-word">
              Verify the skills behind it.
            </span>

          </h1>

          <p className="hero-description">

            VeriSkill transforms a candidate's resume into
            an intelligent, evidence-grounded technical
            assessment — helping verify what candidates
            actually understand.

          </p>

          <div className="hero-buttons">

            <button
              className="primary-button"
              onClick={() =>
                scrollToSection("verification")
              }
            >
              Start Verification
              <span>→</span>
            </button>

            <button
              className="secondary-button"
              onClick={() =>
                scrollToSection("how-it-works")
              }
            >
              Explore VeriSkill
            </button>

          </div>

          <div className="hero-flow">

            <span>Resume</span>
            <b>→</b>

            <span>Evidence</span>
            <b>→</b>

            <span>Assessment</span>
            <b>→</b>

            <span>Verification</span>

          </div>

        </div>

      </section>


      {/* ================================================= */}
      {/* PROBLEM */}
      {/* ================================================= */}

      <section className="problem-section">

        <div className="section-container">

          <div className="section-heading">

            <span className="section-label">
              THE PROBLEM
            </span>

            <h2>
              A resume tells you
              <span> what someone claims.</span>
            </h2>

            <p>
              But it doesn't always tell you what they
              can actually explain, build, or solve.
            </p>

          </div>

          <div className="problem-grid">

            <div className="problem-card">
              <div className="problem-icon">01</div>
              <h3>Skill inflation</h3>
              <p>
                Candidates can list many technologies
                without demonstrating meaningful
                understanding.
              </p>
            </div>

            <div className="problem-card">
              <div className="problem-icon">02</div>
              <h3>Generic interviews</h3>
              <p>
                Traditional screening often asks the
                same questions regardless of the
                candidate's actual experience.
              </p>
            </div>

            <div className="problem-card">
              <div className="problem-icon">03</div>
              <h3>Evidence gets lost</h3>
              <p>
                Important project and experience
                details buried inside resumes are
                rarely used during screening.
              </p>
            </div>

          </div>

        </div>

      </section>


      {/* ================================================= */}
      {/* HOW IT WORKS */}
      {/* ================================================= */}

      <section
        className="how-section"
        id="how-it-works"
      >

        <div className="section-container">

          <div className="section-heading center">

            <span className="section-label">
              HOW IT WORKS
            </span>

            <h2>
              From resume to
              <span> verified skills.</span>
            </h2>

            <p>
              VeriSkill creates an assessment pipeline
              around the candidate's own technical evidence.
            </p>

          </div>


          <div className="process-grid">

            <div className="process-card">

              <div className="process-number">
                01
              </div>

              <div className="process-icon">
                ↑
              </div>

              <h3>Upload Resume</h3>

              <p>
                Upload a candidate's PDF resume
                securely into the platform.
              </p>

            </div>


            <div className="process-card">

              <div className="process-number">
                02
              </div>

              <div className="process-icon">
                ◈
              </div>

              <h3>Resume Intelligence</h3>

              <p>
                Extract skills, sections, projects,
                experience and supporting evidence.
              </p>

            </div>


            <div className="process-card">

              <div className="process-number">
                03
              </div>

              <div className="process-icon">
                ?
              </div>

              <h3>Adaptive Assessment</h3>

              <p>
                Generate questions based on the
                candidate's actual resume evidence.
              </p>

            </div>


            <div className="process-card">

              <div className="process-number">
                04
              </div>

              <div className="process-icon">
                ✓
              </div>

              <h3>Verification Report</h3>

              <p>
                Evaluate technical quality and
                produce a structured verification report.
              </p>

            </div>

          </div>

        </div>

      </section>


      {/* ================================================= */}
      {/* WHY VERISKILL */}
      {/* ================================================= */}

      <section
        className="why-section"
        id="why-veriskill"
      >

        <div className="section-container">

          <div className="section-heading">

            <span className="section-label">
              WHY VERISKILL
            </span>

            <h2>
              More than a resume
              <span> analyzer.</span>
            </h2>

          </div>


          <div className="feature-grid">

            <div className="feature-card blue">

              <div className="feature-number">
                01
              </div>

              <h3>
                Evidence-Grounded
              </h3>

              <p>
                Questions are connected to skills
                and evidence extracted from the
                candidate's own resume.
              </p>

              <div className="feature-line"></div>

            </div>


            <div className="feature-card purple">

              <div className="feature-number">
                02
              </div>

              <h3>
                Adaptive
              </h3>

              <p>
                Assessment difficulty changes based
                on the candidate's demonstrated
                performance.
              </p>

              <div className="feature-line"></div>

            </div>


            <div className="feature-card green">

              <div className="feature-number">
                03
              </div>

              <h3>
                Technical
              </h3>

              <p>
                Move beyond theory with practical
                coding and technical problem-solving
                challenges.
              </p>

              <div className="feature-line"></div>

            </div>


            <div className="feature-card orange">

              <div className="feature-number">
                04
              </div>

              <h3>
                AI Evaluated
              </h3>

              <p>
                Answers are evaluated for relevance,
                technical correctness, depth and
                evidence alignment.
              </p>

              <div className="feature-line"></div>

            </div>

          </div>

        </div>

      </section>


      {/* ================================================= */}
      {/* WHAT IT ELIMINATES */}
      {/* ================================================= */}

      <section className="eliminate-section">

        <div className="section-container">

          <div className="eliminate-content">

            <div>

              <span className="section-label light">
                WHAT VERISKILL ELIMINATES
              </span>

              <h2>
                Less guessing.
                <br />
                More evidence.
              </h2>

            </div>

            <div className="eliminate-list">

              <div>
                <span>✓</span>
                Generic skill screening
              </div>

              <div>
                <span>✓</span>
                Resume-only evaluation
              </div>

              <div>
                <span>✓</span>
                Repetitive technical questions
              </div>

              <div>
                <span>✓</span>
                Keyword-based skill assumptions
              </div>

            </div>

          </div>

        </div>

      </section>


      {/* ================================================= */}
      {/* VERIFICATION */}
      {/* ================================================= */}

      <section
        className="verification-section"
        id="verification"
      >

        <div className="section-container">

          <div className="verification-header">

            <div>

              <span className="section-label">
                GET STARTED
              </span>

              <h2>
                Start candidate
                <span> verification.</span>
              </h2>

              <p>
                Upload a PDF resume and let VeriSkill
                build the technical assessment.
              </p>

            </div>

            <div className="verification-status">
              <span className="pulse-dot"></span>
              SYSTEM READY
            </div>

          </div>


          <div className="upload-card">

            <div className="upload-visual">

              <div className="upload-ring">
                ↑
              </div>

              <div className="upload-glow"></div>

            </div>

            <h3>
              Upload Candidate Resume
            </h3>

            <p>
              PDF format · Resume intelligence ·
              Evidence extraction
            </p>

            <label className="file-input">

              <input
                type="file"
                accept=".pdf"
                onChange={handleFileChange}
              />

              <span>
                {file
                  ? file.name
                  : "Choose PDF Resume"}
              </span>

            </label>

            {file && (

              <button
                className="analyze-button"
                onClick={analyzeResume}
                disabled={loading}
              >
                {loading
                  ? "Analyzing Resume..."
                  : "Analyze Resume →"}
              </button>

            )}

            {error && (
              <div className="error-box">
                {error}
              </div>
            )}

          </div>

        </div>

      </section>


      {/* ================================================= */}
      {/* ANALYSIS */}
      {/* ================================================= */}

      {result && (

        <section
          className="analysis-section"
          id="analysis"
        >

          <div className="section-container">

            <div className="analysis-success">

              <span className="success-dot">
                ✓
              </span>

              ANALYSIS COMPLETE

            </div>

            <div className="analysis-title">

              <div>

                <span className="section-label">
                  RESUME INTELLIGENCE
                </span>

                <h2>
                  Technical Profile
                </h2>

                <p>
                  {result.filename}
                </p>

              </div>

              <div className="analysis-check">
                ✓
              </div>

            </div>


            <div className="stats-grid">

              <div className="stat-card blue-stat">

                <span>SKILLS DETECTED</span>

                <strong>
                  {result.skills?.length || 0}
                </strong>

                <small>
                  Technical signals found
                </small>

              </div>


              <div className="stat-card purple-stat">

                <span>ASSESSMENT SKILLS</span>

                <strong>
                  {result.assessment_skills?.length || 0}
                </strong>

                <small>
                  Selected for verification
                </small>

              </div>


              <div className="stat-card green-stat">

                <span>EVIDENCE MAPPED</span>

                <strong>
                  {
                    Object.keys(
                      result.skill_evidence || {}
                    ).length
                  }
                </strong>

                <small>
                  Resume-backed signals
                </small>

              </div>

            </div>


            <div className="skills-panel">

              <div className="panel-header">

                <div>

                  <span className="section-label">
                    DETECTED PROFILE
                  </span>

                  <h3>
                    Technical Skills
                  </h3>

                </div>

                <span className="skill-count">
                  {result.skills?.length || 0}
                  {" "}skills
                </span>

              </div>

              {/* ================================================= */}
              {/* CANDIDATE SNAPSHOT */}
              {/* ================================================= */}

              <div className="candidate-snapshot">

                <div className="snapshot-header">

                  <div>
                    <span className="section-label">
                      CANDIDATE SNAPSHOT
                    </span>

                    <h3>
                      Recruiter Overview
                    </h3>

                    <p>
                      Key information extracted from the candidate's resume.
                    </p>
                  </div>

                  <div className="snapshot-badge">
                    RESUME INTELLIGENCE
                  </div>

                </div>


                {/* SUMMARY */}

                {result.candidate_profile?.summary?.length > 0 && (

                  <div className="profile-summary">

                    <div className="profile-icon">
                      ✦
                    </div>

                    <div>

                      <span className="profile-label">
                        PROFESSIONAL SUMMARY
                      </span>

                      <p>
                        {result.candidate_profile.summary.join(" ")}
                      </p>

                    </div>

                  </div>

                )}


                <div className="profile-grid">


                  {/* EDUCATION */}

                  <div className="profile-card">

                    <div className="profile-card-icon education-icon">
                      🎓
                    </div>

                    <div>

                      <span>
                        EDUCATION
                      </span>

                      <h4>
                        Academic Background
                      </h4>

                      {result.candidate_profile?.education?.length > 0 ? (

                        <ul>

                          {result.candidate_profile.education
                            .slice(0, 5)
                            .map((item, index) => (
                              <li key={index}>
                                {item}
                              </li>
                            ))}

                        </ul>

                      ) : (

                        <p className="not-available">
                          No education details detected.
                        </p>

                      )}

                    </div>

                  </div>


                  {/* EXPERIENCE */}

                  <div className="profile-card">

                    <div className="profile-card-icon experience-icon">
                      💼
                    </div>

                    <div>

                      <span>
                        EXPERIENCE
                      </span>

                      <h4>
                        Work & Internships
                      </h4>

                      {result.candidate_profile?.experience?.length > 0 ? (

                        <ul>

                          {result.candidate_profile.experience
                            .slice(0, 6)
                            .map((item, index) => (
                              <li key={index}>
                                {item}
                              </li>
                            ))}

                        </ul>

                      ) : (

                        <p className="not-available">
                          No experience details detected.
                        </p>

                      )}

                    </div>

                  </div>


                  {/* PROJECTS */}

                  <div className="profile-card profile-card-wide">

                    <div className="profile-card-icon project-icon">
                      ◈
                    </div>

                    <div>

                      <span>
                        PROJECTS
                      </span>

                      <h4>
                        Project Experience
                      </h4>

                      {result.candidate_profile?.projects?.length > 0 ? (

                        <div className="project-list">

                          {result.candidate_profile.projects
                            .slice(0, 8)
                            .map((item, index) => (

                              <div
                                className="project-item"
                                key={index}
                              >

                                <div className="project-number">
                                  {String(index + 1).padStart(2, "0")}
                                </div>

                                <p>
                                  {item}
                                </p>

                              </div>

                            ))}

                        </div>

                      ) : (

                        <p className="not-available">
                          No project details detected.
                        </p>

                      )}

                    </div>

                  </div>


                  {/* LANGUAGES */}

                  <div className="profile-card">

                    <div className="profile-card-icon language-icon">
                      {"</>"}
                    </div>

                    <div>

                      <span>
                        PROGRAMMING LANGUAGES
                      </span>

                      <h4>
                        Languages
                      </h4>

                      <div className="profile-tags">

                        {result.candidate_profile
                          ?.programming_languages
                          ?.length > 0 ? (

                          result.candidate_profile
                            .programming_languages
                            .map((language) => (

                              <span
                                className="profile-tag blue-tag"
                                key={language}
                              >
                                {language}
                              </span>

                            ))

                        ) : (

                          <p className="not-available">
                            No programming languages detected.
                          </p>

                        )}

                      </div>

                    </div>

                  </div>


                  {/* TECHNOLOGIES */}

                  <div className="profile-card">

                    <div className="profile-card-icon technology-icon">
                      ⚡
                    </div>

                    <div>

                      <span>
                        FRAMEWORKS & TOOLS
                      </span>

                      <h4>
                        Technical Stack
                      </h4>

                      <div className="profile-tags">

                        {result.candidate_profile
                          ?.frameworks_and_tools
                          ?.length > 0 ? (

                          result.candidate_profile
                            .frameworks_and_tools
                            .map((tool) => (

                              <span
                                className="profile-tag purple-tag"
                                key={tool}
                              >
                                {tool}
                              </span>

                            ))

                        ) : (

                          <p className="not-available">
                            No frameworks detected.
                          </p>

                        )}

                      </div>

                    </div>

                  </div>


                  {/* CERTIFICATIONS */}

                  <div className="profile-card">

                    <div className="profile-card-icon certification-icon">
                      ✓
                    </div>

                    <div>

                      <span>
                        CERTIFICATIONS
                      </span>

                      <h4>
                        Credentials
                      </h4>

                      {result.candidate_profile?.certifications?.length > 0 ? (

                        <ul>

                          {result.candidate_profile.certifications
                            .slice(0, 5)
                            .map((item, index) => (
                              <li key={index}>
                                {item}
                              </li>
                            ))}

                        </ul>

                      ) : (

                        <p className="not-available">
                          No certifications detected.
                        </p>

                      )}

                    </div>

                  </div>

                </div>

              </div>


              <div className="skills-list">

                {result.skills?.map((skill) => {

                  const evidence =
                    result.skill_evidence?.[skill];

                  const strength =
                    evidence?.evidence_strength ||
                    "unknown";

                  return (

                    <div
                      className={`skill-pill ${strength}`}
                      key={skill}
                    >

                      <span>
                        {skill}
                      </span>

                      <small>
                        {strength}
                      </small>

                    </div>

                  );

                })}

              </div>

            </div>

          </div>

        </section>

      )}


      {/* ================================================= */}
      {/* ASSESSMENT */}
      {/* ================================================= */}

      {Object.keys(
        assessmentRound === 1
          ? assessmentQuestions
          : nextAssessmentQuestions
      ).length > 0 && (

          <section
            className="assessment-wrapper"
            id="assessment"
          >

            <div className="section-container">

              <Assessment
                assessmentQuestions={
                  assessmentRound === 1
                    ? assessmentQuestions
                    : nextAssessmentQuestions
                }
                round={assessmentRound}
                onComplete={
                  handleAssessmentComplete
                }
              />

            </div>

          </section>

        )}


      {/* ================================================= */}
      {/* LOADING */}
      {/* ================================================= */}

      {evaluationLoading && (

        <section className="evaluation-loading">

          <div className="loader-ring"></div>

          <h2>
            AI is evaluating responses
          </h2>

          <p>
            Comparing technical answers against
            resume evidence...
          </p>

        </section>

      )}


      {/* ================================================= */}
      {/* FINAL REPORT */}
      {/* ================================================= */}

      {evaluation &&
        assessmentRound === 2 && (

          <section
            className="final-report"
            id="final-report"
          >

            <div className="section-container">

              <div className="report-header">

                <div>

                  <span className="section-label light">
                    FINAL VERIFICATION REPORT
                  </span>

                  <h2>
                    Candidate Verification
                  </h2>

                  <p>
                    AI-powered technical skill verification
                  </p>

                </div>

                <button
                  className="home-button"
                  onClick={goHome}
                >
                  ← Back to Home
                </button>

              </div>


              <div className="overall-report">

                <div>

                  <span>
                    VERIFICATION COMPLETE
                  </span>

                  <h3>
                    {result?.filename
                      ?.replace(".pdf", "")
                      || "Candidate"}
                  </h3>

                  <p>
                    {evaluation.length} technical
                    skills evaluated across
                    multiple assessment stages.
                  </p>

                </div>

                <div className="overall-score">

                  <small>
                    OVERALL SCORE
                  </small>

                  <strong>
                    {(
                      evaluation.reduce(
                        (sum, item) =>
                          sum +
                          Number(
                            item.overall_score || 0
                          ),
                        0
                      ) /
                      Math.max(
                        evaluation.length,
                        1
                      )
                    ).toFixed(1)}
                  </strong>

                  <span>/10</span>

                </div>

              </div>


              <div className="report-grid">

                {evaluation.map((item) => (

                  <div
                    className="report-card"
                    key={item.skill}
                  >

                    <div className="report-card-top">

                      <div>

                        <span>
                          VERIFIED SKILL
                        </span>

                        <h3>
                          {item.skill}
                        </h3>

                      </div>

                      <div className="mini-score">

                        {Number(
                          item.overall_score || 0
                        ).toFixed(1)}

                        <small>
                          /10
                        </small>

                      </div>

                    </div>


                    <div className="score-bar">

                      <div
                        style={{
                          width: `${(
                            Number(
                              item.overall_score || 0
                            ) * 10
                          )
                            }%`
                        }}
                      ></div>

                    </div>


                    <p className="evaluation-label">
                      {item.overall_evaluation}
                    </p>


                    {item.results?.[0]?.feedback && (

                      <div className="feedback-box">

                        <strong>
                          AI Feedback
                        </strong>

                        <p>
                          {
                            item.results[0].feedback
                          }
                        </p>

                      </div>

                    )}

                  </div>

                ))}

              </div>


              <div className="report-footer">

                <button
                  className="primary-button"
                  onClick={goHome}
                >
                  Start New Verification →
                </button>

              </div>

            </div>

          </section>

        )}


      {/* ================================================= */}
      {/* FOOTER */}
      {/* ================================================= */}

      <footer className="footer">

        <div className="footer-brand">

          <div className="brand-icon">
            V
          </div>

          <div>

            <strong>
              VeriSkill
            </strong>

            <span>
              AI VERIFICATION PLATFORM
            </span>

          </div>

        </div>

        <p>
          Resume intelligence · Adaptive assessment ·
          Technical verification
        </p>

        <span className="footer-copy">
          © 2026 VeriSkill
        </span>

      </footer>

    </div>
  );
}

export default App;