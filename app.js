const birthDateInput = document.querySelector("#birthDate");
const currentDateInput = document.querySelector("#currentDate");
const ageYearsInput = document.querySelector("#ageYears");
const ageDaysInput = document.querySelector("#ageDays");
const lifespanInput = document.querySelector("#lifespan");
const lifespanNumberInput = document.querySelector("#lifespanNumber");
const lifespanValue = document.querySelector("#lifespanValue");
const lifespanHint = document.querySelector("#lifespanHint");
const updateButton = document.querySelector("#updateButton");
const todayButton = document.querySelector("#todayButton");
const ageButton = document.querySelector("#ageButton");
const copyButton = document.querySelector("#copyButton");
const jumpButton = document.querySelector("#jumpButton");
const controlsForm = document.querySelector("#controls");
const eventTitleInput = document.querySelector("#eventTitle");
const eventDateInput = document.querySelector("#eventDate");
const addEventButton = document.querySelector("#addEventButton");
const eventHeadline = document.querySelector("#eventHeadline");
const eventCount = document.querySelector("#eventCount");
const eventList = document.querySelector("#eventList");
const modeButtons = document.querySelectorAll("[data-mode]");
const ringProgress = document.querySelector("#ringProgress");
const progressPercent = document.querySelector("#progressPercent");
const greeting = document.querySelector("#greeting");
const headline = document.querySelector("#headline");
const statAge = document.querySelector("#statAge");
const statLived = document.querySelector("#statLived");
const statLeft = document.querySelector("#statLeft");
const statBirthday = document.querySelector("#statBirthday");
const ageBar = document.querySelector("#ageBar");
const livedBar = document.querySelector("#livedBar");
const leftBar = document.querySelector("#leftBar");
const birthdayBar = document.querySelector("#birthdayBar");
const statusText = document.querySelector("#status");
const calendarWrap = document.querySelector("#calendarWrap");
const canvas = document.querySelector("#calendarCanvas");
const ctx = canvas.getContext("2d");
const tooltip = document.querySelector("#tooltip");
const ambientCanvas = document.querySelector("#ambientCanvas");
const ambient = ambientCanvas.getContext("2d");
const zoomInButton = document.querySelector("#zoomInButton");
const zoomOutButton = document.querySelector("#zoomOutButton");
const resetButton = document.querySelector("#resetButton");

const dayMs = 24 * 60 * 60 * 1000;
const ringLength = 2 * Math.PI * 52;
let mode = "day";
let metrics = {};
let stats = null;
let animationFrame = 0;
let ambientFrame = 0;
let personalEvents = loadPersonalEvents();
let editingEventId = null;
let dotScale = 1;

function parseLocalDate(value) {
  const [year, month, day] = value.split("-").map(Number);
  return new Date(year, month - 1, day);
}

