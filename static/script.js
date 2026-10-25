const formPanel = document.getElementById("registration");
const registrationForm = document.getElementById("registration-form");
let selectedEventId = null;

function selectEvent(id, title) {
  selectedEventId = id;
  document.getElementById("event-id").value = id;
  document.getElementById("form-title").textContent = `Register for ${title}`;
  document.getElementById("form-message").textContent = "";
  formPanel.classList.remove("hidden");
  formPanel.scrollIntoView({ behavior: "smooth", block: "start" });
}

function closeForm() {
  formPanel.classList.add("hidden");
  registrationForm.reset();
}

registrationForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const message = document.getElementById("form-message");
  const submitButton = registrationForm.querySelector('button[type="submit"]');
  submitButton.disabled = true;
  message.className = "";
  message.textContent = "Submitting…";
  try {
    const response = await fetch("/api/register", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        event_id: selectedEventId,
        name: document.getElementById("name").value,
        email: document.getElementById("email").value,
        phone: document.getElementById("phone").value
      })
    });
    const result = await response.json();
    if (!response.ok) throw new Error(result.error || "Something went wrong.");
    message.className = "message success";
    message.textContent = result.message;
    if (result.type === "registration") registrationForm.reset();
  } catch (error) {
    message.className = "message error";
    message.textContent = error.message;
  } finally {
    submitButton.disabled = false;
  }
});
