/* script.js - IOWA Pipeline Frontend Logic */

const API_BASE = 'http://localhost:8000';

// --- DOM refs ---
const fileInput      = document.getElementById('orderImage');
const dropZone       = document.getElementById('dropZone');
const dropContent    = document.getElementById('dropContent');
const previewWrap    = document.getElementById('previewWrap');
const previewImg     = document.getElementById('previewImg');
const previewLabel   = document.getElementById('previewLabel');
const clearBtn       = document.getElementById('clearBtn');
const processBtn     = document.getElementById('processBtn');
const btnText        = document.getElementById('btnText');
const loaderWrap     = document.getElementById('loaderWrap');
const loaderMsg      = document.getElementById('loaderMsg');
const resultsSection = document.getElementById('resultsSection');
const tableBody      = document.getElementById('tableBody');
const downloadBtn    = document.getElementById('downloadBtn');
const errorToast     = document.getElementById('errorToast');
const errorMsg       = document.getElementById('errorMsg');

// --- Pipeline step elements ---
const steps = [
  document.getElementById('step1'),
  document.getElementById('step2'),
  document.getElementById('step3'),
  document.getElementById('step4'),
];

// --- File Selection & Preview ---
fileInput.addEventListener('change', () => {
  if (fileInput.files[0]) showPreview(fileInput.files[0]);
});

clearBtn.addEventListener('click', (e) => {
  e.stopPropagation();
  clearSelection();
});

function showPreview(file) {
  const reader = new FileReader();
  reader.onload = (ev) => {
    previewImg.src = ev.target.result;
    previewLabel.textContent = `${file.name} (${formatBytes(file.size)})`;
    dropContent.classList.add('hidden');
    previewWrap.classList.remove('hidden');
    processBtn.disabled = false;
    hideError();
  };
  reader.readAsDataURL(file);
}

function clearSelection() {
  fileInput.value = '';
  previewImg.src = '';
  previewWrap.classList.add('hidden');
  dropContent.classList.remove('hidden');
  processBtn.disabled = true;
  resultsSection.classList.add('hidden');
  resetSteps();
}

// --- Drag & Drop ---
['dragenter', 'dragover'].forEach(evt =>
  dropZone.addEventListener(evt, (e) => {
    e.preventDefault();
    dropZone.classList.add('drag-over');
  })
);

['dragleave', 'dragend', 'drop'].forEach(evt =>
  dropZone.addEventListener(evt, (e) => {
    e.preventDefault();
    dropZone.classList.remove('drag-over');
  })
);

dropZone.addEventListener('drop', (e) => {
  const file = e.dataTransfer.files[0];
  if (file && file.type.startsWith('image/')) {
    // Sync with the file input for FormData
    const dt = new DataTransfer();
    dt.items.add(file);
    fileInput.files = dt.files;
    showPreview(file);
  } else {
    showError('Please drop a valid image file (JPEG, PNG, WEBP, or BMP).');
  }
});

// --- Pipeline Step Helpers ---
function setStep(index) {
  steps.forEach((s, i) => {
    s.classList.remove('active', 'done');
    if (i < index)  s.classList.add('done');
    if (i === index) s.classList.add('active');
  });
}

function resetSteps() {
  steps.forEach(s => s.classList.remove('active', 'done'));
}

function completeSteps() {
  steps.forEach(s => { s.classList.remove('active'); s.classList.add('done'); });
}

// --- Main Process Function ---
async function processOrder() {
  if (!fileInput.files[0]) return;

  // UI: start loading
  processBtn.disabled = true;
  loaderWrap.classList.remove('hidden');
  resultsSection.classList.add('hidden');
  hideError();

  const loaderMessages = [
    { step: 0, msg: 'Uploading image to server...' },
    { step: 1, msg: 'Preprocessing with OpenCV...' },
    { step: 2, msg: 'Extracting data with Gemini AI...' },
    { step: 3, msg: 'Generating ERP CSV with Pandas...' },
  ];

  // Animate through step messages while the real request runs
  let msgIndex = 0;
  setStep(0);
  loaderMsg.textContent = loaderMessages[0].msg;

  const stepInterval = setInterval(() => {
    msgIndex++;
    if (msgIndex < loaderMessages.length) {
      const { step, msg } = loaderMessages[msgIndex];
      setStep(step);
      loaderMsg.textContent = msg;
    }
  }, 1800);

  try {
    const formData = new FormData();
    formData.append('file', fileInput.files[0]);

    const response = await fetch(`${API_BASE}/api/upload`, {
      method: 'POST',
      body: formData,
    });

    clearInterval(stepInterval);

    if (!response.ok) {
      const errData = await response.json().catch(() => ({}));
      throw new Error(errData.detail || `Server error (${response.status})`);
    }

    const result = await response.json();
    completeSteps();
    renderResults(result);

  } catch (error) {
    clearInterval(stepInterval);
    resetSteps();
    showError(error.message);
  } finally {
    loaderWrap.classList.add('hidden');
    processBtn.disabled = false;
  }
}

// --- Render Results ---
function renderResults(result) {
  const data = result.data;

  // Meta badges
  document.getElementById('badgeCustomer').textContent = `Customer: ${data.customer_name}`;
  document.getElementById('badgeDate').textContent     = `Date: ${data.order_date}`;

  // Table rows
  tableBody.innerHTML = '';
  (data.items || []).forEach((item, i) => {
    const urgencyClass = urgencyToClass(item.urgency);
    const row = document.createElement('tr');
    row.innerHTML = `
      <td>${i + 1}</td>
      <td><strong>${escHtml(item.part_number)}</strong></td>
      <td>${item.quantity}</td>
      <td><span class="urgency-badge ${urgencyClass}">${urgencyDot(item.urgency)} ${escHtml(item.urgency)}</span></td>
    `;
    tableBody.appendChild(row);
  });

  // Download link
  downloadBtn.href = `${API_BASE}${result.download_url}`;

  // Show results
  resultsSection.classList.remove('hidden');
  resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// --- Utility ---
function urgencyToClass(urgency = '') {
  const u = urgency.toLowerCase();
  if (u === 'high')   return 'urgency-high';
  if (u === 'low')    return 'urgency-low';
  return 'urgency-medium';
}

function urgencyDot(urgency = '') {
  const u = urgency.toLowerCase();
  if (u === 'high')   return '[!]';
  if (u === 'low')    return '[ ]';
  return '[-]';
}

function escHtml(str = '') {
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

function formatBytes(bytes) {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function showError(msg) {
  errorMsg.textContent = msg;
  errorToast.classList.remove('hidden');
}

function hideError() {
  errorToast.classList.add('hidden');
}