function toInputDate(value) {
  const year = value.getFullYear();
  const month = String(value.getMonth() + 1).padStart(2, "0");
  const day = String(value.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
}

function addYears(value, years) {
  const result = new Date(value);
  result.setFullYear(value.getFullYear() + years);
  if (result.getMonth() !== value.getMonth()) result.setDate(0);
  return result;
}

function addDays(value, days) {
  const result = new Date(value);
  result.setDate(result.getDate() + days);
  return result;
}

function daysBetween(start, end) {
  const a = Date.UTC(start.getFullYear(), start.getMonth(), start.getDate());
  const b = Date.UTC(end.getFullYear(), end.getMonth(), end.getDate());
  return Math.round((b - a) / dayMs);
}

function formatDate(value) {
  return value.toLocaleDateString(undefined, { year: "numeric", month: "long", day: "numeric" });
}

function formatShortDate(value) {
  return value.toLocaleDateString(undefined, { year: "numeric", month: "short", day: "numeric" });
}

function calculateStats() {
  const birthDate = parseLocalDate(birthDateInput.value);
  const currentDate = parseLocalDate(currentDateInput.value);
  const lifespanYears = normalizeLifespan(lifespanNumberInput.value);
  if (Number.isNaN(birthDate.getTime()) || Number.isNaN(currentDate.getTime())) {
    throw new Error("Use valid dates.");
  }
  if (currentDate < birthDate) {
    throw new Error("Calendar date must be on or after birth date.");
  }

  const birthdayThisYear = addYears(birthDate, currentDate.getFullYear() - birthDate.getFullYear());
  const hadBirthday = currentDate >= birthdayThisYear;
  const ageYears = currentDate.getFullYear() - birthDate.getFullYear() - (hadBirthday ? 0 : 1);
  const lastBirthday = addYears(birthDate, ageYears);
  const nextBirthday = addYears(birthDate, ageYears + 1);
  const deathDate = addYears(birthDate, lifespanYears);
  const daysLived = Math.max(0, daysBetween(birthDate, currentDate));
  const totalDays = Math.max(1, daysBetween(birthDate, deathDate));
  const daysRemaining = Math.max(0, daysBetween(currentDate, deathDate));

  return {
    birthDate,
    currentDate,
    lifespanYears,
    ageYears,
    ageDays: Math.max(0, daysBetween(lastBirthday, currentDate)),
    daysLived,
    totalDays,
    weeksLived: Math.floor(daysLived / 7),
    daysRemaining,
    nextBirthday,
    progress: Math.min(1, Math.max(0, daysLived / totalDays)),
  };
}

function normalizeLifespan(value) {
  const parsed = Math.round(Number(value));
  if (!Number.isFinite(parsed)) return 90;
  return Math.min(150, Math.max(1, parsed));
}

function loadPersonalEvents() {
  try {
    const saved = JSON.parse(localStorage.getItem("mementoMoriPersonalDates") || "[]");
    return Array.isArray(saved) ? saved : [];
  } catch {
    return [];
  }
}

function savePersonalEvents() {
  localStorage.setItem("mementoMoriPersonalDates", JSON.stringify(personalEvents));
}

function updateStats() {
  try {
    stats = calculateStats();
    lifespanInput.value = String(stats.lifespanYears);
    lifespanNumberInput.value = String(stats.lifespanYears);
    ageYearsInput.value = stats.ageYears;
    ageDaysInput.value = stats.ageDays;
    lifespanValue.textContent = stats.lifespanYears;
    greeting.textContent = `${timeGreeting()}, Prabin`;
    headline.textContent = "Here is your life at a glance.";
    statAge.textContent = `${stats.ageYears} years, ${stats.ageDays} days`;
    statLived.textContent = stats.daysLived.toLocaleString();
    statLeft.textContent = stats.daysRemaining.toLocaleString();
    statBirthday.textContent = formatShortDate(stats.nextBirthday);
    const percent = stats.progress * 100;
    progressPercent.textContent = `${percent.toFixed(1)}%`;
    ringProgress.style.strokeDashoffset = String(ringLength * (1 - stats.progress));
    updateStatBars();
    updateLifespanHint();
    document.body.dataset.urgency = stats.progress > 0.8 ? "high" : stats.progress > 0.55 ? "medium" : "calm";
    statusText.textContent = `Showing one square per ${mode}. Hover any square for details.`;
    renderPersonalEvents();
    drawCalendar(true);
  } catch (error) {
    statusText.textContent = error.message;
  }
}

function timeGreeting() {
  const hour = new Date().getHours();
  if (hour < 12) return "Good morning";
  if (hour < 18) return "Good afternoon";
  return "Good evening";
}

function updateStatBars() {
  const progress = Math.round(stats.progress * 100);
  const leftProgress = Math.max(4, 100 - progress);
  const birthdayDistance = Math.max(0, daysBetween(stats.currentDate, stats.nextBirthday));
  const birthdayProgress = Math.max(4, Math.min(100, Math.round(((365 - birthdayDistance) / 365) * 100)));
  ageBar.style.setProperty("--value", `${Math.max(4, progress)}%`);
  livedBar.style.setProperty("--value", `${Math.max(4, progress)}%`);
  leftBar.style.setProperty("--value", `${leftProgress}%`);
  birthdayBar.style.setProperty("--value", `${birthdayProgress}%`);
}

function updateLifespanHint() {
  const difference = stats.lifespanYears - stats.ageYears;
  if (difference < 0) {
    lifespanHint.textContent = `This target is already ${Math.abs(difference)} years behind your current age.`;
  } else if (difference === 0) {
    lifespanHint.textContent = "This target is your current age. The calendar is fully urgent.";
  } else if (difference <= 5) {
    lifespanHint.textContent = `${difference} years remain in this target. Very urgent mode.`;
  } else {
    lifespanHint.textContent = `${difference} years remain in this target lifespan.`;
  }
}

function addPersonalEvent() {
  const title = eventTitleInput.value.trim() || "Personal date";
  const dateValue = eventDateInput.value;
  if (!dateValue) {
    statusText.textContent = "Choose a target date for your personal countdown.";
    return;
  }
  if (editingEventId) {
    personalEvents = personalEvents.map((event) => {
      return event.id === editingEventId ? { ...event, title, date: dateValue } : event;
    });
    editingEventId = null;
    addEventButton.textContent = "Add Personal Date";
  } else {
    personalEvents.push({
      id: globalThis.crypto && crypto.randomUUID ? crypto.randomUUID() : String(Date.now()),
      title,
      date: dateValue,
    });
  }
  personalEvents.sort((a, b) => parseLocalDate(a.date) - parseLocalDate(b.date));
  savePersonalEvents();
  eventTitleInput.value = "";
  eventDateInput.value = "";
  renderPersonalEvents();
  statusText.textContent = `${title} saved to personal dates.`;
}

function deletePersonalEvent(id) {
  personalEvents = personalEvents.filter((event) => event.id !== id);
  savePersonalEvents();
  renderPersonalEvents();
}

function editPersonalEvent(id) {
  const event = personalEvents.find((item) => item.id === id);
  if (!event) return;
  editingEventId = id;
  eventTitleInput.value = event.title;
  eventDateInput.value = event.date;
  addEventButton.textContent = "Save Personal Date";
  eventTitleInput.focus();
}

function renderPersonalEvents() {
  if (!stats) return;
  const currentDate = stats.currentDate;
  const sorted = [...personalEvents].sort((a, b) => {
    return daysBetween(currentDate, parseLocalDate(a.date)) - daysBetween(currentDate, parseLocalDate(b.date));
  });
  eventCount.textContent = `${sorted.length} saved`;
  eventList.replaceChildren();

  if (!sorted.length) {
    eventHeadline.textContent = "No personal dates yet";
    const empty = document.createElement("article");
    empty.className = "event-card";
    empty.innerHTML = "<div><strong>Add an examination date</strong><span>Your countdown will appear here.</span><b>Ready when you are</b></div>";
    eventList.append(empty);
    return;
  }

  const nearest = sorted[0];
  const nearestDays = daysBetween(currentDate, parseLocalDate(nearest.date));
  eventHeadline.textContent = `${nearest.title}: ${formatCountdown(nearestDays)} / ${formatWeekCountdown(nearestDays)}`;

  sorted.slice(0, 6).forEach((event) => {
    const targetDate = parseLocalDate(event.date);
    const daysLeft = daysBetween(currentDate, targetDate);
    const card = document.createElement("article");
    card.className = "event-card";
    card.innerHTML = `
      <div>
        <strong></strong>
        <span></span>
        <b></b>
        <em></em>
      </div>
      <div class="event-actions">
        <button type="button" class="edit-event" aria-label="Edit ${escapeHtml(event.title)}">E</button>
        <button type="button" class="delete-event" aria-label="Remove ${escapeHtml(event.title)}">X</button>
      </div>
    `;
    card.querySelector("strong").textContent = event.title;
    card.querySelector("span").textContent = formatDate(targetDate);
    card.querySelector("b").textContent = formatCountdown(daysLeft);
    card.querySelector("em").textContent = formatWeekCountdown(daysLeft);
    card.querySelector(".edit-event").addEventListener("click", () => editPersonalEvent(event.id));
    card.querySelector(".delete-event").addEventListener("click", () => deletePersonalEvent(event.id));
    eventList.append(card);
  });
}

function formatCountdown(daysLeft) {
  if (daysLeft === 0) return "Today";
  if (daysLeft > 0) return `${daysLeft.toLocaleString()} days left`;
  return `${Math.abs(daysLeft).toLocaleString()} days ago`;
}

function formatWeekCountdown(daysLeft) {
  const absoluteDays = Math.abs(daysLeft);
  const weeks = Math.floor(absoluteDays / 7);
  const days = absoluteDays % 7;
  const weekText = weeks === 1 ? "1 week" : `${weeks.toLocaleString()} weeks`;
  const dayText = days === 1 ? "1 day" : `${days} days`;
  const direction = daysLeft < 0 ? "ago" : "left";

  if (daysLeft === 0) return "0 weeks, 0 days";
  if (weeks === 0) return `${dayText} ${direction}`;
  if (days === 0) return `${weekText} ${direction}`;
  return `${weekText}, ${dayText} ${direction}`;
}

function escapeHtml(value) {
  return value.replace(/[&<>"']/g, (char) => {
    return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#039;" }[char];
  });
}

function drawCalendar(animate = false) {
  cancelAnimationFrame(animationFrame);
  const wrapWidth = Math.max(calendarWrap.clientWidth, 720);
  const rowGap = mode === "day" ? Math.round(7 * dotScale) : Math.round(12 * dotScale);
  const cell = mode === "day" ? Math.max(3, Math.min(6, Math.floor((wrapWidth - 150) / 410))) * dotScale : Math.max(7, Math.min(11, Math.floor((wrapWidth - 130) / 68))) * dotScale;
  const gap = mode === "day" ? Math.max(2, Math.round(2 * dotScale)) : Math.max(3, Math.round(4 * dotScale));
  const columns = mode === "day" ? 366 : 52;
  const left = 42;
  const top = 26;
  const label = 34;
  const width = left + label + columns * (cell + gap) + 140;
  const height = top + stats.lifespanYears * (cell + rowGap) + 42;
  const dpr = window.devicePixelRatio || 1;

  canvas.style.width = `${width}px`;
  canvas.style.height = `${height}px`;
  canvas.width = Math.floor(width * dpr);
  canvas.height = Math.floor(height * dpr);
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);

  metrics = { left, top, label, cell, gap, rowGap, columns, width, height };
  const duration = animate ? 540 : 1;
  const start = performance.now();

  function frame(now) {
    const t = Math.min(1, (now - start) / duration);
    const reveal = 1 - Math.pow(1 - t, 3);
    paintCalendar(reveal);
    if (t < 1) animationFrame = requestAnimationFrame(frame);
  }

  animationFrame = requestAnimationFrame(frame);
}

