/** Rendert die Demo ausschließlich über sichere DOM-Operationen. */

const byId = (id) => document.getElementById(id);

function replaceWithText(node, className, text) {
    node.replaceChildren();
    const child = document.createElement("div");
    child.className = className;
    child.textContent = text;
    node.append(child);
}

function addStep(flow, text, variant = "") {
    const node = document.createElement("div");
    node.className = `flow-step ${variant}`.trim();
    node.textContent = `↓ ${text}`;
    flow.append(node);
}

function formatTokens(value) {
    return value === null || value === undefined ? "nicht gemeldet" : value.toLocaleString("de-DE");
}

function renderStep(flow, step) {
    switch (step.type) {
        case "catalog_loaded":
            addStep(flow, `${step.tool_count} Tools per MCP geladen`);
            break;
        case "schemas_sent":
            addStep(flow, `${step.tool_count} Schemas an das LLM gesendet (${step.phase})`);
            break;
        case "candidates_selected":
            addStep(flow, `Suche „${step.search_query}“: ${step.candidate_names.join(", ") || "kein Treffer"}`, "candidates");
            break;
        case "phase_reset":
            addStep(flow, "Neuer Dialog für die Ausführungsphase; der Suchdialog wird nicht fortgeführt");
            break;
        case "tool_called":
            addStep(flow, `Tool-Aufruf ${step.tool_name} ${JSON.stringify(step.tool_arguments)}`, "tool-call");
            break;
        case "selection_failed":
            addStep(flow, "Modell hat die verpflichtende Suche nicht ausgeführt", "error");
            break;
        case "no_candidates":
            addStep(flow, "Ausführung endet ohne Kandidaten", "error");
            break;
        case "answer_generated":
            addStep(flow, "Antwort erzeugt");
            break;
        default:
            addStep(flow, "Unbekannter API-Schritt", "error");
    }
}

function renderResult(prefix, data) {
    byId(`${prefix}-available`).textContent = data.available_tool_count;
    byId(`${prefix}-initial`).textContent = data.initial_visible_tool_count;
    byId(`${prefix}-candidates`).textContent = data.selected_candidate_count;
    byId(`${prefix}-schema`).textContent = formatTokens(data.metrics.schema_tokens_sent);
    byId(`${prefix}-endpoint`).textContent = `${formatTokens(data.metrics.endpoint_input_tokens)} / ${formatTokens(data.metrics.endpoint_output_tokens)}`;
    byId(`${prefix}-calls`).textContent = data.metrics.llm_calls;

    const flow = byId(`${prefix}-flow`);
    flow.replaceChildren();
    data.steps.forEach((step) => renderStep(flow, step));

    const answer = byId(`${prefix}-answer`);
    answer.hidden = false;
    replaceWithText(answer, "answer-content", data.answer || "Keine Textantwort erhalten.");
}

function addBar(container, label, value, maximum, variant) {
    const row = document.createElement("div");
    row.className = "bar-row";
    const labelNode = document.createElement("div");
    labelNode.className = "bar-label";
    labelNode.textContent = label;
    const track = document.createElement("div");
    track.className = "bar-track";
    const fill = document.createElement("div");
    fill.className = `bar-fill ${variant}`;
    fill.style.width = `${(value / maximum) * 100}%`;
    track.append(fill);
    const number = document.createElement("div");
    number.className = "bar-value";
    number.textContent = value.toLocaleString("de-DE");
    row.append(labelNode, track, number);
    container.append(row);
}

function renderChart(normal, progressiv) {
    const normalValue = normal.metrics.schema_tokens_sent;
    const progressiveValue = progressiv.metrics.schema_tokens_sent;
    const maximum = Math.max(normalValue, progressiveValue, 1);
    const container = byId("chart-container");
    container.replaceChildren();
    addBar(container, "Vollständig", normalValue, maximum, "normal");
    addBar(container, "Progressiv", progressiveValue, maximum, "progressive");
    const difference = normalValue
        ? ((progressiveValue - normalValue) / normalValue) * 100
        : 0;
    byId("comparison-info").textContent = `Differenz dieses einzelnen Laufs: ${difference.toLocaleString("de-DE", { maximumFractionDigits: 1 })} %. Kein Benchmark.`;
}

// Zeitbudget für einen kompletten Vergleichslauf. Der echte Wert kommt beim
// Laden aus FRONTEND_REQUEST_TIMEOUT der Root-.env; dieser Startwert greift
// nur, solange /api/config noch nicht geantwortet hat oder nicht erreichbar ist.
let requestTimeoutMs = 300000;

async function loadConfig() {
    try {
        const response = await fetch("/api/config");
        if (!response.ok) return;
        const payload = await response.json();
        if (Number.isFinite(payload.request_timeout_ms) && payload.request_timeout_ms > 0) {
            requestTimeoutMs = payload.request_timeout_ms;
        }
    } catch (error) {
        // Startwert oben bleibt bestehen.
    }
}

async function runDemo() {
    const message = byId("prompt-input").value.trim();
    if (!message) return;
    const button = byId("run-btn");
    button.disabled = true;
    button.textContent = "Läuft …";
    replaceWithText(byId("normal-flow"), "placeholder", "Vollständiger Modus läuft …");
    replaceWithText(byId("progressiv-flow"), "placeholder", "Progressiver Modus wartet …");

    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), requestTimeoutMs);

    try {
        const response = await fetch("/api/demo", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message }),
            signal: controller.signal,
        });
        clearTimeout(timeoutId);
        const payload = await response.json();
        if (!response.ok) throw new Error(payload.error || `HTTP ${response.status}`);
        renderResult("normal", payload.normal);
        renderResult("progressiv", payload.progressiv);
        renderChart(payload.normal, payload.progressiv);
    } catch (error) {
        clearTimeout(timeoutId);
        const message = error.name === "AbortError"
            ? `Zeitüberschreitung nach ${requestTimeoutMs / 1000} s.`
            : error.message;
        replaceWithText(byId("normal-flow"), "placeholder error", `Fehler: ${message}`);
        replaceWithText(byId("progressiv-flow"), "placeholder error", `Fehler: ${message}`);
    } finally {
        button.disabled = false;
        button.textContent = "Vergleichen";
    }
}

document.addEventListener("DOMContentLoaded", () => {
    loadConfig();
    byId("run-btn").addEventListener("click", runDemo);
    byId("prompt-input").addEventListener("keydown", (event) => {
        if (event.key === "Enter") runDemo();
    });
});
