document.getElementById('addUserForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const name = document.getElementById('name').value;
    const email = document.getElementById('email').value;
    const messageDiv = document.getElementById('message');
    
    try {
        const response = await fetch('/api/users/add', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ name, email })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            messageDiv.className = 'success';
            messageDiv.textContent = '✓ เพิ่มผู้ใช้สำเร็จ!';
            document.getElementById('addUserForm').reset();
            
            // รีโหลดหน้าหลังจาก 1 วินาที
            setTimeout(() => {
                location.reload();
            }, 1000);
        } else {
            messageDiv.className = 'error';
            messageDiv.textContent = '✗ เกิดข้อผิดพลาด: ' + data.message;
        }
    } catch (error) {
        messageDiv.className = 'error';
        messageDiv.textContent = '✗ เกิดข้อผิดพลาดในการเชื่อมต่อ';
    }
});
