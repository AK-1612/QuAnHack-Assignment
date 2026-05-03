const API_BASE = 'http://localhost:8000/api/v1';

async function fetchLeads() {
    try {
        const response = await fetch(`${API_BASE}/leads/`);
        const leads = await response.json();
        renderLeads(leads);
        updateStats(leads);
    } catch (error) {
        console.error('Error fetching leads:', error);
    }
}

function renderLeads(leads) {
    const tableBody = document.getElementById('leads-table-body');
    tableBody.innerHTML = leads.map(lead => `
        <tr class="border-b border-slate-700/50 cursor-pointer hover:bg-slate-800/20" onclick="showLeadDetails(${lead.id})">
            <td class="p-4">
                <div class="font-semibold">${lead.name || 'Anonymous'}</div>
                <div class="text-xs text-slate-500">${lead.phone_number}</div>
            </td>
            <td class="p-4">${lead.destination || '-'}</td>
            <td class="p-4">${lead.duration_days ? lead.duration_days + ' days' : '-'}</td>
            <td class="p-4 text-emerald-400">${lead.budget_usd ? '$' + lead.budget_usd.toLocaleString() : '-'}</td>
            <td class="p-4">
                <span class="badge badge-${lead.status}">${lead.status}</span>
            </td>
            <td class="p-4">
                <button class="text-slate-400 hover:text-white transition">
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/></svg>
                </button>
            </td>
        </tr>
    `).join('');
}

function updateStats(leads) {
    document.getElementById('stat-total').textContent = leads.length;
    document.getElementById('stat-qualified').textContent = leads.filter(l => l.status === 'qualified').length;
    
    const budgets = leads.filter(l => l.budget_usd).map(l => l.budget_usd);
    const avgBudget = budgets.length ? budgets.reduce((a, b) => a + b) / budgets.length : 0;
    document.getElementById('stat-budget').textContent = '$' + Math.round(avgBudget).toLocaleString();
    
    document.getElementById('stat-active').textContent = leads.filter(l => l.status === 'interested').length;
}

async function showLeadDetails(leadId) {
    try {
        const response = await fetch(`${API_BASE}/leads/${leadId}`);
        const data = await response.json();
        
        const modal = document.getElementById('lead-modal');
        const left = document.getElementById('modal-left');
        const right = document.getElementById('modal-right');
        
        document.getElementById('modal-title').textContent = `Details: ${data.lead.name || data.lead.phone_number}`;
        
        left.innerHTML = `
            <div class="space-y-6">
                <div>
                    <h4 class="text-slate-400 text-sm mb-1 uppercase tracking-wider font-bold">Preferences</h4>
                    <div class="bg-slate-800 p-4 rounded-xl border border-slate-700">
                        <p><span class="text-slate-400">Destination:</span> ${data.lead.destination || 'Not set'}</p>
                        <p><span class="text-slate-400">Duration:</span> ${data.lead.duration_days || '-'} days</p>
                        <p><span class="text-slate-400">Budget:</span> $${data.lead.budget_usd || '-'}</p>
                        <p><span class="text-slate-400">Interests:</span> ${data.lead.interests || '-'}</p>
                    </div>
                </div>
                <div>
                    <h4 class="text-slate-400 text-sm mb-1 uppercase tracking-wider font-bold">Latest Itinerary</h4>
                    <div class="bg-slate-800 p-4 rounded-xl border border-slate-700 overflow-y-auto max-h-64 whitespace-pre-wrap text-sm text-slate-300">
                        ${data.itineraries.length ? data.itineraries[0].full_text : 'No itinerary generated yet.'}
                    </div>
                </div>
            </div>
        `;
        
        right.innerHTML = `
            <h4 class="text-slate-400 text-sm mb-1 uppercase tracking-wider font-bold">Chat History</h4>
            <div class="bg-slate-900 p-4 rounded-xl border border-slate-700 h-[400px] overflow-y-auto space-y-4">
                ${data.conversations.map(c => `
                    <div class="flex ${c.role === 'user' ? 'justify-end' : 'justify-start'}">
                        <div class="max-w-[80%] p-3 rounded-2xl text-sm ${c.role === 'user' ? 'bg-blue-600 text-white rounded-tr-none' : 'bg-slate-800 text-slate-200 rounded-tl-none'}">
                            ${c.content}
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
        
        modal.classList.remove('hidden');
    } catch (error) {
        console.error('Error fetching lead details:', error);
    }
}

function closeModal() {
    document.getElementById('lead-modal').classList.add('hidden');
}

// Initial fetch
fetchLeads();
// Refresh every 30 seconds
setInterval(fetchLeads, 30000);
