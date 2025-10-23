// ===============================
// login.js - Gestion du formulaire
// ===============================

function showMessage(message, type = 'success') {
    const messageContainer = document.getElementById('message-container');
    const messageElement = document.getElementById('message');

    messageContainer.style.display = 'none';
    messageElement.className = `alert alert-${type === 'success' ? 'success' : 'danger'}`;
    messageElement.innerHTML = `
        <div class="d-flex align-items-center">
            <i class="fas fa-${type === 'success' ? 'check-circle' : 'exclamation-triangle'} me-2"></i>
            <span>${message}</span>
        </div>
    `;
    messageContainer.style.display = 'block';

    if (type === 'success') {
        setTimeout(() => { messageContainer.style.display = 'none'; }, 5000);
    }
}

function showNotification(type, message, title = "") {
    if (window.AppUtils && window.AppUtils.showNotification) {
        AppUtils.showNotification(type, message, title);
    } else {
        $.notify(
            { title, message, icon: type === "success" ? "fa fa-check-circle" : "fa fa-exclamation-circle" },
            { type, placement: { from: "top", align: "right" }, delay: 3000, timer: 500 }
        );
    }
}

function setLoadingState(isLoading) {
    const submitBtn = document.getElementById('submit');
    if (isLoading) {
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Connexion en cours...';
        submitBtn.disabled = true;
    } else {
        submitBtn.innerHTML = 'Se connecter';
        submitBtn.disabled = false;
    }
}

// ----------------------
// Formulaire login
// ----------------------
document.getElementById("login").addEventListener("submit", function (e) {
    e.preventDefault();

    const username = e.target.username.value.trim();
    const password = e.target.password.value;

    if (!username || !password) {
        showMessage('Veuillez remplir tous les champs', 'error');
        return;
    }

    setLoadingState(true);
    document.getElementById('message-container').style.display = 'none';

    // Utilisation de CONFIG pour les URLs
    axios.post(CONFIG.BASE_URL + CONFIG.ENDPOINTS.AUTH.LOGIN, { username, password })
        .then(res => {
            const token = res.data.key;
            localStorage.setItem('token', token);

            return axios.get(CONFIG.BASE_URL + CONFIG.ENDPOINTS.AUTH.USER_INFO, {
                headers: { Authorization: `Token ${token}` }
            });
        })
        .then(userRes => {
            const userData = userRes.data;
            localStorage.setItem('user', JSON.stringify(userData));

            const role = userData.role;
            let redirectUrl = '/pages/student/classe.html';
            if (role === 'teacher') redirectUrl = '/pages/teacher/classes.html';
            if (role === 'admin') redirectUrl = '/pages/administration/classes.html';

            showNotification('success', `Redirection vers l'espace ${role}...`, 'Connexion réussie');

            setTimeout(() => { window.location.href = redirectUrl; }, 1500);
        })
        .catch(error => {
            console.error('Erreur de connexion:', error);
            setLoadingState(false);

            let errorMessage = 'Une erreur est survenue lors de la connexion';
            if (error.response) {
                const status = error.response.status;
                const data = error.response.data;

                if (status === 400) {
                    errorMessage = data.non_field_errors?.[0] || data.username?.[0] || data.password?.[0] || 'Identifiants invalides';
                } else if (status === 401) errorMessage = "Nom d'utilisateur ou mot de passe incorrect";
                else if (status === 403) errorMessage = "Accès refusé. Votre compte pourrait être désactivé.";
                else if (status === 500) errorMessage = "Erreur serveur. Veuillez réessayer plus tard.";
            } else if (error.request) {
                errorMessage = 'Impossible de se connecter au serveur. Vérifiez votre connexion internet.';
            } else {
                errorMessage = error.message || 'Une erreur inattendue s\'est produite';
            }

            showNotification('danger', errorMessage, 'Échec de la connexion');
        });
});

// Masquer messages à la saisie
document.querySelectorAll('#login input').forEach(input => {
    input.addEventListener('input', () => {
        document.getElementById('message-container').style.display = 'none';
    });
});
