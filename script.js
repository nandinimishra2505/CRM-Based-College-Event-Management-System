let events = JSON.parse(localStorage.getItem("events")) || [
  { id: 1, name: "Hackathon 2026", type: "Tech" },
  { id: 2, name: "Cultural Fest", type: "Cultural" },
  { id: 3, name: "Sports Meet", type: "Sports" }
];

let registrations = JSON.parse(localStorage.getItem("registrations")) || [];
let leads = JSON.parse(localStorage.getItem("leads")) || [];

/* ---------------------------
   ADMIN AUTH CHECK
----------------------------*/
if (
  window.location.pathname.includes("admin.html") &&
  sessionStorage.getItem("adminLoggedIn") !== "true"
) {
  window.location.href = "login.html";
}

/* ---------------------------
   UNIQUE USER KEY
----------------------------*/
function getUserKey(name, eventId) {
  return name.trim().toLowerCase() + "_" + eventId;
}

/* ---------------------------
   PHONE VALIDATION
----------------------------*/
function isValidPhone(phone) {
  return /^[6-9]\d{9}$/.test(phone);
}

/* ---------------------------
   SAVE DATA
----------------------------*/
function saveData() {
  localStorage.setItem("events", JSON.stringify(events));
  localStorage.setItem("registrations", JSON.stringify(registrations));
  localStorage.setItem("leads", JSON.stringify(leads));
}

/* ---------------------------
   DISPLAY EVENTS
----------------------------*/
function displayEvents() {
  let list = document.getElementById("eventList");

  if (!list) return;

  list.innerHTML = "";

  events.forEach(event => {
    list.innerHTML += `
      <div class="event">
        <h3>${event.name}</h3>
        <p>Category: ${event.type}</p>
        <button onclick="register(${event.id})">Register</button>
      </div>
    `;
  });
}

/* ---------------------------
   STUDENT REGISTRATION FLOW
----------------------------*/
function register(eventId) {
  let name = prompt("Enter your name:");
  let phone = prompt("Enter your 10-digit phone number (optional):");

  if (!name) {
    alert("Name is required");
    return;
  }

  phone = phone ? phone.replace(/\D/g, "") : "";
  let userKey = getUserKey(name, eventId);

  /* LEAD CASE */
  if (!phone || !isValidPhone(phone)) {
    alert("Saved as Lead (Incomplete / Invalid)");

    let existingLead = leads.find(l => l.key === userKey);

    if (!existingLead) {
      leads.push({
        key: userKey,
        name,
        phone: phone || "Not Provided",
        eventId,
        status: "Lead"
      });
    }

    saveData();
    updateCRM();
    return;
  }

  /* DUPLICATE REGISTRATION CHECK */
  let alreadyRegistered = registrations.find(r => r.key === userKey);

  if (alreadyRegistered) {
    alert("Already registered for this event!");
    return;
  }

  /* LEAD CONVERSION */
  let leadIndex = leads.findIndex(l => l.key === userKey);

  if (leadIndex !== -1) {
    leads[leadIndex].status = "Converted";
  }

  /* REGISTER USER */
  registrations.push({
    key: userKey,
    student: name,
    phone,
    eventId
  });

  saveData();
  notify(name, eventId);
  updateCRM();
}

/* ---------------------------
   AUTOMATED NOTIFICATION
----------------------------*/
function notify(name, eventId) {
  let event = events.find(e => e.id === eventId);

  alert(`Registered for "${event.name}"`);

  console.log(`
EMAIL SIMULATION
----------------
To: ${name}
Event: ${event.name}
Status: Confirmed
  `);
}

/* ---------------------------
   ADMIN LOGIN
----------------------------*/
function adminLogin() {
  let username = document.getElementById("username")?.value;
  let password = document.getElementById("password")?.value;

  if (username === "admin" && password === "1234") {
    sessionStorage.setItem("adminLoggedIn", "true");
    window.location.href = "admin.html";
  } else {
    alert("Invalid credentials");
  }
}

/* ---------------------------
   LOGOUT
----------------------------*/
function logout() {
  sessionStorage.removeItem("adminLoggedIn");
  window.location.href = "login.html";
}

/* ---------------------------
   CRM DASHBOARD
----------------------------*/
function updateCRM() {
  let crm = document.getElementById("crmData");
  let stats = document.getElementById("stats");

  if (!crm || !stats) return;

  crm.innerHTML = "";

  stats.innerHTML = `
    Total Events: ${events.length} <br>
    Leads: ${leads.length} <br>
    Registrations: ${registrations.length}
  `;

  crm.innerHTML += `<h3>🔥 Leads</h3>`;

  leads.forEach(l => {
    let event = events.find(e => e.id === l.eventId);

    crm.innerHTML += `
      <p>
        ${l.name} (${l.phone}) → ${event.name}
        <strong>[${l.status}]</strong>
      </p>
    `;
  });

  crm.innerHTML += `<h3>✅ Registrations</h3>`;

  registrations.forEach(r => {
    let event = events.find(e => e.id === r.eventId);

    crm.innerHTML += `
      <p>
        ${r.student} (${r.phone}) → ${event.name}
      </p>
    `;
  });
}

/* ---------------------------
   INIT
----------------------------*/
displayEvents();
updateCRM();
