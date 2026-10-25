function escapeHTML(value) {
  return String(value ?? "").replace(/[&<>"']/g, char => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"
  }[char]));
}

async function loadDashboard() {
  const message = document.getElementById("dashboard-message");
  try {
    const response = await fetch("/api/dashboard");
    if (response.status === 401) {
      window.location.href = "/login";
      return;
    }
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || "Could not load dashboard.");
    document.getElementById("count-events").textContent = data.counts.events;
    document.getElementById("count-leads").textContent = data.counts.leads;
    document.getElementById("count-registrations").textContent = data.counts.registrations;
    document.getElementById("count-rate").textContent = `${data.counts.conversion_rate}%`;

    const leadsBody = document.getElementById("leads-body");
    leadsBody.innerHTML = data.leads.length ? data.leads.map(lead => `
      <tr>
        <td>${escapeHTML(lead.name)}</td><td>${escapeHTML(lead.event_title)}</td>
        <td>${escapeHTML(lead.phone || "—")}</td><td>${escapeHTML(lead.email || "—")}</td>
        <td><span class="status status-${lead.status.toLowerCase()}">${escapeHTML(lead.status)}</span></td>
        <td><select aria-label="Update status for ${escapeHTML(lead.name)}" onchange="updateLeadStatus(${lead.id}, this.value)">
          ${["New","Contacted","Converted"].map(status => `<option ${lead.status === status ? "selected" : ""}>${status}</option>`).join("")}
        </select></td>
      </tr>`).join("") : '<tr><td colspan="6">No leads yet.</td></tr>';

    const registrationsBody = document.getElementById("registrations-body");
    registrationsBody.innerHTML = data.registrations.length ? data.registrations.map(item => `
      <tr><td>${escapeHTML(item.name)}</td><td>${escapeHTML(item.event_title)}</td>
      <td>${escapeHTML(item.phone)}</td><td>${escapeHTML(item.email)}</td>
      <td>${escapeHTML(item.created_at)}</td></tr>`).join("") : '<tr><td colspan="5">No registrations yet.</td></tr>';
    message.textContent = "";
  } catch (error) {
    message.className = "message error";
    message.textContent = error.message;
  }
}

async function updateLeadStatus(id, status) {
  const message = document.getElementById("dashboard-message");
  try {
    const response = await fetch(`/api/leads/${id}/status`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ status })
    });
    const result = await response.json();
    if (!response.ok) throw new Error(result.error || "Could not update lead.");
    message.className = "message success";
    message.textContent = "Lead status updated.";
    await loadDashboard();
  } catch (error) {
    message.className = "message error";
    message.textContent = error.message;
  }
}
loadDashboard();