function paintCalendar(reveal) {
  ctx.clearRect(0, 0, metrics.width, metrics.height);
  ctx.font = "700 10px Segoe UI, sans-serif";
  ctx.textAlign = "right";
  ctx.textBaseline = "middle";

  for (let year = 0; year < stats.lifespanYears; year += 1) {
    const y = metrics.top + year * (metrics.cell + metrics.rowGap);
    const rowReveal = Math.min(1, Math.max(0, reveal * stats.lifespanYears - year));
    if (rowReveal <= 0) continue;

    ctx.fillStyle = year % 10 === 0 ? "#dbe4ff" : year % 5 === 0 ? "#94a3b8" : "rgba(148, 163, 184, 0.32)";
    ctx.globalAlpha = 0.45 + rowReveal * 0.55;
    ctx.fillText(String(year).padStart(2, "0"), metrics.left, y + metrics.cell / 2);

    if (mode === "day") {
      paintDayRow(year, y, rowReveal);
    } else {
      paintWeekRow(year, y, rowReveal);
    }
  }

  ctx.globalAlpha = 1;
  const nowY = metrics.top + Math.min(stats.ageYears, stats.lifespanYears - 1) * (metrics.cell + metrics.rowGap);
  ctx.textAlign = "left";
  ctx.fillStyle = "#f59e0b";
  ctx.font = "800 10px Segoe UI, sans-serif";
  ctx.fillText("you are here", metrics.left + metrics.label + metrics.columns * (metrics.cell + metrics.gap) + 10, nowY + metrics.cell / 2);
}

