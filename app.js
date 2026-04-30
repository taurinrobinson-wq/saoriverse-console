const DEFAULT_API_BASE =
  window.location.protocol === "https:"
    ? ""
    : "http://localhost:8000";

let apiBase = (localStorage.getItem("emlApiBase") || DEFAULT_API_BASE).trim();

const dropZone = document.getElementById("drop-zone");
const fileInput = document.getElementById("file-input");
const selectedFilesEl = document.getElementById("selected-files");
const previewBtn = document.getElementById("preview-btn");
const processBtn = document.getElementById("process-btn");
const previewBody = document.getElementById("preview-body");
const manifestOutput = document.getElementById("manifest-output");
const statusLine = document.getElementById("status-line");
const downloadLink = document.getElementById("download-link");
const apiUrlInput = document.getElementById("api-url");
const testApiBtn = document.getElementById("test-api-btn");

let selectedFiles = [];

if (apiUrlInput) {
  apiUrlInput.value = apiBase;
}

function getApiBase() {
  const candidate = (apiUrlInput?.value || apiBase || "").trim().replace(/\/+$/, "");
  if (!candidate) {
    throw new Error("Set API Base URL first.");
  }
  apiBase = candidate;
  localStorage.setItem("emlApiBase", apiBase);
  return apiBase;
}

async function testApiConnection() {
  try {
    const base = getApiBase();
    setStatus("Testing API connection...");
    const response = await fetch(`${base}/health`, { method: "GET" });
    if (!response.ok) {
      throw new Error(`Health check failed: ${response.status}`);
    }
    setStatus(`Connected to ${base}`);
  } catch (error) {
    const hint =
      window.location.protocol === "https:" && String(apiUrlInput?.value || "").startsWith("http://")
        ? " Browser blocked HTTP API from an HTTPS page. Use an HTTPS API URL, or run UI locally on http://localhost."
        : "";
    setStatus(`${error.message}${hint}`);
  }
}

function setStatus(message) {
  statusLine.textContent = message;
}

function setSelectedFiles(files) {
  selectedFiles = files.filter((f) => f.name.toLowerCase().endsWith(".eml"));

  selectedFilesEl.innerHTML = "";
  if (selectedFiles.length === 0) {
    const li = document.createElement("li");
    li.className = "muted";
    li.textContent = "No valid .eml files selected.";
    selectedFilesEl.appendChild(li);
  } else {
    selectedFiles.forEach((file) => {
      const li = document.createElement("li");
      li.textContent = `${file.name} (${Math.round(file.size / 1024)} KB)`;
      selectedFilesEl.appendChild(li);
    });
  }

  const canRun = selectedFiles.length > 0;
  previewBtn.disabled = !canRun;
  processBtn.disabled = !canRun;

  downloadLink.classList.add("hidden");
  downloadLink.removeAttribute("href");
}

function buildFormData() {
  const formData = new FormData();
  selectedFiles.forEach((file) => {
    formData.append("files", file, file.name);
  });
  return formData;
}

async function previewRenames() {
  if (selectedFiles.length === 0) {
    setStatus("Select .eml files first.");
    return;
  }

  setStatus("Requesting preview...");
  previewBtn.disabled = true;

  try {
    const response = await fetch(`${getApiBase()}/api/eml/preview`, {
      method: "POST",
      body: buildFormData(),
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`Preview failed: ${response.status} ${errorText}`);
    }

    const data = await response.json();
    renderPreviewTable(data.files || []);
    setStatus(`Preview complete. ${data.successful ?? 0} success, ${data.failed ?? 0} failed.`);

    const clientManifest = {
      type: "preview",
      timestamp: new Date().toISOString(),
      total_files: data.total_files,
      successful: data.successful,
      failed: data.failed,
      files: data.files,
    };
    manifestOutput.textContent = JSON.stringify(clientManifest, null, 2);
  } catch (error) {
    const hint =
      window.location.protocol === "https:" && String(apiUrlInput?.value || "").startsWith("http://")
        ? " Browser blocked HTTP API from an HTTPS page. Use an HTTPS API URL, or run UI locally on http://localhost."
        : "";
    setStatus(`${error.message}${hint}`);
  } finally {
    previewBtn.disabled = selectedFiles.length === 0;
  }
}

