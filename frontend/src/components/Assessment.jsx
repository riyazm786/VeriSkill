import React, { useEffect, useState } from "react";

function Assessment({
  assessmentQuestions,
  onComplete,
  round = 1
}) {

  const [answers, setAnswers] = useState({});

  const questions = Object.entries(assessmentQuestions || {}).flatMap(
    ([skill, skillQuestions]) =>
      skillQuestions.map((item) => {
        if (typeof item === "string") {
          return {
            skill,
            question: item,
            type: "resume",
            starter_code: null
          };
        }

        return {
          skill: item.skill || skill,
          question: item.question,
          type: item.type || "technical",
          starter_code: item.starter_code || null,
          id: item.id || null
        };
      })
  );

  useEffect(() => {
    setAnswers({});
  }, [round]);

  const handleAnswerChange =
    (index, value) => {

      setAnswers(
        previous => ({
          ...previous,
          [index]: value
        })
      );
    };

  const handleSubmit = () => {

    const formattedAnswers =
      questions.map(
        (item, index) => ({
          skill: item.skill,
          question: item.question,
          answer: answers[index] || ""
        })
      );

    onComplete(formattedAnswers);
  };

  if (questions.length === 0) {
    return null;
  }

  const answeredCount =
    Object.values(answers).filter(
      answer => answer.trim().length > 0
    ).length;

  return (

    <section className="assessment-section">

      <div className="assessment-top-line">

        <div>

          <span className="section-label">

            {round === 1
              ? "ROUND 01 · RESUME INTELLIGENCE"
              : "ROUND 02 · TECHNICAL VERIFICATION"}

          </span>

          <h2>

            {round === 1
              ? "Resume Intelligence Assessment"
              : "Technical Verification Lab"}

          </h2>

          <p>

            {round === 1
              ? "Demonstrate your understanding of the skills and projects found in your resume."
              : "A deeper technical assessment generated from your previous performance."}

          </p>

        </div>


        <div className="assessment-progress">

          <strong>
            {answeredCount}
          </strong>

          <span>
            / {questions.length}
          </span>

          <small>
            answered
          </small>

        </div>

      </div>


      <div className="round-banner">

        <div className="round-indicator">

          <span>
            {round === 1 ? "01" : "02"}
          </span>

        </div>

        <div>

          <strong>

            {round === 1
              ? "Resume-grounded questions"
              : "Practical technical verification"}

          </strong>

          <p>

            {round === 1
              ? "Questions are connected to the candidate's technical profile."
              : "Focus on implementation, debugging, coding and technical reasoning."}

          </p>

        </div>

      </div>


      <div className="questions-container">

        {questions.map(
          (item, index) => (

            <div
              className="question-card"
              key={`${round}-${index}`}
            >

              <div className="question-top">

                <span className="question-number">

                  Q{String(index + 1).padStart(2, "0")}

                </span>

                <span className="question-type">

                  {round === 1
                    ? "RESUME GROUNDED"
                    : index === 0
                      ? "TECHNICAL CHALLENGE"
                      : "SCENARIO"}

                </span>

                <span className="question-skill">
                  {item.skill}
                </span>

              </div>


              <div className="challenge-label">

                Challenge {index + 1}

              </div>


              <div className="challenge-type">
                {item.type === "coding"
                  ? "CODING CHALLENGE"
                  : item.type === "debugging"
                    ? "DEBUGGING CHALLENGE"
                    : item.type === "technical_scenario"
                      ? "TECHNICAL SCENARIO"
                      : item.type === "engineering"
                        ? "ENGINEERING CHALLENGE"
                        : "RESUME GROUNDED"}
              </div>

              <h3>{item.question}</h3>

              {item.starter_code && (
                <pre className="starter-code">
                  <code>{item.starter_code}</code>
                </pre>
              )}


              <textarea
                value={answers[index] || ""}
                onChange={
                  event =>
                    handleAnswerChange(
                      index,
                      event.target.value
                    )
                }
                placeholder={
                  round === 1
                    ? "Explain your answer clearly. Include technical decisions, implementation details and examples."
                    : "Explain your approach, implementation, reasoning and how you would handle edge cases."
                }
                rows={7}
              />

              <div className="answer-hint">

                <span>
                  AI evaluated
                </span>

                <span>
                  Your response is compared with
                  resume evidence
                </span>

              </div>

            </div>

          )
        )}

      </div>


      <div className="assessment-submit-area">

        <div>

          <strong>

            {round === 1
              ? "Ready for Round 2?"
              : "Complete verification?"}

          </strong>

          <p>

            {round === 1
              ? "Your performance will determine the next technical assessment."
              : "Submit your final technical responses to generate the verification report."}

          </p>

        </div>


        <button
          className="submit-assessment"
          onClick={handleSubmit}
        >

          {round === 1
            ? "Submit Round 1 →"
            : "Generate Final Report →"}

        </button>

      </div>

    </section>
  );
}

export default Assessment;