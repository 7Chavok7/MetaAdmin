// static/dashboard/js/salary_table.js

// ===== СВОРАЧИВАНИЕ ПОДРАЗДЕЛЕНИЙ =====
function toggleParent(headerRow) {
    const isExpanded = headerRow.dataset.expanded === 'true';
    const parentIndex = headerRow.rowIndex;
    const table = headerRow.closest('table');
    const rows = table.querySelectorAll('tr');
    const toggleIcon = headerRow.querySelector('.toggle-icon i');
    
    // Ищем все строки, принадлежащие этой группе
    let found = false;
    for (let i = parentIndex + 1; i < rows.length; i++) {
        const row = rows[i];
        if (row.classList.contains('parent-header')) {
            break;
        }
        if (row.classList.contains('parent-content')) {
            if (!found) found = true;
            if (isExpanded) {
                row.classList.add('hidden');
            } else {
                row.classList.remove('hidden');
            }
        }
    }
    
    // Меняем состояние
    if (isExpanded) {
        headerRow.dataset.expanded = 'false';
        if (toggleIcon) toggleIcon.className = 'bi bi-chevron-right';
    } else {
        headerRow.dataset.expanded = 'true';
        if (toggleIcon) toggleIcon.className = 'bi bi-chevron-down';
    }
}

// ===== РАЗВЕРНУТЬ ВСЕ =====
function expandAll() {
    const headers = document.querySelectorAll('.parent-header');
    headers.forEach(header => {
        if (header.dataset.expanded === 'false') {
            toggleParent(header);
        }
    });
}

// ===== СВЕРНУТЬ ВСЕ =====
function collapseAll() {
    const headers = document.querySelectorAll('.parent-header');
    headers.forEach(header => {
        if (header.dataset.expanded === 'true') {
            toggleParent(header);
        }
    });
}

// ===== РАСЧЁТ ЗАРПЛАТЫ =====
function calculateMonth(year, month) {
    const btn = event.target.closest('.btn-calc-month');
    if (!btn) return;
    
    if (btn.classList.contains('calculated')) {
        if (!confirm('Зарплата за этот месяц уже рассчитана. Пересчитать?')) {
            return;
        }
    }
    
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner-border spinner-border-sm"></span>';
    
    const url = document.querySelector('meta[name="calculate-url"]')?.content || '/api/calculate-month/';
    
    fetch(url, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCsrfToken(),
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ year: year, month: month })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            btn.className = 'btn btn-sm btn-calc-month calculated';
            btn.innerHTML = '<i class="bi bi-check-circle"></i>';
            showNotification('✅ ' + data.message);
            setTimeout(() => location.reload(), 1500);
        } else {
            btn.className = 'btn btn-sm btn-calc-month not-calculated';
            btn.innerHTML = '<i class="bi bi-exclamation-triangle"></i>';
            showNotification('❌ Ошибка: ' + (data.error || 'Неизвестная ошибка'));
        }
    })
    .catch(error => {
        btn.className = 'btn btn-sm btn-calc-month not-calculated';
        btn.innerHTML = '<i class="bi bi-x-circle"></i>';
        showNotification('❌ Ошибка при расчёте');
        console.error(error);
    })
    .finally(() => {
        btn.disabled = false;
    });
}

function calculateAllMonths() {
    if (!confirm('Рассчитать зарплату за все месяцы текущего года?')) {
        return;
    }
    
    const year = new Date().getFullYear();
    const months = [1,2,3,4,5,6,7,8,9,10,11,12];
    let processed = 0;
    
    months.forEach(month => {
        const buttons = document.querySelectorAll('.btn-calc-month');
        const btn = buttons[month - 1];
        
        setTimeout(() => {
            calculateMonthWithDelay(year, month, btn, () => {
                processed++;
                if (processed === 12) {
                    showNotification('✅ Все месяцы рассчитаны!');
                    setTimeout(() => location.reload(), 1000);
                }
            });
        }, month * 500);
    });
}

function calculateMonthWithDelay(year, month, btn, callback) {
    if (!btn) return callback();
    
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner-border spinner-border-sm"></span>';
    
    const url = document.querySelector('meta[name="calculate-url"]')?.content || '/api/calculate-month/';
    
    fetch(url, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCsrfToken(),
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ year: year, month: month })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            btn.className = 'btn btn-sm btn-calc-month calculated';
            btn.innerHTML = '<i class="bi bi-check-circle"></i>';
        } else {
            btn.className = 'btn btn-sm btn-calc-month not-calculated';
            btn.innerHTML = '<i class="bi bi-x-circle"></i>';
        }
    })
    .catch(() => {
        btn.className = 'btn btn-sm btn-calc-month not-calculated';
        btn.innerHTML = '<i class="bi bi-x-circle"></i>';
    })
    .finally(() => {
        btn.disabled = false;
        callback();
    });
}

function getCsrfToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]')?.value || 
           document.cookie.split('; ').find(row => row.startsWith('csrftoken='))?.split('=')[1] || '';
}

function showNotification(message) {
    const existing = document.querySelector('.alert.position-fixed');
    if (existing) existing.remove();
    
    const div = document.createElement('div');
    div.className = 'alert alert-info alert-dismissible fade show position-fixed';
    div.style.cssText = `
        position: fixed;
        bottom: 20px;
        right: 20px;
        z-index: 9999;
        max-width: 400px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    `;
    div.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    document.body.appendChild(div);
    setTimeout(() => { if (div) div.remove(); }, 3000);
}