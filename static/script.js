document
    .getElementById("roll-form")
    .addEventListener("submit", function (event) {
        event.preventDefault();

        const dice = document.getElementById("dice");

        dice.classList.add("rolling");

        setTimeout(() => {
            this.submit();
        }, 500);
    });
