"use client";

import React, { useState } from "react";
import "./ResponseMetadata.css";

interface ResponseMetadataProps {
    metadata?: {
        firstperson_orchestrator?: {
            mortality_salience?: number;
            memory_context_injected?: boolean;
            frequency_reflection?: string;
            safety_signal?: boolean;
            affect_analysis?: {
                valence?: number;
                intensity?: number;
            };
        };
    };
    messageId: string;
    onFeedback?: (messageId: string, helpful: boolean) => void;
}

export const ResponseMetadata: React.FC<ResponseMetadataProps> = ({
    metadata,
    messageId,
    onFeedback,
}) => {
    const [feedback, setFeedback] = useState<boolean | null>(null);
    const [showDetails, setShowDetails] = useState(false);

    const orchestrator = metadata?.firstperson_orchestrator;
    if (!orchestrator) return null;

    const mortality = orchestrator.mortality_salience ?? 0;
    const isSafetySignal = orchestrator.safety_signal ?? false;
    const hasMemoryContext = orchestrator.memory_context_injected ?? false;
    const affect = orchestrator.affect_analysis ?? {};

    // Determine indicator color based on mortality salience
    const getMortalityColor = (val: number) => {
        if (val > 0.6) return "high"; // Warm/urgent
        if (val > 0.3) return "moderate"; // Gentle
        return "low"; // Neutral
    };

    const handleFeedback = (helpful: boolean) => {
        setFeedback(helpful);
        onFeedback?.(messageId, helpful);
        setTimeout(() => setFeedback(null), 2000); // Reset after 2s
    };

    return (
        <div className="response-metadata">
            {/* Safety signal alert if triggered */}
            {isSafetySignal && (
                <div className="safety-alert">
                    <span className="alert-icon">⚠</span>
                    <span className="alert-text">
                        I'm noticing something important. If you need immediate support, please reach out to a counselor or call a helpline.
                    </span>
                </div>
            )}

            {/* Mortality salience indicator */}
            {mortality > 0 && (
                <div className="mortality-indicator">
                    <div className={`indicator-dot ${getMortalityColor(mortality)}`} />
                    <span className="indicator-label">
                        Meaning-oriented response
                    </span>
                    <button
                        className="details-toggle"
                        onClick={() => setShowDetails(!showDetails)}
                        aria-label="Toggle details"
                    >
                        ℹ
                    </button>
                </div>
            )}

            {/* Memory context indicator */}
            {hasMemoryContext && (
                <div className="memory-indicator">
                    <span className="memory-icon">📝</span>
                    <span className="memory-text">Using conversation memory</span>
                </div>
            )}

            {/* Detailed breakdown (optional) */}
            {showDetails && (
                <div className="metadata-details">
                    <div className="detail-row">
                        <span className="detail-label">Finitude salience:</span>
                        <span className="detail-value">{(mortality * 100).toFixed(0)}%</span>
                    </div>
                    {affect.valence !== undefined && (
                        <div className="detail-row">
                            <span className="detail-label">Emotional tone:</span>
                            <span className="detail-value">
                                {affect.valence > 0.3 ? "positive" : affect.valence < -0.3 ? "challenging" : "neutral"}
                            </span>
                        </div>
                    )}
                    {affect.intensity !== undefined && (
                        <div className="detail-row">
                            <span className="detail-label">Intensity:</span>
                            <span className="detail-value">{(affect.intensity * 100).toFixed(0)}%</span>
                        </div>
                    )}
                </div>
            )}

            {/* Feedback buttons */}
            <div className="feedback-buttons">
                <button
                    className={`feedback-btn ${feedback === true ? "active" : ""}`}
                    onClick={() => handleFeedback(true)}
                    disabled={feedback !== null}
                    title="This response was helpful"
                >
                    👍 Helpful
                </button>
                <button
                    className={`feedback-btn ${feedback === false ? "active" : ""}`}
                    onClick={() => handleFeedback(false)}
                    disabled={feedback !== null}
                    title="This response wasn't helpful"
                >
                    👎 Not helpful
                </button>
            </div>
        </div>
    );
};

export default ResponseMetadata;
