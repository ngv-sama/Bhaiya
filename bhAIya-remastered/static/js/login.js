document.addEventListener('DOMContentLoaded', function() {
    const userToggleButton = document.querySelectorAll('.toggle-button')[0];
    const adminToggleButton = document.querySelectorAll('.toggle-button')[1];
    const loginForm = document.querySelector('.login-form');
    const inputGroups = document.querySelectorAll('.input-group');
    const userTypeInput = document.querySelector('input[name="user_type"]');

    userToggleButton.addEventListener('click', function() {
        setActiveToggle(userToggleButton, adminToggleButton, 'user');
    });

    adminToggleButton.addEventListener('click', function() {
        setActiveToggle(adminToggleButton, userToggleButton, 'admin');
    });

    function setActiveToggle(activeButton, inactiveButton, role) {
        activeButton.classList.add('active');
        inactiveButton.classList.remove('active');
        userTypeInput.value = role;
    }

    function checkFilled(input) {
        if (input.value.trim() !== "") {
            input.parentElement.classList.add("filled");
        } else {
            input.parentElement.classList.remove("filled");
        }
    }

    inputGroups.forEach(group => {
        const input = group.querySelector('.input-bubble');
        input.addEventListener('input', function() {
            checkFilled(this);
        });

        input.addEventListener('focus', function() {
            group.classList.add('active');
        });

        input.addEventListener('blur', function() {
            group.classList.remove('active');
            checkFilled(this);
        });
    });
});