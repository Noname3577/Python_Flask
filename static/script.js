// ฟังก์ชันโหลดข้อมูลผู้ใช้
async function loadUsers() {
    try {
        const response = await fetch('/api/users');
        const data = await response.json();
        
        if (data.status === 'success' && data.data.length > 0) {
            const tbody = document.querySelector('tbody');
            tbody.innerHTML = '';
            
            data.data.forEach(user => {
                const row = document.createElement('tr');
                row.setAttribute('data-id', user.id);
                row.innerHTML = `
                    <td>${user.id}</td>
                    <td class="user-name">${user.name}</td>
                    <td class="user-email">${user.email}</td>
                    <td>${user.created_at}</td>
                    <td>
                        <button class="btn-edit" onclick="editUser(${user.id}, '${user.name.replace(/'/g, "\\'")}', '${user.email}')">✏️ แก้ไข</button>
                        <button class="btn-delete" onclick="deleteUser(${user.id})">🗑️ ลบ</button>
                    </td>
                `;
                tbody.appendChild(row);
            });
            
            // อัพเดทจำนวนผู้ใช้
            document.querySelector('.stat-number').textContent = data.data.length;
        }
    } catch (error) {
        console.error('Error loading users:', error);
    }
}

// ฟังก์ชันค้นหา
function searchTable() {
    const input = document.getElementById('searchInput');
    const filter = input.value.toLowerCase();
    const table = document.getElementById('userTable');
    const tbody = table.getElementsByTagName('tbody')[0];
    const rows = tbody.getElementsByTagName('tr');
    const noResults = document.getElementById('noResults');
    let visibleCount = 0;
    
    for (let i = 0; i < rows.length; i++) {
        const nameCell = rows[i].getElementsByClassName('user-name')[0];
        const emailCell = rows[i].getElementsByClassName('user-email')[0];
        
        if (nameCell && emailCell) {
            const nameText = nameCell.textContent || nameCell.innerText;
            const emailText = emailCell.textContent || emailCell.innerText;
            
            if (nameText.toLowerCase().indexOf(filter) > -1 || 
                emailText.toLowerCase().indexOf(filter) > -1) {
                rows[i].classList.remove('hidden');
                visibleCount++;
            } else {
                rows[i].classList.add('hidden');
            }
        }
    }
    
    // แสดง/ซ่อนข้อความ "ไม่พบข้อมูล"
    if (visibleCount === 0 && filter !== '') {
        table.style.display = 'none';
        noResults.style.display = 'block';
    } else {
        table.style.display = 'table';
        noResults.style.display = 'none';
    }
}

// Event listener สำหรับช่องค้นหา
document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        searchInput.addEventListener('keyup', searchTable);
    }
});

// ฟังก์ชันเรียงลำดับตาราง
let sortDirection = {};

function sortTable(columnIndex) {
    const table = document.getElementById('userTable');
    const tbody = table.getElementsByTagName('tbody')[0];
    const rows = Array.from(tbody.getElementsByTagName('tr'));
    
    // กำหนดทิศทางการเรียง
    if (!sortDirection[columnIndex]) {
        sortDirection[columnIndex] = 'asc';
    } else {
        sortDirection[columnIndex] = sortDirection[columnIndex] === 'asc' ? 'desc' : 'asc';
    }
    
    const direction = sortDirection[columnIndex];
    
    // เรียงลำดับ
    rows.sort((a, b) => {
        const aValue = a.getElementsByTagName('td')[columnIndex].textContent.trim();
        const bValue = b.getElementsByTagName('td')[columnIndex].textContent.trim();
        
        // ถ้าเป็นตัวเลข
        if (!isNaN(aValue) && !isNaN(bValue)) {
            return direction === 'asc' ? aValue - bValue : bValue - aValue;
        }
        
        // ถ้าเป็นข้อความ
        if (direction === 'asc') {
            return aValue.localeCompare(bValue, 'th');
        } else {
            return bValue.localeCompare(aValue, 'th');
        }
    });
    
    // ลบ class sorted ทั้งหมด
    const headers = table.getElementsByTagName('th');
    for (let i = 0; i < headers.length; i++) {
        headers[i].classList.remove('sorted-asc', 'sorted-desc');
    }
    
    // เพิ่ม class sorted ให้คอลัมน์ที่เลือก
    headers[columnIndex].classList.add(direction === 'asc' ? 'sorted-asc' : 'sorted-desc');
    
    // เรียงแถวใหม่
    rows.forEach(row => tbody.appendChild(row));
}

