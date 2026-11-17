"use strict";

const form = document.querySelector("#filters");
const table = document.querySelector("#flights");
const tableRows = Array.from(table.rows);
const count = document.querySelector("#results-count");
const empty = document.querySelector("#empty");
const exportButton = document.querySelector("#export");
const metricButtons = Array.from(document.querySelectorAll("[data-select-program]"));

function normalize(value) {
  return value.toLowerCase().normalize("NFD").replace(/\p{Diacritic}/gu, "")
    .replace(/[^\p{Letter}\p{Number}]+/gu, " ").trim();
}

const searchIndex = new Map(tableRows.map(row => [
  row, normalize(row.textContent + " " + row.dataset.id.replaceAll("-", "")),
]));

function update() {
  const filters = new FormData(form);
  const terms = normalize(filters.get("q")).split(" ").filter(Boolean);
  const facets = ["program", "kind", "outcome"];
  const year = filters.get("year");
  const order = filters.get("sort") === "desc" ? tableRows : [...tableRows].reverse();
  let visible = 0;
  for (const row of order) {
    const matchesFacets = facets.every(key => !filters.get(key) || row.dataset[key] === filters.get(key));
    const matchesYear = !year || row.dataset.date.startsWith(year);
    const matchesTerms = terms.every(term => searchIndex.get(row).includes(term));
    row.hidden = !(matchesFacets && matchesYear && matchesTerms);
    if (!row.hidden) visible++;
  }
  if (table.firstElementChild !== order[0]) table.append(...order);
  count.textContent = visible === 1 ? "1 evento" : visible + " eventi";
  empty.hidden = visible > 0;
  exportButton.disabled = visible === 0;
  for (const button of metricButtons) {
    button.setAttribute("aria-pressed", String(button.dataset.selectProgram === filters.get("program")));
  }
}

const csvFields = [
  "data", "id", "programma", "tipo", "sito", "missione", "veicolo", "esito", "recupero", "nota",
];

function csvCell(value) {
  return '"' + value.replaceAll('"', '""') + '"';
}

function exportCsv() {
  const rows = Array.from(table.rows).filter(row => !row.hidden);
  const lines = [
    csvFields.concat("fonti"),
    ...rows.map(row => csvFields.map(field => (
      field === "data" ? row.dataset.date : row.querySelector("[data-field=" + field + "]").textContent.trim()
    )).concat(Array.from(row.querySelectorAll("details a"), link => link.href).join(" | "))),
  ];
  const csv = "\uFEFF" + lines.map(line => line.map(csvCell).join(";")).join("\r\n") + "\r\n";
  const url = URL.createObjectURL(new Blob([csv], { type: "text/csv;charset=utf-8" }));
  const link = document.createElement("a");
  link.href = url;
  link.download = "lanci-blue-origin.csv";
  document.body.append(link);
  link.click();
  link.remove();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}

form.addEventListener("submit", event => event.preventDefault());
form.addEventListener("input", update);
form.addEventListener("reset", () => queueMicrotask(update));
for (const button of metricButtons) {
  button.disabled = false;
  button.addEventListener("click", () => {
    form.elements.namedItem("program").value = button.dataset.selectProgram;
    update();
  });
}
exportButton.addEventListener("click", exportCsv);
const parameters = new URLSearchParams(location.search);
for (const name of ["program", "kind"]) {
  const filter = form.elements.namedItem(name);
  const requestedValue = parameters.get(name);
  if (Array.from(filter.options).some(option => option.value === requestedValue)) {
    filter.value = requestedValue;
  }
}
form.hidden = false;
exportButton.hidden = false;
update();