function renderPreviewTable(rows) {
  previewBody.innerHTML = "";

  if (!rows.length) {
    const tr = document.createElement("tr");
    tr.innerHTML = '<td colspan="3" class="muted">No rows returned.</td>';
    previewBody.appendChild(tr);
    return;
  }

  rows.forEach((row) => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${escapeHtml(row.original_name || "")}</td>
      <td>${escapeHtml(row.proposed_name || row.renamed_eml || row.normalized_filename || "")}</td>
      <td>${escapeHtml(row.status || "")}</td>
    `;
    previewBody.appendChild(tr);
  });
}

async function processBatch() {
  if (selectedFiles.length === 0) {
    setStatus("Select .eml files first.");
    return;
  }

  setStatus("Processing batch...");
  processBtn.disabled = true;

  try {
    const response = await fetch(`${getApiBase()}/api/eml/process`, {
      method: "POST",
      body: buildFormData(),
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`Process failed: ${response.status} ${errorText}`);
    }

    const blob = await response.blob();
    const objectUrl = URL.createObjectURL(blob);
    const filename = getFilenameFromHeaders(response.headers) || `processed_emails_${Date.now()}.zip`;

    downloadLink.href = objectUrl;
    downloadLink.download = filename;
    downloadLink.textContent = `Download ZIP (${filename})`;
    downloadLink.classList.remove("hidden");

    const processManifest = {
      type: "process",
      timestamp: new Date().toISOString(),
      total_files_sent: selectedFiles.length,
      download_file: filename,
      message: "ZIP returned by backend. Click Download ZIP.",
    };
    manifestOutput.textContent = JSON.stringify(processManifest, null, 2);

    setStatus("Batch process complete. ZIP ready to download.");
  } catch (error) {
    const hint =
      window.location.protocol === "https:" && String(apiUrlInput?.value || "").startsWith("http://")
        ? " Browser blocked HTTP API from an HTTPS page. Use an HTTPS API URL, or run UI locally on http://localhost."
        : "";
    setStatus(`${error.message}${hint}`);
  } finally {
    processBtn.disabled = selectedFiles.length === 0;
  }
}

function getFilenameFromHeaders(headers) {
  const disposition = headers.get("content-disposition");
  if (!disposition) return null;

  const utfMatch = disposition.match(/filename\*=UTF-8''([^;]+)/i);
  if (utfMatch && utfMatch[1]) return decodeURIComponent(utfMatch[1]);

  const plainMatch = disposition.match(/filename="?([^";]+)"?/i);
  return plainMatch ? plainMatch[1] : null;
}

function escapeHtml(str) {
  return String(str)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

// Drag-and-drop + click handling

dropZone.addEventListener("click", () => fileInput.click());
dropZone.addEventListener("keydown", (e) => {
  if (e.key === "Enter" || e.key === " ") {
    e.preventDefault();
    fileInput.click();
  }
});

fileInput.addEventListener("change", (e) => {
  setSelectedFiles(Array.from(e.target.files || []));
});

["dragenter", "dragover"].forEach((evt) => {
  dropZone.addEventListener(evt, (e) => {
    e.preventDefault();
    e.stopPropagation();
    dropZone.classList.add("dragover");
  });
});

["dragleave", "drop"].forEach((evt) => {
  dropZone.addEventListener(evt, (e) => {
    e.preventDefault();
    e.stopPropagation();
    dropZone.classList.remove("dragover");
  });
});

dropZone.addEventListener("drop", (e) => {
  const files = Array.from(e.dataTransfer?.files || []);
  setSelectedFiles(files);
});

previewBtn.addEventListener("click", previewRenames);
processBtn.addEventListener("click", processBatch);
testApiBtn.addEventListener("click", testApiConnection);

if (apiUrlInput) {
  apiUrlInput.addEventListener("change", () => {
    apiBase = apiUrlInput.value.trim().replace(/\/+$/, "");
    localStorage.setItem("emlApiBase", apiBase);
  });
}

setStatus("Ready. Add .eml files to begin.");