// ฟังก์ชัน Export เป็น CSV
function exportToCSV() {
    const table = document.getElementById('userTable');
    const rows = table.querySelectorAll('tr:not(.hidden)');
    let csv = [];
    
    for (let i = 0; i < rows.length; i++) {
        const row = [];
        const cols = rows[i].querySelectorAll('td, th');
        
        for (let j = 0; j < cols.length - 1; j++) { // -1 เพื่อไม่เอาคอลัมน์ "จัดการ"
            let data = cols[j].innerText.replace(/(\r\n|\n|\r)/gm, '').replace(/(\s\s)/gm, ' ');
            data = data.replace(/"/g, '""');
            row.push('"' + data + '"');
        }
        csv.push(row.join(','));
    }
    
    // สร้างไฟล์และดาวน์โหลด
    const csvContent = '\uFEFF' + csv.join('\n'); // \uFEFF สำหรับ UTF-8 BOM
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    
    link.setAttribute('href', url);
    link.setAttribute('download', 'users_' + new Date().getTime() + '.csv');
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

// ฟังก์ชัน Export เป็น Excel (HTML Table)
function exportToExcel() {
    const table = document.getElementById('userTable').cloneNode(true);
    
    // ลบคอลัมน์ "จัดการ"
    const rows = table.querySelectorAll('tr');
    rows.forEach(row => {
        const lastCell = row.querySelector('th:last-child, td:last-child');
        if (lastCell) lastCell.remove();
    });
    
    // ลบแถวที่ซ่อน
    const hiddenRows = table.querySelectorAll('tr.hidden');
    hiddenRows.forEach(row => row.remove());
    
    const html = table.outerHTML;
    const blob = new Blob(['\uFEFF' + html], {
        type: 'application/vnd.ms-excel;charset=utf-8;'
    });
    
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    
    link.setAttribute('href', url);
    link.setAttribute('download', 'users_' + new Date().getTime() + '.xls');
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

// ฟังก์ชันแก้ไขผู้ใช้
function editUser(id, name, email) {
    document.getElementById('userId').value = id;
    document.getElementById('name').value = name;
    document.getElementById('email').value = email;
    document.getElementById('formTitle').textContent = '✏️ แก้ไขข้อมูลผู้ใช้';
    document.getElementById('submitBtn').textContent = 'บันทึกการแก้ไข';
    document.getElementById('cancelBtn').style.display = 'inline-block';
    
    // เลื่อนไปที่ฟอร์ม
    document.getElementById('userForm').scrollIntoView({ behavior: 'smooth' });
}

// ฟังก์ชันลบผู้ใช้
async function deleteUser(id) {
    if (!confirm('คุณแน่ใจหรือไม่ที่จะลบผู้ใช้นี้?')) {
        return;
    }
    
    const messageDiv = document.getElementById('message');
    
    try {
        const response = await fetch(`/api/users/${id}`, {
            method: 'DELETE'
        });
        
        const data = await response.json();
        
        if (response.ok) {
            messageDiv.className = 'success';
            messageDiv.textContent = '✓ ลบผู้ใช้สำเร็จ!';
            messageDiv.style.display = 'block';
            
            // โหลดข้อมูลใหม่
            await loadUsers();
            
            setTimeout(() => {
                messageDiv.style.display = 'none';
            }, 3000);
        } else {
            messageDiv.className = 'error';
            messageDiv.textContent = '✗ เกิดข้อผิดพลาด: ' + data.message;
            messageDiv.style.display = 'block';
        }
    } catch (error) {
        messageDiv.className = 'error';
        messageDiv.textContent = '✗ เกิดข้อผิดพลาดในการเชื่อมต่อ';
        messageDiv.style.display = 'block';
    }
}

// ฟังก์ชันยกเลิกการแก้ไข
function cancelEdit() {
    document.getElementById('userId').value = '';
    document.getElementById('userForm').reset();
    document.getElementById('formTitle').textContent = '➕ เพิ่มผู้ใช้ใหม่';
    document.getElementById('submitBtn').textContent = 'เพิ่มผู้ใช้';
    document.getElementById('cancelBtn').style.display = 'none';
}

// Event listener สำหรับปุ่มยกเลิก
document.getElementById('cancelBtn').addEventListener('click', cancelEdit);

// Event listener สำหรับฟอร์ม
document.getElementById('userForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const userId = document.getElementById('userId').value;
    const name = document.getElementById('name').value;
    const email = document.getElementById('email').value;
    const messageDiv = document.getElementById('message');
    const submitBtn = document.getElementById('submitBtn');
    
    const isEdit = userId !== '';
    const url = isEdit ? `/api/users/${userId}` : '/api/users/add';
    const method = isEdit ? 'PUT' : 'POST';
    
    // ปิดปุ่มชั่วคราว
    submitBtn.disabled = true;
    submitBtn.textContent = isEdit ? 'กำลังบันทึก...' : 'กำลังเพิ่ม...';
    
    try {
        const response = await fetch(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ name, email })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            messageDiv.className = 'success';
            messageDiv.textContent = isEdit ? '✓ แก้ไขข้อมูลสำเร็จ!' : '✓ เพิ่มผู้ใช้สำเร็จ!';
            messageDiv.style.display = 'block';
            
            // รีเซ็ตฟอร์ม
            cancelEdit();
            
            // โหลดข้อมูลใหม่ทันที
            await loadUsers();
            
            // ซ่อนข้อความหลังจาก 3 วินาที
            setTimeout(() => {
                messageDiv.style.display = 'none';
            }, 3000);
        } else {
            messageDiv.className = 'error';
            messageDiv.textContent = '✗ เกิดข้อผิดพลาด: ' + data.message;
            messageDiv.style.display = 'block';
        }
    } catch (error) {
        messageDiv.className = 'error';
        messageDiv.textContent = '✗ เกิดข้อผิดพลาดในการเชื่อมต่อ';
        messageDiv.style.display = 'block';
    } finally {
        // เปิดปุ่มอีกครั้ง
        submitBtn.disabled = false;
        submitBtn.textContent = isEdit ? 'บันทึกการแก้ไข' : 'เพิ่มผู้ใช้';
    }
});
