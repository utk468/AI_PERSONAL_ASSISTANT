// UI Layout Renderers & Component Injectors Module
import { escapeHTML } from './utils.js';

export function initClock(element) {
    if (!element) return;
    setInterval(() => {
        const now = new Date();
        element.textContent = now.toLocaleTimeString();
    }, 1000);
}



export async function loadComponents() {
    document.getElementById("header-container").innerHTML = await (await fetch("/components/header.html")).text();
    document.getElementById("left-panel-container").innerHTML = await (await fetch("/components/left_panel.html")).text();
    document.getElementById("right-panel-container").innerHTML = await (await fetch("/components/right_panel.html")).text();
    lucide.createIcons();
}

export function updateSystemStatusUI(status) {
    const dbDot = document.getElementById("db-dot");
    const dbVal = document.getElementById("db-val");
    const llmDot = document.getElementById("llm-dot");
    const llmVal = document.getElementById("llm-val");

    if (!dbDot || !status) return;

    // Database Active dot & message
    if (status.db_backend_active === "mongodb") {
        dbDot.className = "status-dot dot-green";
        dbVal.textContent = "MongoDB (Active)";
    } else {
        dbDot.className = "status-dot dot-yellow";
        dbVal.textContent = "Local Fallback JSON";
    }

    // Engine Active dot & message
    if (status.groq_api_configured) {
        llmDot.className = "status-dot dot-green";
        llmVal.textContent = "Groq AI (Fastest)";
    } else {
        llmDot.className = "status-dot dot-yellow";
        llmVal.textContent = "Offline Parsing Engine";
    }
}

export function showToastAlert(data, isError = false) {
    const container = document.getElementById("toast-container");
    if (!container) return;

    const toast = document.createElement("div");
    toast.className = `toast toast-${data.priority || 'medium'}`;

    const timestampStr = new Date().toLocaleTimeString();
    let icon = isError ? "alert-triangle" : "bell-ring";
    let titleText = isError ? "Deployment Error" : "Task Reminder Alert";
    let subtitleText = isError ? "Failed to schedule task" : `Triggered: "${escapeHTML(data.original_text)}"`;

    if (data.priority === "high") icon = "zap";

    toast.innerHTML = `
        <div class="toast-header">
            <div class="toast-title">
                <i data-lucide="${icon}"></i>
                <span>${titleText}</span>
            </div>
            <span class="toast-time">${timestampStr}</span>
        </div>
        <div class="toast-body">
            <strong>${escapeHTML(data.task)}</strong>
        </div>
        <div class="toast-footer">
            <span>${subtitleText}</span>
        </div>
    `;

    container.appendChild(toast);
    lucide.createIcons();

    // Fade and delete toast
    setTimeout(() => {
        toast.classList.add("hide");
        setTimeout(() => toast.remove(), 300);
    }, 6000);
}

export function renderExtractionResult(reminder, systemStatus) {
    const extractionCard = document.getElementById("extraction-card");
    if (!extractionCard) return;

    extractionCard.classList.remove("hidden");
    document.getElementById("ext-task").textContent = reminder.task;
    document.getElementById("ext-recurring").textContent = reminder.is_recurring
        ? `Yes (${reminder.recurrence_pattern || 'recurring'})`
        : "No (One-time)";

    const extPriority = document.getElementById("ext-priority");
    extPriority.textContent = reminder.priority;
    extPriority.className = `badge badge-${reminder.priority}`;

    const date = new Date(reminder.next_run_time);
    document.getElementById("ext-time").textContent = date.toLocaleString();

    // Render LLM brand details on badge
    const parserEngineBadge = document.getElementById("parser-engine-badge");
    if (systemStatus && systemStatus.groq_api_configured) {
        parserEngineBadge.textContent = "Groq LLaMA-3";
        parserEngineBadge.className = "badge badge-cyan";
    } else {
        parserEngineBadge.textContent = "Local Parser";
        parserEngineBadge.className = "badge badge-medium";
    }
}

export function renderQueue(reminders, onDeleteClickCallback) {
    const container = document.getElementById("queue-container");
    const emptyState = document.getElementById("queue-empty");
    const countDisplay = document.getElementById("queue-count");

    if (!container) return;

    // Remove existing items
    const items = container.querySelectorAll(".queue-item");
    items.forEach(el => el.remove());

    if (reminders.length === 0) {
        emptyState.classList.remove("hidden");
        countDisplay.textContent = "0 Reminders";
        return;
    }

    emptyState.classList.add("hidden");
    countDisplay.textContent = `${reminders.length} Active Reminders`;

    reminders.forEach(reminder => {
        const item = document.createElement("div");
        item.className = `queue-item ${reminder.status === 'completed' ? 'completed-item' : ''}`;
        item.setAttribute("data-id", reminder.id);

        let prioClass = `badge-${reminder.priority}`;
        const runDate = new Date(reminder.next_run_time);
        const timeFormatted = runDate.toLocaleString();

        let relativeCountdown = "";
        if (reminder.status === "active") {
            const diffMs = runDate - new Date();
            if (diffMs > 0) {
                const diffMins = Math.ceil(diffMs / 60000);
                if (diffMins < 60) {
                    relativeCountdown = `(in ${diffMins} min${diffMins > 1 ? 's' : ''})`;
                } else {
                    const diffHrs = Math.floor(diffMins / 60);
                    const remainingMins = diffMins % 60;
                    relativeCountdown = `(in ${diffHrs}h ${remainingMins}m)`;
                }
            } else {
                relativeCountdown = "(triggering)";
            }
        }

        item.innerHTML = `
            <div class="queue-item-left">
                <div class="queue-item-title">${escapeHTML(reminder.task)}</div>
                <div class="queue-item-meta">
                    <span class="badge ${prioClass}">${reminder.priority}</span>
                    <span class="badge ${reminder.status === 'active' ? 'badge-active' : 'badge-completed'}">${reminder.status}</span>
                    
                    <div class="meta-pill">
                        <i data-lucide="${reminder.is_recurring ? 'repeat' : 'clock'}"></i>
                        <span>${reminder.is_recurring ? (reminder.recurrence_pattern || 'recurring') : 'one-time'}</span>
                    </div>
                    
                    <div class="meta-pill">
                        <i data-lucide="calendar"></i>
                        <span class="cyan-text">${timeFormatted} ${relativeCountdown}</span>
                    </div>
                </div>
            </div>
            <div class="queue-item-right">
                <button class="btn-delete" title="Delete reminder">
                    <i data-lucide="trash-2"></i>
                </button>
            </div>
        `;

        container.appendChild(item);

        // Bind delete trigger
        item.querySelector(".btn-delete").addEventListener("click", async () => {
            if (onDeleteClickCallback) {
                const success = await onDeleteClickCallback(reminder.id);
                if (success) {
                    item.style.opacity = "0";
                    item.style.transform = "translateX(50px)";
                    setTimeout(() => item.remove(), 300);
                }
            }
        });
    });

    lucide.createIcons();
}