function paintDayRow(year, y, rowReveal) {
  const birthday = addYears(stats.birthDate, year);
  const nextBirthday = addYears(stats.birthDate, year + 1);
  const daysInLifeYear = daysBetween(birthday, nextBirthday);
  const startIndex = daysBetween(stats.birthDate, birthday);
  const shownColumns = Math.floor(daysInLifeYear * rowReveal);

  for (let day = 0; day < shownColumns; day += 1) {
    const index = startIndex + day;
    if (index >= stats.totalDays) break;
    drawSquare(day, y, colorFor(index, stats.daysLived), index === stats.daysLived);
  }
}

function paintWeekRow(year, y, rowReveal) {
  const shownColumns = Math.floor(52 * rowReveal);
  for (let week = 0; week < shownColumns; week += 1) {
    const index = year * 52 + week;
    drawSquare(week, y, colorFor(index, stats.weeksLived), index === stats.weeksLived);
  }
}

function drawSquare(column, y, color, isNow) {
  const x = metrics.left + metrics.label + column * (metrics.cell + metrics.gap);
  ctx.globalAlpha = 1;
  ctx.fillStyle = color.fill;
  ctx.beginPath();
  ctx.arc(x + metrics.cell / 2, y + metrics.cell / 2, metrics.cell / 2, 0, Math.PI * 2);
  ctx.fill();
  if (isNow) {
    ctx.shadowColor = "#2dd4bf";
    ctx.shadowBlur = 14;
    ctx.strokeStyle = "#2dd4bf";
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.arc(x + metrics.cell / 2, y + metrics.cell / 2, metrics.cell * 1.2, 0, Math.PI * 2);
    ctx.stroke();
    ctx.shadowBlur = 0;
  }
}

