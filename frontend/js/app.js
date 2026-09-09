// Main Controller & Application Orchestrator Module
import { loadComponents, initClock, renderExtractionResult, showToastAlert, renderQueue, updateSystemStatusUI } from './ui.js';
import { checkSystemStatus, fetchReminders, submitReminder, deleteReminder } from './api.js';
import { playChimeAlert } from './audio.js';

document.addEventListener("DOMContentLoaded", async () => {
    // 1. Fetch, compile, and inject HTML subcomponent views
    await loadComponents();

    // 2. Initialize clock display and status indicators
    const clockElement = document.getElementById("current-time-display");
    initClock(clockElement);
    
    // Load initial data
    await refreshSystemStatus();
    await refreshQueue();

    // 3. Select newly rendered template elements
    const form = document.getElementById("reminder-form");
    const input = document.getElementById("command-input");
    const clearBtn = document.getElementById("clear-btn");
    const scheduleBtn = document.getElementById("schedule-btn");
    const suggestButtons = document.querySelectorAll(".suggest-btn");

    // Form submission processing
    form.addEventListener("submit", async (e) => {
        e.preventDefault();
        const text = input.value.trim();
        if (!text) return;

        // Button Loading state
        scheduleBtn.disabled = true;
        scheduleBtn.innerHTML = `<i data-lucide="loader" class="animate-spin"></i> Deploying...`;
        lucide.createIcons();

        try {
            const reminder = await submitReminder(text);
            const status = await checkSystemStatus();
            
            // Output AI Intent Analysis
            renderExtractionResult(reminder, status);
            
            input.value = "";
            await refreshQueue();
            updateSystemStatusUI(status);
        } catch (error) {
            console.error("Scheduler deployment error:", error);
            showToastAlert({ task: `Error: ${error.message}`, priority: "high", original_text: text }, true);
        } finally {
            scheduleBtn.disabled = false;
            scheduleBtn.innerHTML = `<i data-lucide="sparkles"></i> Deploy Scheduler`;
            lucide.createIcons();
        }
    });

    // Clear input field
    clearBtn.addEventListener("click", () => {
        input.value = "";
        input.focus();
    });

    // Suggestions pre-fills
    suggestButtons.forEach(btn => {
        btn.addEventListener("click", () => {
            const text = btn.getAttribute("data-text");
            input.value = text;
            input.focus();
            input.classList.add("glowing-focus");
            setTimeout(() => input.classList.remove("glowing-focus"), 600);
        });
    });

    // 4. Establish persistent SSE Notification Stream
    establishSSEStream();

    // HELPER FUNCTIONS FOR GLUING VIEWS & NETWORKING

    async function refreshSystemStatus() {
        const status = await checkSystemStatus();
        updateSystemStatusUI(status);
    }

    async function refreshQueue() {
        const reminders = await fetchReminders();
        // Pass queue payload and delete trigger callback to UI renderer
        renderQueue(reminders, async (id) => {
            const success = await deleteReminder(id);
            if (success) {
                // Briefly delay reload to let slide-out transition finish
                setTimeout(refreshQueue, 200);
            }
            return success;
        });
    }

    function establishSSEStream() {
        console.log("Connecting real-time SSE trigger feed...");
        const source = new EventSource("/api/stream");

        source.addEventListener("reminder_trigger", async (e) => {
            console.log("Real-time trigger SSE received:", e.data);
            const reminder = JSON.parse(e.data);
            
            // Play beautiful synthetic harmonized chime alert
            playChimeAlert();
            
            // Show toast notification banner
            showToastAlert(reminder);
            
            // Refresh Active reminders list
            await refreshQueue();
        });

        source.onerror = () => {
            source.close();
            console.warn("SSE disconnected. Retrying connection in 5 seconds...");
            setTimeout(establishSSEStream, 5000);
        };
    }
});
