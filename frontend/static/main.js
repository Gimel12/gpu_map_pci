let motherboards = {};

async function fetchMotherboards() {
    const apiRes = await fetch('/get_all_motherboards');
    motherboards = await apiRes.json();
    return motherboards;
}

function renderSlots(board, detectedMapping = null) {
    const slotGrid = document.getElementById('slot-grid');
    slotGrid.innerHTML = '';
    if (!board || !motherboards[board]) return;
    const boardData = motherboards[board];
    const slotCount = boardData.slot_count || Object.keys(boardData.slots || {}).length;
    const slots = boardData.slots || {};
    // Render all slots, even if not mapped, up to slotCount
    for (let i = 1; i <= slotCount; i++) {
        const slotKey = i.toString();
        const m = slots[slotKey];
        let extra = '';
        if (detectedMapping && detectedMapping[slotKey]) {
            const d = detectedMapping[slotKey];
            let nameDisplay = d.name ? `<br><b>Name:</b> ${d.name}` : '';
            extra = `<div class='detected-gpu'><b>Detected:</b> GPU ${d.gpu_index}${nameDisplay}<br>UUID: ${d.uuid}</div>`;
        } else if (detectedMapping && detectedMapping[slotKey] === null) {
            extra = `<div class='no-gpu'><b>No GPU detected</b></div>`;
        }
        let busId = m ? m.bus_id : '<i>Unmapped</i>';
        // Remove configured UUID display
        const div = document.createElement('div');
        div.className = 'slot-card';
        div.innerHTML = `<div class='slot-label'>Slot ${slotKey}</div><div class='gpu-id'><b>Bus ID:</b> ${busId}</div>${extra}`;
        slotGrid.appendChild(div);
    }
}

function populateMotherboardDropdown() {
    const select = document.getElementById('motherboard-select');
    select.innerHTML = '';
    for (const board in motherboards) {
        const opt = document.createElement('option');
        opt.value = board;
        opt.textContent = board;
        select.appendChild(opt);
    }
}

document.addEventListener('DOMContentLoaded', async function() {
    await fetchMotherboards();
    populateMotherboardDropdown();
    const select = document.getElementById('motherboard-select');
    select.onchange = function() {
        renderSlots(this.value);
    };
    if (select.value) renderSlots(select.value);

    document.getElementById('detect-btn').onclick = async function(e) {
        e.preventDefault();
        const board = select.value;
        if (!board) return;
        const res = await fetch(`/detect_gpus/${encodeURIComponent(board)}`);
        const detected = await res.json();
        renderSlots(board, detected);
    };
});
