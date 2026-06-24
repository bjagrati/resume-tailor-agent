// ────────────── Helpers ──────────────

async function api(path, options = {}) {
    const response = await fetch(path, options);
    if (!response.ok) {
        const errBody = await response.json().catch(() => ({}));
        throw new Error(errBody.detail || `HTTP ${response.status}`);
    }
    return response.json();
}

function setStatus(type, message) {
    const el = document.getElementById("status");
    el.className = "status " + type;
    el.textContent = message;
}

function clearStatus() {
    const el = document.getElementById("status");
    el.className = "status";
    el.textContent = "";
}

function escapeHtml(text) {
    const div = document.createElement("div");
    div.textContent = String(text);
    return div.innerHTML;
}

// ────────────── Input mode toggle ──────────────

let inputMode = "paste"; // 'paste' or 'upload'

document.querySelectorAll(".toggle-btn").forEach(btn => {
    btn.addEventListener("click", () => {
        document.querySelectorAll(".toggle-btn").forEach(b => b.classList.remove("active"));
        btn.classList.add("active");
        inputMode = btn.dataset.mode;
        
        const textarea = document.getElementById("resume-text");
        const fileInput = document.getElementById("resume-file");
        if (inputMode === "paste") {
            textarea.style.display = "";
            fileInput.style.display = "none";
        } else {
            textarea.style.display = "none";
            fileInput.style.display = "";
        }
    });
});

// ────────────── Analyze ──────────────

document.getElementById("analyze-btn").addEventListener("click", async () => {
    const jdText = document.getElementById("jd-text").value.trim();
    if (!jdText) {
        setStatus("error", "Please paste the job description.");
        return;
    }
    
    const btn = document.getElementById("analyze-btn");
    btn.disabled = true;
    setStatus("info", "Analyzing... this takes 30-45 seconds.");
    
    try {
        let analysis;
        
        if (inputMode === "paste") {
            const resumeText = document.getElementById("resume-text").value.trim();
            if (!resumeText) {
                throw new Error("Please paste your résumé.");
            }
            analysis = await api("/analyze/text", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ resume_text: resumeText, jd_text: jdText }),
            });
        } else {
            const fileInput = document.getElementById("resume-file");
            const file = fileInput.files[0];
            if (!file) {
                throw new Error("Please select a résumé file.");
            }
            const formData = new FormData();
            formData.append("resume_file", file);
            formData.append("jd_text", jdText);
            analysis = await api("/analyze/upload", {
                method: "POST",
                body: formData,
            });
        }
        
        renderAnalysis(analysis);
        clearStatus();
    } catch (e) {
        setStatus("error", "Analysis failed: " + e.message);
    } finally {
        btn.disabled = false;
    }
});

// ────────────── Render results ──────────────

function renderAnalysis(a) {
    // Show results section, scroll to it
    document.getElementById("results-section").style.display = "";
    
    // Score + summary
    document.getElementById("score-value").textContent = a.gap.alignment_score;
    document.getElementById("gap-summary").textContent = a.gap.summary;
    
    // Required skills
    renderSkillMatches("required-skills", a.gap.required_skill_matches);
    renderSkillMatches("nice-to-have", a.gap.nice_to_have_matches);
    
    // Gaps
    const gapsList = document.getElementById("gaps-list");
    gapsList.innerHTML = a.gap.biggest_gaps
        .map(g => `<li>${escapeHtml(g)}</li>`)
        .join("");
    
    // Missing keywords
    document.getElementById("missing-keywords").textContent =
        a.gap.missing_keywords.length ? a.gap.missing_keywords.join(", ") : "None.";
    
    // Bullet recommendations
    renderBulletRecs(a.recommendations.bullet_recommendations);
    
    // Extras
    document.getElementById("suggested-summary").textContent =
        a.recommendations.suggested_summary || "(No summary suggestion.)";
    document.getElementById("skills-to-add").textContent =
        a.recommendations.additional_skills_to_add.length
            ? a.recommendations.additional_skills_to_add.join(", ")
            : "None.";
    
    // Scroll into view
    document.getElementById("results-section").scrollIntoView({ behavior: "smooth" });
}

function renderSkillMatches(containerId, matches) {
    const container = document.getElementById(containerId);
    if (!matches || !matches.length) {
        container.innerHTML = '<p class="hint">None listed.</p>';
        return;
    }
    container.innerHTML = matches.map(m => {
        const cls = m.present ? "present" : "absent";
        const icon = m.present ? "✓" : "✗";
        const evidence = m.evidence
            ? `<div class="skill-evidence">${escapeHtml(m.evidence)}</div>`
            : "";
        return `
            <div>
                <div class="skill-pill ${cls}">
                    <span>${icon} ${escapeHtml(m.skill)}</span>
                </div>
                ${evidence}
            </div>
        `;
    }).join("");
}

function renderBulletRecs(recs) {
    const container = document.getElementById("bullet-recs");
    if (!recs || !recs.length) {
        container.innerHTML = '<p class="hint">No bullet recommendations.</p>';
        return;
    }
    container.innerHTML = recs.map(r => {
        const rewriteBlock = r.rewritten_text
            ? `<div class="rewrite-text" data-rewrite="${escapeHtml(r.rewritten_text)}">${escapeHtml(r.rewritten_text)}</div>`
            : "";
        return `
            <div class="bullet-rec action-${r.action}">
                <div class="bullet-rec-header">
                    <span class="action-tag ${r.action}">${r.action}</span>
                    <span>${escapeHtml(r.experience_company)}</span>
                </div>
                <div class="original"><strong>Original:</strong> ${escapeHtml(r.original_text)}</div>
                ${rewriteBlock}
                <div class="reasoning">${escapeHtml(r.reasoning)}</div>
            </div>
        `;
    }).join("");
    
    // Attach click-to-copy to rewrite blocks
    container.querySelectorAll(".rewrite-text").forEach(el => {
        el.addEventListener("click", async () => {
            const text = el.dataset.rewrite;
            try {
                await navigator.clipboard.writeText(text);
                el.classList.add("copied");
                const original = el.textContent;
                el.textContent = "✓ Copied!";
                setTimeout(() => {
                    el.classList.remove("copied");
                    el.textContent = original;
                }, 1200);
            } catch (e) {
                console.warn("Copy failed:", e);
            }
        });
    });
}

// ────────────── Reset ──────────────

document.getElementById("reset-btn").addEventListener("click", () => {
    document.getElementById("results-section").style.display = "none";
    document.getElementById("resume-text").value = "";
    document.getElementById("resume-file").value = "";
    document.getElementById("jd-text").value = "";
    clearStatus();
    document.getElementById("input-section").scrollIntoView({ behavior: "smooth" });
});