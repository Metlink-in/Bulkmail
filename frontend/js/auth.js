document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('loginForm');
    const registerForm = document.getElementById('registerForm');
    const errorMsg = document.getElementById('errorMsg');

    function showError(msg) {
        if (!errorMsg) return;
        errorMsg.textContent = msg;
        errorMsg.style.display = 'block';
        
        errorMsg.animate([
            { transform: 'translateX(0)' },
            { transform: 'translateX(-5px)' },
            { transform: 'translateX(5px)' },
            { transform: 'translateX(-5px)' },
            { transform: 'translateX(5px)' },
            { transform: 'translateX(0)' }
        ], { duration: 400, iterations: 1 });
    }

    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const btn = loginForm.querySelector('button[type="submit"]');
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            
            btn.disabled = true;
            btn.innerHTML = '<span class="spinner spinner-sm"></span> Loading...';
            errorMsg.style.display = 'none';

            try {
                const data = await api.post('/auth/login', { email, password });
                api.setTokens(data.access_token, data.refresh_token);
                if (api.getUserRole() === 'admin') {
                    window.location.href = '/admin.html';
                } else {
                    window.location.href = '/dashboard.html';
                }
            } catch (err) {
                showError(err.message || 'Login failed. Please check your credentials.');
                btn.disabled = false;
                btn.innerHTML = 'Sign In';
            }
        });
    }

    if (registerForm) {
        const passInput = document.getElementById('password');
        const passConfirm = document.getElementById('passwordConfirm');
        const strengthInd = document.getElementById('passwordStrength');
        
        if (passInput) {
            passInput.addEventListener('input', (e) => {
                const v = e.target.value;
                let strength = "weak";
                let color = "var(--danger)";
                if (v.length > 7 && /[A-Z]/.test(v) && /[0-9]/.test(v)) { strength = "strong"; color = "var(--success)"; }
                else if (v.length > 5) { strength = "medium"; color = "var(--warning)"; }
                
                if(strengthInd) {
                    strengthInd.textContent = `Strength: ${strength}`;
                    strengthInd.style.color = color;
                }
            });
        }

        registerForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const btn = registerForm.querySelector('button[type="submit"]');
            const name = document.getElementById('name').value;
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            const org_name = document.getElementById('org_name').value || '';
            
            if (password !== passConfirm.value) {
                showError("Passwords do not match");
                return;
            }

            btn.disabled = true;
            btn.innerHTML = '<span class="spinner spinner-sm"></span> Creating...';
            errorMsg.style.display = 'none';

            try {
                const data = await api.post('/auth/register', { name, email, password, org_name });
                api.setTokens(data.access_token, data.refresh_token);
                window.location.href = '/dashboard.html';
            } catch (err) {
                showError(err.message || 'Registration failed.');
                btn.disabled = false;
                btn.innerHTML = 'Create Account';
            }
        });
    }

    document.querySelectorAll('.toggle-password').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const input = e.target.closest('.input-group').querySelector('input');
            if (input.type === 'password') {
                input.type = 'text';
                e.target.textContent = 'Hide';
            } else {
                input.type = 'password';
                e.target.textContent = 'Show';
            }
        });
    });
});
