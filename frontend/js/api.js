// API Fetch operations module

export async function checkSystemStatus() {
    try {
        const response = await fetch("/api/status");
        if (!response.ok) return null;
        return await response.json();
    } catch (error) {
        console.error("System status check failed:", error);
        return null;
    }
}



export async function fetchReminders() {
    try {
        const response = await fetch("/api/reminders");
        if (!response.ok) throw new Error("Could not fetch active queue.");
        return await response.json();
    } catch (error) {
        console.error("Failed to load reminders:", error);
        return [];
    }
}



export async function submitReminder(text) {
    const response = await fetch("/api/reminders", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text })
    });
    if (!response.ok) {
        const err = await response.json();
        throw new Error(err.detail || "Server failed to schedule task.");
    }
    return await response.json();
}

export async function deleteReminder(id) {
    try {
        const response = await fetch(`/api/reminders/${id}`, { method: "DELETE" });
        return response.ok;
    } catch (error) {
        console.error("Failed to delete reminder ID " + id + ":", error);
        return false;
    }
}
