document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('registration-form');
    const fieldsContainer = document.getElementById('dynamic-fields-container');
    const submitBtn = document.getElementById('submit-btn');
    const btnText = document.getElementById('btn-text');
    const btnIcon = document.getElementById('btn-icon');
    const formMessage = document.getElementById('form-message');
    const usersTableBody = document.getElementById('users-table-body');
    
    let formSchema = [];

    // ==========================================================================
    // REGLAS DE VALIDACIÓN EN CLIENTE (ESTRATEGIA)
    // ==========================================================================
    const clientValidators = {
        name: (value) => {
            const val = value.trim();
            if (val.length < 2) return "El nombre debe tener al menos 2 caracteres.";
            if (!/^[A-Za-zÁÉÍÓÚáéíóúÑñ\s]+$/.test(val)) return "El nombre solo puede contener letras y espacios.";
            return "";
        },
        last_name: (value) => {
            const val = value.trim();
            if (val.length < 2) return "El apellido debe tener al menos 2 caracteres.";
            if (!/^[A-Za-zÁÉÍÓÚáéíóúÑñ\s]+$/.test(val)) return "El apellido solo puede contener letras y espacios.";
            return "";
        },
        age: (value) => {
            const val = parseInt(value, 10);
            if (isNaN(val) || val < 0 || val > 120) return "La edad debe ser un número entero entre 0 y 120.";
            return "";
        },
        email: (value) => {
            const val = value.trim();
            const emailRegex = /^[\w\.-]+@[\w\.-]+\.\w+$/;
            if (!emailRegex.test(val)) return "El formato del correo electrónico no es válido.";
            return "";
        },
        password: (value) => {
            if (value.length < 8) return "La contraseña debe tener al menos 8 caracteres.";
            if (!/\d/.test(value)) return "La contraseña debe contener al menos un número.";
            if (!/[A-Z]/.test(value)) return "La contraseña debe contener al menos una letra mayúscula.";
            if (!/[a-z]/.test(value)) return "La contraseña debe contener al menos una letra minúscula.";
            return "";
        },
        // Validador por defecto para cualquier campo dinámico adicional
        default: (value, fieldSchema) => {
            const val = value.trim();
            if (fieldSchema.required && !val) {
                return `El campo '${fieldSchema.label}' es obligatorio.`;
            }
            // Si el campo tiene tipo 'tel' (teléfono), aplicamos una validación estándar
            if (fieldSchema.field_type === 'tel' && val) {
                if (!/^\+?[\d\s-]{8,15}$/.test(val)) {
                    return "El teléfono debe tener entre 8 y 15 dígitos.";
                }
            }
            return "";
        }
    };

    // Inicialización de la aplicación
    init();

    async function init() {
        await loadFormSchema();
        loadUsersTable();
        
        // Mostrar alerta de verificación si viene desde el servidor
        if (window.verificationAlert) {
            showBanner(window.verificationAlert.message, window.verificationAlert.status);
            // Limpiar la alerta para evitar repetir el mensaje al recargar
            window.verificationAlert = null;
        }
    }

    // ==========================================================================
    // CARGAR ESQUEMA Y RENDERIZAR FORMULARIO
    // ==========================================================================
    async function loadFormSchema() {
        try {
            const response = await fetch('/api/schema');
            if (!response.ok) throw new Error('No se pudo obtener el esquema del formulario.');
            
            formSchema = await response.json();
            renderForm(formSchema);
        } catch (error) {
            console.error('Error al cargar esquema:', error);
            showBanner('Error al conectar con el servidor para cargar el formulario.', 'error');
        }
    }

    function renderForm(fields) {
        fieldsContainer.innerHTML = '';
        
        fields.forEach(field => {
            const group = document.createElement('div');
            group.className = 'input-group';
            group.id = `group-${field.name}`;
            
            // Placeholder amigable
            let placeholder = `Ingresa tu ${field.label.toLowerCase()}`;
            if (field.field_type === 'password') placeholder = '••••••••';
            if (field.field_type === 'email') placeholder = 'ejemplo@correo.com';
            
            group.innerHTML = `
                <label class="input-label" for="input-${field.name}">
                    <span>${field.label}</span>
                    ${field.required ? '<span class="req">*</span>' : ''}
                </label>
                <div class="input-wrapper">
                    <input 
                        type="${field.field_type}" 
                        id="input-${field.name}" 
                        name="${field.name}" 
                        class="form-input" 
                        placeholder="${placeholder}"
                        ${field.required ? 'required' : ''}
                    >
                    <i class="validation-icon fa-solid"></i>
                </div>
                <div class="error-msg" id="error-${field.name}">Mensaje de error</div>
            `;
            
            fieldsContainer.appendChild(group);
            
            // Agregar event listeners para validación en tiempo real
            const inputEl = group.querySelector('.form-input');
            inputEl.addEventListener('input', () => validateInput(inputEl, field));
            inputEl.addEventListener('blur', () => validateInput(inputEl, field));
        });
    }

    // Validar un campo individualmente
    function validateInput(inputEl, fieldSchema) {
        const value = inputEl.value;
        const validator = clientValidators[fieldSchema.name] || clientValidators.default;
        
        // Obtener el mensaje de error (vacío si es válido)
        const errorMsg = validator(value, fieldSchema);
        const errorDiv = document.getElementById(`error-${fieldSchema.name}`);
        const iconEl = inputEl.nextElementSibling;

        if (errorMsg) {
            inputEl.classList.remove('valid');
            inputEl.classList.add('invalid');
            errorDiv.textContent = errorMsg;
            errorDiv.classList.add('visible');
            
            iconEl.className = 'validation-icon fa-solid fa-circle-xmark';
            return false;
        } else {
            // No validar visualmente si está vacío y no es obligatorio
            if (!fieldSchema.required && !value.trim()) {
                inputEl.classList.remove('valid', 'invalid');
                errorDiv.classList.remove('visible');
                iconEl.className = 'validation-icon fa-solid';
                return true;
            }
            
            inputEl.classList.remove('invalid');
            inputEl.classList.add('valid');
            errorDiv.classList.remove('visible');
            errorDiv.textContent = '';
            
            iconEl.className = 'validation-icon fa-solid fa-circle-check';
            return true;
        }
    }

    // ==========================================================================
    // ENVIAR FORMULARIO (AJAX / FETCH)
    // ==========================================================================
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        // Ocultar banners anteriores
        hideBanner();

        // 1. Validar todos los campos antes de enviar
        let isFormValid = true;
        let firstInvalidElement = null;

        formSchema.forEach(field => {
            const inputEl = document.getElementById(`input-${field.name}`);
            const isValid = validateInput(inputEl, field);
            if (!isValid) {
                isFormValid = false;
                if (!firstInvalidElement) firstInvalidElement = inputEl;
            }
        });

        if (!isFormValid) {
            if (firstInvalidElement) firstInvalidElement.focus();
            showBanner('Por favor, corrige los errores en el formulario.', 'error');
            return;
        }

        // 2. Reunir los datos del formulario
        const formData = {};
        formSchema.forEach(field => {
            const inputEl = document.getElementById(`input-${field.name}`);
            formData[field.name] = inputEl.value;
        });

        // 3. Enviar datos al Servidor (API)
        setLoadingState(true);
        try {
            const response = await fetch('/api/register', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(formData)
            });

            const result = await response.json();

            if (response.ok && result.success) {
                showBanner(result.message, 'success');
                form.reset();
                
                // Limpiar estados visuales de los inputs
                formSchema.forEach(field => {
                    const inputEl = document.getElementById(`input-${field.name}`);
                    inputEl.classList.remove('valid', 'invalid');
                    const iconEl = inputEl.nextElementSibling;
                    iconEl.className = 'validation-icon fa-solid';
                });
                
                // Recargar tabla de usuarios
                loadUsersTable();
            } else {
                // Manejar errores de servidor (generales o específicos)
                showBanner(result.message || 'Error al registrar el usuario.', 'error');
                
                if (result.errors) {
                    // Si el servidor devolvió errores específicos por campo, los marcamos en la UI
                    Object.keys(result.errors).forEach(fieldName => {
                        const inputEl = document.getElementById(`input-${fieldName}`);
                        if (inputEl) {
                            inputEl.classList.remove('valid');
                            inputEl.classList.add('invalid');
                            const errorDiv = document.getElementById(`error-${fieldName}`);
                            errorDiv.textContent = result.errors[fieldName];
                            errorDiv.classList.add('visible');
                            const iconEl = inputEl.nextElementSibling;
                            iconEl.className = 'validation-icon fa-solid fa-circle-xmark';
                        }
                    });
                }
            }
        } catch (error) {
            console.error('Error al enviar formulario:', error);
            showBanner('Error de red. No se pudo conectar con el backend.', 'error');
        } finally {
            setLoadingState(false);
        }
    });

    function setLoadingState(isLoading) {
        if (isLoading) {
            submitBtn.disabled = true;
            btnText.textContent = 'Procesando...';
            btnIcon.className = 'fa-solid fa-circle-notch fa-spin btn-spinner';
        } else {
            submitBtn.disabled = false;
            btnText.textContent = 'Registrar Usuario';
            btnIcon.className = 'fa-solid fa-arrow-right';
        }
    }

    // Banner de Notificaciones
    function showBanner(message, type) {
        formMessage.textContent = '';
        formMessage.className = `form-message-banner ${type}`;
        
        const icon = document.createElement('i');
        if (type === 'success') {
            icon.className = 'fa-solid fa-circle-check';
        } else {
            icon.className = 'fa-solid fa-circle-exclamation';
        }
        
        formMessage.appendChild(icon);
        formMessage.appendChild(document.createTextNode(` ${message}`));
        formMessage.classList.remove('hidden');
        
        // Auto ocultar después de 6 segundos si es éxito
        if (type === 'success') {
            setTimeout(() => {
                hideBanner();
            }, 6000);
        }
    }

    function hideBanner() {
        formMessage.classList.add('hidden');
        formMessage.className = 'form-message-banner hidden';
    }

    // ==========================================================================
    // CARGAR Y RENDERIZAR TABLA DE USUARIOS (POSTGRESQL)
    // ==========================================================================
    async function loadUsersTable() {
        try {
            const response = await fetch('/api/users');
            if (!response.ok) throw new Error('No se pudieron obtener los usuarios.');
            
            const users = await response.json();
            renderUsersTable(users);
        } catch (error) {
            console.error('Error al cargar tabla de usuarios:', error);
            usersTableBody.innerHTML = `
                <tr class="empty-state">
                    <td colspan="7" style="color: var(--error-color)">
                        <i class="fa-solid fa-triangle-exclamation"></i> Error al conectar con PostgreSQL
                    </td>
                </tr>
            `;
        }
    }

    function renderUsersTable(users) {
        usersTableBody.innerHTML = '';
        
        if (users.length === 0) {
            usersTableBody.innerHTML = `
                <tr class="empty-state">
                    <td colspan="7">
                        <div class="empty-message">
                            <i class="fa-solid fa-folder-open"></i>
                            <span>No hay usuarios registrados aún.</span>
                        </div>
                    </td>
                </tr>
            `;
            return;
        }

        users.forEach(user => {
            const tr = document.createElement('tr');
            
            // Construir los badges para los datos adicionales (JSONB)
            let extraDataHtml = '';
            const extraKeys = Object.keys(user.extra_data || {});
            
            if (extraKeys.length > 0) {
                extraDataHtml = '<div class="json-badge-container">';
                extraKeys.forEach(key => {
                    extraDataHtml += `
                        <span class="json-badge" title="${key}: ${user.extra_data[key]}">
                            <i class="fa-solid fa-cube"></i> ${key}: ${user.extra_data[key]}
                        </span>
                    `;
                });
                extraDataHtml += '</div>';
            } else {
                extraDataHtml = '<span class="json-badge empty">Ninguno</span>';
            }

            // Construir el badge de estado de verificación
            const statusHtml = user.is_verified 
                ? `<span class="status-badge verified"><i class="fa-solid fa-circle-check"></i> Verificado</span>`
                : `<span class="status-badge pending"><i class="fa-solid fa-clock"></i> Pendiente</span>`;

            tr.innerHTML = `
                <td><span class="user-id-badge">${user.id}</span></td>
                <td style="font-weight: 500; color: var(--text-primary);">${user.name} ${user.last_name}</td>
                <td>${user.age}</td>
                <td>${user.email}</td>
                <td>${statusHtml}</td>
                <td>${extraDataHtml}</td>
                <td style="font-size: 0.8rem; white-space: nowrap;">${user.created_at}</td>
            `;
            
            usersTableBody.appendChild(tr);
        });
    }
});