function colorFor(index, currentIndex) {
  if (index < currentIndex) return { fill: "#5664ff" };
  if (index === currentIndex) return { fill: "#2dd4bf" };
  return { fill: "#32384f" };
}

function periodState(index, currentIndex) {
  if (index < currentIndex) return "Lived";
  if (index === currentIndex) return "Current";
  return "Future";
}

function inspectCalendar(event) {
  if (!stats || !metrics.width) return;
  const rect = canvas.getBoundingClientRect();
  const x = event.clientX - rect.left;
  const y = event.clientY - rect.top;
  const gridX = x - metrics.left - metrics.label;
  const gridY = y - metrics.top;
  const rowHeight = metrics.cell + metrics.rowGap;
  const columnWidth = metrics.cell + metrics.gap;
  if (gridX < 0 || gridY < 0) return hideTooltip();
  const column = Math.floor(gridX / columnWidth);
  const row = Math.floor(gridY / rowHeight);
  if (column < 0 || row < 0 || column >= metrics.columns || row >= stats.lifespanYears) return hideTooltip();
  if (gridX % columnWidth > metrics.cell || gridY % rowHeight > metrics.cell) return hideTooltip();

  let title = "";
  let body = "";
  if (mode === "day") {
    const birthday = addYears(stats.birthDate, row);
    const nextBirthday = addYears(stats.birthDate, row + 1);
    const daysInLifeYear = daysBetween(birthday, nextBirthday);
    if (column >= daysInLifeYear) return hideTooltip();
    const index = daysBetween(stats.birthDate, birthday) + column;
    const exactDate = addDays(stats.birthDate, index);
    title = `Age ${row}, day ${column + 1}`;
    body = `${periodState(index, stats.daysLived)} day - ${formatDate(exactDate)}`;
  } else {
    const index = row * 52 + column;
    title = `Age ${row}, week ${column + 1}`;
    body = `${periodState(index, stats.weeksLived)} week`;
  }

  tooltip.style.display = "block";
  tooltip.style.left = `${event.clientX}px`;
  tooltip.style.top = `${event.clientY}px`;
  tooltip.innerHTML = `<strong>${title}</strong><span>${body}</span>`;
  statusText.textContent = `${title}: ${body}`;
}

function hideTooltip() {
  tooltip.style.display = "none";
}

function setDateFromAge() {
  const birth = parseLocalDate(birthDateInput.value);
  const years = Math.max(0, Number(ageYearsInput.value || 0));
  const days = Math.max(0, Number(ageDaysInput.value || 0));
  currentDateInput.value = toInputDate(addDays(addYears(birth, years), days));
  updateStats();
}

function copySummary() {
  const summary = [
    `Born: ${formatDate(stats.birthDate)}`,
    `Age: ${stats.ageYears} years and ${stats.ageDays} days`,
    `Days lived: ${stats.daysLived.toLocaleString()}`,
    `Days left: ${stats.daysRemaining.toLocaleString()} in a ${stats.lifespanYears}-year calendar`,
    `Next birthday: ${formatDate(stats.nextBirthday)}`,
    ...personalEvents.map((event) => {
      const daysLeft = daysBetween(stats.currentDate, parseLocalDate(event.date));
      return `${event.title}: ${formatCountdown(daysLeft)} / ${formatWeekCountdown(daysLeft)} (${formatDate(parseLocalDate(event.date))})`;
    }),
  ].join("\n");
  navigator.clipboard.writeText(summary);
  statusText.textContent = "Summary copied to clipboard.";
}

