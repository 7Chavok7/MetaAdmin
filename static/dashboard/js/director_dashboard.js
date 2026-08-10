/* static/dashboard/js/director_dashboard.js */

/**
 * Переключение видимости дочерних элементов в дереве подразделений
 */
function toggleDepartment(element) {
    const parent = element.closest('li');
    const childList = parent.querySelector('ul');
    
    if (childList) {
        if (childList.style.display === 'none') {
            childList.style.display = 'block';
            element.querySelector('i').className = 'bi bi-folder-open';
        } else {
            childList.style.display = 'none';
            element.querySelector('i').className = 'bi bi-folder';
        }
    }
}

/**
 * Инициализация дерева подразделений
 */
function initDepartmentTree() {
    // По умолчанию разворачиваем только первый уровень
    document.querySelectorAll('.department-tree > li > ul').forEach(el => {
        el.style.display = 'block';
    });
    document.querySelectorAll('.department-tree li li > ul').forEach(el => {
        el.style.display = 'none';
    });
}

/**
 * Автогенерация кода из названия (для формы подразделения)
 */
function initCodeAutogeneration() {
    const nameField = document.getElementById('name');
    const codeField = document.getElementById('code');
    
    if (!nameField || !codeField) return;
    
    nameField.addEventListener('input', function() {
        if (!codeField.value || codeField.dataset.auto === 'true') {
            const name = this.value;
            const code = name
                .toUpperCase()
                .replace(/[^А-ЯA-Z0-9]/g, '_')
                .replace(/_+/g, '_')
                .replace(/^_|_$/g, '');
            
            if (code) {
                codeField.value = code;
                codeField.dataset.auto = 'true';
            }
        }
    });
    
    codeField.addEventListener('input', function() {
        this.dataset.auto = 'false';
    });
}

/**
 * Запуск всех инициализаций при загрузке страницы
 */
document.addEventListener('DOMContentLoaded', function() {
    initDepartmentTree();
    initCodeAutogeneration();
});