function jumpToNow() {
  if (!stats || !metrics.width) return;
  const y = metrics.top + Math.min(stats.ageYears, stats.lifespanYears - 1) * (metrics.cell + metrics.rowGap);
  calendarWrap.scrollTop = Math.max(0, y - calendarWrap.clientHeight * 0.42);
  if (mode === "day") {
    const x = metrics.left + metrics.label + stats.ageDays * (metrics.cell + metrics.gap);
    calendarWrap.scrollLeft = Math.max(0, x - calendarWrap.clientWidth * 0.52);
  }
}

function adjustZoom(delta) {
  dotScale = Math.max(0.75, Math.min(1.7, dotScale + delta));
  drawCalendar(false);
}

function resizeAmbient() {
  const dpr = window.devicePixelRatio || 1;
  ambientCanvas.width = Math.floor(innerWidth * dpr);
  ambientCanvas.height = Math.floor(innerHeight * dpr);
  ambientCanvas.style.width = `${innerWidth}px`;
  ambientCanvas.style.height = `${innerHeight}px`;
  ambient.setTransform(dpr, 0, 0, dpr, 0, 0);
}

function animateAmbient(now) {
  ambient.clearRect(0, 0, innerWidth, innerHeight);
  const count = Math.max(42, Math.floor(innerWidth / 22));
  for (let i = 0; i < count; i += 1) {
    const seed = i * 97.13;
    const x = (Math.sin(seed) * 0.5 + 0.5) * innerWidth + Math.sin(now / 2400 + i) * 18;
    const y = (Math.cos(seed * 1.7) * 0.5 + 0.5) * innerHeight + Math.cos(now / 3000 + i) * 18;
    const radius = 1 + (i % 4) * 0.35;
    ambient.fillStyle = i % 3 === 0 ? "rgba(56,189,248,0.35)" : i % 3 === 1 ? "rgba(20,184,166,0.28)" : "rgba(251,113,133,0.24)";
    ambient.beginPath();
    ambient.arc(x, y, radius, 0, Math.PI * 2);
    ambient.fill();
  }
  const sweep = ambient.createLinearGradient(0, 0, innerWidth, innerHeight);
  const pulse = (Math.sin(now / 1800) + 1) / 2;
  sweep.addColorStop(0, `rgba(56,189,248,${0.02 + pulse * 0.035})`);
  sweep.addColorStop(0.5, "rgba(20,184,166,0)");
  sweep.addColorStop(1, `rgba(245,158,11,${0.018 + pulse * 0.03})`);
  ambient.fillStyle = sweep;
  ambient.fillRect(0, 0, innerWidth, innerHeight);
  ambientFrame = requestAnimationFrame(animateAmbient);
}

function init() {
  currentDateInput.value = toInputDate(new Date());
  ringProgress.style.strokeDasharray = String(ringLength);
  modeButtons.forEach((button) => {
    button.addEventListener("click", () => {
      mode = button.dataset.mode;
      modeButtons.forEach((item) => item.classList.toggle("active", item === button));
      updateStats();
    });
  });
  lifespanNumberInput.addEventListener("change", () => {
    lifespanNumberInput.value = String(normalizeLifespan(lifespanNumberInput.value));
    lifespanInput.value = lifespanNumberInput.value;
    updateStats();
  });
  updateButton.addEventListener("click", updateStats);
  controlsForm.addEventListener("submit", (event) => {
    event.preventDefault();
    updateStats();
  });
  todayButton.addEventListener("click", () => {
    currentDateInput.value = toInputDate(new Date());
    updateStats();
  });
  ageButton.addEventListener("click", setDateFromAge);
  copyButton.addEventListener("click", copySummary);
  addEventButton.addEventListener("click", addPersonalEvent);
  jumpButton.addEventListener("click", jumpToNow);
  zoomInButton.addEventListener("click", () => adjustZoom(0.15));
  zoomOutButton.addEventListener("click", () => adjustZoom(-0.15));
  resetButton.addEventListener("click", () => {
    dotScale = 1;
    drawCalendar(false);
    jumpToNow();
  });
  lifespanInput.addEventListener("input", () => {
    lifespanNumberInput.value = lifespanInput.value;
    updateStats();
  });
  calendarWrap.addEventListener("mousemove", inspectCalendar);
  calendarWrap.addEventListener("mouseleave", hideTooltip);
  window.addEventListener("resize", () => {
    resizeAmbient();
    if (stats) drawCalendar(false);
  });
  resizeAmbient();
  cancelAnimationFrame(ambientFrame);
  ambientFrame = requestAnimationFrame(animateAmbient);
  updateStats();
  setTimeout(jumpToNow, 700);
}

init();
